import json
import random
from datetime import datetime, timedelta
import uuid

# Predefined data
items = ["Paracetamol", "Ibuprofen", "Amoxicillin"]
vendors = [
    {"name": "PharmaCorp", "details": "4 star", "unit_price": {"Paracetamol": 2.5, "Ibuprofen": 3.0, "Amoxicillin": 5.0}},
    {"name": "MediSupply", "details": "3 star", "unit_price": {"Paracetamol": 2.0, "Ibuprofen": 2.8, "Amoxicillin": 4.8}}
]
departments = ["Emergency", "Pediatrics", "Surgery"]
external_factors = [
    "Clear weather, Moderate traffic",
    "Rainy weather, Heavy traffic",
    "Sunny weather, Light traffic",
    "Foggy weather, Delayed traffic"
]

# Fixed distances for vendors
distances = {
    "PharmaCorp": 50,  # Distance in kilometers
    "MediSupply": 75
}

# Generate JSON data
def generate_data(n):
    data = []
    for _ in range(n):
        item = random.choice(items)
        vendor = random.choice(vendors)
        quantity = random.randint(20, 150)
        unit_price = vendor["unit_price"][item]
        total_price = quantity * unit_price
        department = random.choice(departments)
        stock_before_order = random.randint(200, 1000)
        current_inventory = random.randint(10, 80)
        priority = random.choice(["Yes", "No"])
        external_factor = random.choice(external_factors)

        # Random date after October 2024
        random_days = random.randint(1, 42)  # Up to 60 days after October 31, 2024
        order_date = (datetime(2024, 10, 31) + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        estimated_days = random.randint(7, 15)
        buffer_days = random.randint(2, 5)
        item_id = str(uuid.uuid4())  # Generate unique item ID
        distance = distances[vendor["name"]]

        entry = {
            "item_id": item_id,
            "item_name": item,
            "vendor": {
                "name": vendor["name"],
                "details": vendor["details"]
            },
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "hospital_department": department,
            "stock_before_order": stock_before_order,
            "current_inventory": current_inventory,
            "priority": priority,
            "external_factor_encitation": external_factor,
            "order_date": order_date,
            "estimated_days_promised": estimated_days,
            "buffer_days_given": buffer_days,
            "distance": distance
        }
        data.append(entry)

    return data

# Save to a JSON file
def save_to_json_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Generate and save the data
n = int(input("Enter the number of entries you need: "))
data = generate_data(n)
save_to_json_file(data, "inventory_data.json")

print(f"Generated {n} entries and saved to inventory_data.json")
