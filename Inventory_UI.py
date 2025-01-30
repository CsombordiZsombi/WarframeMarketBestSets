import streamlit as st
import pandas as pd
import json
import requests
import time


MARKET_URL = "https://api.warframe.market/v1"

def load_inventory(file_path="inventory.json"):

    # Fájl beolvasása
    with open(file_path, "r") as file:
        return json.load(file)

def load_items(file_path="items.json"):
    with open(file_path, "r") as file:
        return json.load(file)["payload"]["items"]

def map_inventory_to_urls(inventory, items):
    item_url_map = {item["item_name"]: item["url_name"] for item in items}
    for entry in inventory:
        entry["url_name"] = item_url_map.get(entry["item_name"], None)
    return inventory

def fetch_market_orders(item_url_name):
    url = f"{MARKET_URL}/items/{item_url_name}/orders"
    time.sleep(0.1)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["payload"]["orders"]
    else:
        st.error(f"Failed to fetch orders for {item_url_name}")
        return []

def get_sell_value(orders):
    sell_prices = [order["platinum"] for order in orders 
                   if order["order_type"] == "sell" and order["user"]["status"] == "ingame"]
    return min(sell_prices) if sell_prices else 0

def get_buy_value(orders):
    buy_prices = [order["platinum"] for order in orders 
                  if order["order_type"] == "buy" and order["user"]["status"] == "ingame"]
    return max(buy_prices) if buy_prices else 0

def enrich_inventory_for_display(inventory):
    display_data = []
    for entry in inventory:
        sell_value = buy_value = None
        if entry.get("url_name"):
            orders = fetch_market_orders(entry["url_name"])
            sell_value = get_sell_value(orders)
            buy_value = get_buy_value(orders)

        display_data.append({
            "Item Name": entry["item_name"],
            "Quantity": entry["quantity"],
            "Sell": sell_value,
            "Buy": buy_value
        })
    return display_data

def main():
    st.title("Warframe Market Inventory Table")

    if "refresh_count" not in st.session_state:
        st.session_state["refresh_count"] = 0

    # Gomb az adatok újratöltéséhez
    if st.button("Refresh"):
        st.session_state["refresh_count"] += 1
    items_data = load_items()
    inventory_data = load_inventory()
    mapped_inventory = map_inventory_to_urls(inventory_data, items_data)
    display_inventory = enrich_inventory_for_display(mapped_inventory)

    df = pd.DataFrame(display_inventory)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()