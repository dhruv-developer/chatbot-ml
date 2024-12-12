from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os

# Load inventory data
try:
    with open("./inventory_data.json", "r") as f:
        inventory_data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("The inventory data file 'inventory_data.json' is missing.")

# Initialize FastAPI app
app = FastAPI()

# Securely load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request model for input
class CaseRequest(BaseModel):
    item_id: str

# Helper function to find entry by item_id
def find_entry_by_item_id(item_id: str) -> Optional[dict]:
    for entry in inventory_data:
        if entry.get("item_id") == item_id:
            return entry
    return None

# FastAPI route to handle case solving
@app.post("/solve_case")
async def solve_case(case_request: CaseRequest):
    item_id = case_request.item_id
    entry = find_entry_by_item_id(item_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Item ID not found.")

    # Calculate expected delivery date
    try:
        order_date = datetime.strptime(entry["order_date"], "%Y-%m-%d")
        estimated_days = entry.get("estimated_days_promised", 0)
        buffer_days = entry.get("buffer_days_given", 0)
        expected_delivery_date = order_date + timedelta(days=estimated_days + buffer_days)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing order dates: {str(e)}")

    current_date = datetime.now()

    if current_date < expected_delivery_date:
        return f"The order with ID {item_id} should be delivered soon."

    # If delayed, determine fault using OpenAI
    delay_days = (current_date - expected_delivery_date).days

    external_factors = entry.get("external_factor_encitation", "None provided")
    vendor_name = entry.get("vendor", {}).get("name", "Unknown")
    distance = entry.get("distance", "Unknown")
    priority = entry.get("priority", "Unknown")
    stock_before_order = entry.get("stock_before_order", "Unknown")
    current_inventory = entry.get("current_inventory", "Unknown")
    quantity = entry.get("quantity", "Unknown")

    # Construct prompt for OpenAI
    prompt = (
        f"The delivery of an order by {vendor_name} is delayed by {delay_days} days. Here are the details:\n"
        f"Item Name: {entry.get('item_name', 'Unknown')}\n"
        f"Quantity: {quantity}\n"
        f"External Factors: {external_factors}\n"
        f"Distance: {distance} km\n"
        f"Priority: {priority}\n"
        f"Stock Before Order: {stock_before_order} units\n"
        f"Current Inventory: {current_inventory} units\n"
        "Based on these details, determine if the vendor is at fault or if they can be exempted. "
        "Do not give mixed or confusing answers. The vendor is either at fault or not. "
        "Consider that priority is for hospital medicines, and a delay of more than three days past the buffer time is unacceptable."
    )

    # OpenAI API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert case solver for dispute settlements. Ensure fairness in analysis. Provide concise answers, but elaborate if requested."},
                {"role": "user", "content": prompt}
            ]
        )
        decision = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with OpenAI API: {str(e)}")

    return f"Decision on the order with ID {item_id}: {decision}"
