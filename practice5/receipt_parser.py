import re
import json
with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()
prices = re.findall(r"\d+\.\d{2}", text)

products = re.findall(r"([A-Za-z ]+)\s\d+\.\d{2}", text)

price_values = [float(p) for p in prices]

calculated_total = sum(price_values)

date_time_match = re.search(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}", text)

date_time = date_time_match.group() if date_time_match else None

payment_match = re.search(r"Payment Method:\s*(\w+)", text)

payment_method = payment_match.group(1) if payment_match else None

result = {
    "products": [p.strip() for p in products],
    "prices": price_values,
    "total_amount": calculated_total,
    "date_time": date_time,
    "payment_method": payment_method
}
print(json.dumps(result, indent=4))