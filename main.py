import requests
import pandas as pd
import time

MARKET_URL = "https://api.warframe.market/v1"
TIME_TO_WAIT = 0.1 # if lower, gets 429 (too many requests) http error code

def get_items_list(filters=["prime set"]):
    """Get all item info

    Args:
        filters (list, optional): Finding only item names containing one of the filters. Defaults to ["prime set"].

    Returns:
        pd.DataFrame: DataFrame containing all item info, columns: thumb, url_name, item_name, id, vaulted
    """
    response = requests.get(f"{MARKET_URL}/items")

    if response.status_code != requests.codes.OK:
        print("Error getting the items")
        return
    
    df = pd.DataFrame(response.json()["payload"]["items"])

    df.attrs["filters"] = filters
    return df[df["item_name"].str.contains('|'.join(filters), case=False)]


def get_item_price(item_url:str):
    item_url = item_url.lower()
    if " " in item_url:
        item_url = item_url.replace(" ", "_")  # Replace spaces with underscores in the URL
    response = requests.get(f"{MARKET_URL}/items/{item_url}/orders")
    if response.status_code != requests.codes.OK:
        print(f"Error getting the item price {item_url}, {response.status_code}")
        return
    
    df = pd.DataFrame(pd.json_normalize(response.json()["payload"]["orders"], sep="_"))
    df = df[df["user_status"].str.contains("ingame", case=False)]
    df = df[df["visible"]]
    min_sell = df[df["order_type"].str.contains("sell", case=False)]["platinum"].min()
    
    max_buy = df[df["order_type"].str.contains("buy", case=False)]["platinum"].max()
    if max_buy is None:
        max_buy = 0
    return {"item_url":item_url ,"min_sell":int(min_sell),"max_buy":int(max_buy)}


def get_set_info(set_url):
    set_url = set_url.lower()  # Convert to lowercase to match the API URL format (all lowercase)
    if " " in set_url:
        set_url = set_url.replace(" ", "_")  # Replace spaces with underscores in the URL
    response = requests.get(f"{MARKET_URL}/items/{set_url}")
    if response.status_code != requests.codes.OK:
        print(f"Error getting the item set {set_url}, {response.status_code}")
        return
    set_price = get_item_price(set_url)

    df = pd.DataFrame(columns=["item_url", "min_sell", "max_buy"])
    jitems_in_set = response.json()["payload"]["item"]["items_in_set"]
    for item in jitems_in_set:
        time.sleep(0.1)
        if item["url_name"] == set_url:
            continue
        item_info = get_item_price(item["url_name"])
        for i in range(item["quantity_for_set"]):
            df = pd.concat([df, pd.DataFrame(item_info, index=[0])], ignore_index=True)

    return {
        "set_url": set_url,
        "set_max_buy": set_price["max_buy"],
        "set_min_sell": set_price["min_sell"],
        "items_max_buy_sum": df["max_buy"].sum(),
        "items_min_sell_sum": df["min_sell"].sum(),
        "number_of_items": len(jitems_in_set) - 1,
        "instant_profit": set_price["max_buy"] - df["min_sell"].sum(),
        "listed_profit": set_price["min_sell"] - df["min_sell"].sum(),
    }

def main():
    df = pd.DataFrame(columns=[
        "set_url",
        "set_max_buy",
        "set_min_sell",
        "items_max_buy_sum",
        "items_min_sell_sum",
        "number_of_items",
        "instant_profit",
        "listed_profit"])
    prime_sets = get_items_list()
    for item_set in prime_sets["url_name"]:
        time.sleep(0.1)
        try:
            df = pd.concat([df,pd.DataFrame(get_set_info(item_set), index=[1])], ignore_index=True)
        except Exception as e:
            print(f"Error processing item set {item_set}: {e}")
    
    df = df.sort_values(by='instant_profit', ascending=False)
    print(df[:10])
    df = df.sort_values(by='listed_profit', ascending=False)
    print(df[:10])

if __name__ == "__main__":
    main()
    