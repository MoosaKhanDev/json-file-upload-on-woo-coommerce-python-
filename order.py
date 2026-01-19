import pandas as pd
import numpy as np
import json
import requests
from requests.auth import HTTPBasicAuth
import time

WC_URL = "https://nona.amazonbookhouse.com/wp-json/wc/v3/orders"
CONSUMER_KEY = "ck_a1f48ae3095f98cd20353d240d93f4e95900090a"
CONSUMER_SECRET = "cs_d2b6559f4914af8f32cde882760c23f54a6f35bb"

def clean_str(val):
    if pd.isna(val) or val is None:
        return ""
    return str(val)

df = pd.read_csv("woocommerce_orders.csv")

orders = []

for _, r in df.iterrows():
    line_total = r["subtotal"] if pd.notna(r["subtotal"]) else r["order_total"]
    shipping_total = r["shipping_total"] if pd.notna(r["shipping_total"]) else 0

    orders.append({
        "status": clean_str(r["status"]),
        "currency": clean_str(r["currency"]),
        "date_created": clean_str(r["date_created"]),
        "billing": {
            "first_name": clean_str(str(r["billing_name"]).split(" ")[0]) if pd.notna(r["billing_name"]) else "",
            "last_name": clean_str(" ".join(str(r["billing_name"]).split(" ")[1:])) if pd.notna(r["billing_name"]) else "",
            "email": clean_str(r["billing_email"]),
            "phone": clean_str(r["billing_phone"]),
            "address_1": clean_str(r["billing_address_1"]),
            "address_2": clean_str(r["billing_address_2"]),
            "city": clean_str(r["billing_city"]),
            "state": clean_str(r["billing_state"]),
            "postcode": clean_str(r["billing_postcode"]),
            "country": clean_str(r["billing_country"])
        },
        "line_items": [
            {
                "product_id": 123,  # Replace 123 with a valid WooCommerce product ID
                "quantity": 1,
                "subtotal": str(line_total),
                "total": str(line_total)
            }
        ],
        "shipping_lines": [
            {
                "method_id": "flat_rate",  # Replace with your actual shipping method ID
                "method_title": "Imported Shipping",
                "total": str(shipping_total)
            }
        ],
        "customer_note": clean_str(r["notes"])
    })

with open("woocommerce_orders_with_price.json", "w") as f:
    json.dump(orders, f, indent=2)

for i, order in enumerate(orders, 1):
    print(f"Uploading order {i}...")
    try:
        response = requests.post(
            WC_URL,
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            headers={"Content-Type": "application/json"},
            json=order,
            verify=True  # Change to False if SSL issues persist (not recommended)
        )
        if response.status_code == 201:
            print(f"Order {i} uploaded successfully: ID {response.json().get('id')}")
        else:
            print(f"Failed to upload order {i}. Status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for order {i}: {e}")
        time.sleep(5)
