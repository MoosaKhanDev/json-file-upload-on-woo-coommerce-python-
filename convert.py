import pandas as pd
import json

df = pd.read_csv("woocommerce_orders.csv")

orders = []

for _, r in df.iterrows():
    line_total = r["subtotal"] if pd.notna(r["subtotal"]) else r["order_total"]
    shipping_total = r["shipping_total"] if pd.notna(r["shipping_total"]) else 0

    orders.append({
        "status": r["status"],
        "currency": r["currency"],
        "date_created": r["date_created"],
        "billing": {
            "first_name": str(r["billing_name"]).split(" ")[0] if pd.notna(r["billing_name"]) else "",
            "last_name": " ".join(str(r["billing_name"]).split(" ")[1:]) if pd.notna(r["billing_name"]) else "",
            "email": r["billing_email"],
            "phone": r["billing_phone"],
            "address_1": r["billing_address_1"],
            "address_2": r["billing_address_2"],
            "city": r["billing_city"],
            "state": r["billing_state"],
            "postcode": r["billing_postcode"],
            "country": r["billing_country"]
        },
        "line_items": [
            {
                "name": "Imported Order Item",
                "quantity": 1,
                "subtotal": str(line_total),
                "total": str(line_total)
            }
        ],
        "shipping_lines": [
            {
                "method_title": "Imported Shipping",
                "total": str(shipping_total)
            }
        ],
        "customer_note": r["notes"]
    })

with open("woocommerce_orders_with_price.json", "w") as f:
    json.dump(orders, f, indent=2)

print("File generated successfully")
