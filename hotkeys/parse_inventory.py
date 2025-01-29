import time
import easyocr
import numpy as np
import mss
import pandas as pd
from pynput.mouse import Controller
import winsound
import json
from rapidfuzz.distance import Levenshtein

SLOT_GRID = None
SLOT_SIZE = None
ITEM_LIST = None

BEEP = False

mouse = Controller()

def main(*args, **kvargs):
    start_time = time.time()
    print("Scanning inventory")

    df = predict_inventory()
    df.to_json("inventory.json", orient="records", indent=4)

    print(f"Done scanning inventory, took {round(time.time()-start_time,1)} seconds")
def predict_inventory():
    df = pd.DataFrame(columns=["item_name","quantity"])
    
    with open("Warframe_UI/items.json") as file:
        global ITEM_LIST
        item_list = json.load(file)["payload"]["items"]
        ITEM_LIST = [item["item_name"] for item in item_list]

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Az első monitor adatai
        width, height = monitor["width"], monitor["height"]
        global SLOT_GRID 
        global SLOT_SIZE
        SLOT_GRID = [
           [(width*0.041, height*0.186),(width*0.147, height*0.186), (width*0.259, height*0.186), (width*0.37, height*0.186), (width*0.48, height*0.186),(width*0.59, height*0.187)],
           [(width*0.041, height*0.373),(width*0.147, height*0.373), (width*0.259, height*0.373), (width*0.37, height*0.373), (width*0.48, height*0.373),(width*0.59, height*0.373)],
           [(width*0.041, height*0.556),(width*0.147, height*0.556), (width*0.259, height*0.556), (width*0.37, height*0.556), (width*0.48, height*0.556),(width*0.59, height*0.556)],
           [(width*0.041, height*0.744),(width*0.147, height*0.744), (width*0.259, height*0.744), (width*0.37, height*0.744), (width*0.48, height*0.744),(width*0.59, height*0.744)],
        ]
        SLOT_SIZE = (width*0.086, height*0.153)
        reader = easyocr.Reader(["en"], gpu=True)
        
        for row in SLOT_GRID: # we predict and store the first 4 rows.
            for slot in row:
                item = predict_item(slot, reader, sct)
                if item["item_name"] == "":
                    print("sor oszlop")
                    return df
                #if df["item_name"].str.contains(item["item_name"]).any():
                #    return df
                df = pd.concat([df, pd.DataFrame(item)])
        
        while True:
            mouse.scroll(0, -1) #scroll down
            time.sleep(0.5)
            for slot in SLOT_GRID[-1]:
                item = predict_item(slot, reader, sct)
                if item["item_name"] == "":
                    return df
                if df["item_name"].str.contains(item["item_name"]).any():
                    return df
                df = pd.concat([df, pd.DataFrame(item)])
    return df
def similar_item_name(word, max_distance=2):
    global ITEM_LIST
    for w in ITEM_LIST:
        if Levenshtein.distance(word, w) <= max_distance:
            return w
    return ""

def predict_item(slot, reader, sct):
    region = {
        "left":int(slot[0]),
        "top": int(slot[1]), 
        "width":int(SLOT_SIZE[0]),
        "height":int(SLOT_SIZE[1])
        }
    mouse.position = (int(slot[0]+SLOT_SIZE[0]/2), slot[1])
    time.sleep(0.1)
    screenshot = sct.grab(region)
    img = np.array(screenshot)
    raw_text = reader.readtext(img, detail=0)
    item = process_raw_text(raw_text)
    global ITEM_LIST
    print(ITEM_LIST)
    print(item)
    if not (item["item_name"] in ITEM_LIST):
        print("")
        item['item_name'] = similar_item_name(item['item_name'])
    if BEEP:
        winsound.Beep(500, 300)
    return item
                
def process_raw_text(raw_text):
    item = {"quantity":[1]}
    if len(raw_text) == 1: # if only item name in one line, and no quantity
        if "[" in raw_text[0]: # strip lvl
            item["item_name"] = [raw_text[0].split("[")[0].strip()]
        else:
            item["item_name"] = raw_text
        return item
    item["item_name"] = ""
    for text in raw_text:
        if text.startswith("["): # if the lvl of the item is in new line, just skip 
            continue
        if text.isdigit(): # if the quantity of the item is in new line
            item["quantity"] = [int(text)]
            continue
        if "[" in text: # strip item lvl
            item["item_name"] += f" {text.split('[')[0].strip()}"
            continue
        if "]" in text: # strip item lvl
            item["item_name"] += f" {text.split(']')[0].strip()}"
            continue
        item["item_name"] += f" {text.strip()}"
    
    item["item_name"] = [item["item_name"].strip()]
    return item

def test():
    data = {"item_name":["asd","bsd"], "quantity":[1, 1]}
    df = pd.DataFrame(data)
    print(df["item_name"].str.contains("aasd").any())

if __name__ == "__main__":
    test()

    