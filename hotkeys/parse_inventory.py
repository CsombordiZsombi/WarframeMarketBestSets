import time
import easyocr
import numpy as np
import mss
import pandas as pd
from pynput.mouse import Controller
import winsound
import json
from rapidfuzz.distance import Levenshtein
import keyboard as kb
import hotkeys

SLOT_GRID = None
SLOT_SIZE = None
ITEM_LIST = None

BEEP_ON_START = True
BEEP = False
BEEP_ON_END = True

mouse = Controller()

def main(*args, **kvargs):
    if BEEP_ON_START:
        winsound.Beep(500, 300)
    start_time = time.time()
    print("Scanning inventory")

    df, wdf = predict_inventory()
    df.to_json("inventory.json", orient="records", indent=4)
    wdf.to_json("wrong_reads.json", orient="records", indent=4)

    if BEEP_ON_START:
        winsound.Beep(500, 300)
    print(f"Done scanning inventory, took {round(time.time()-start_time,1)} seconds")
def predict_inventory():
    df = pd.DataFrame(columns=["item_name","quantity"]) # inventory data
    wdf = pd.DataFrame(columns=["item_name","quantity"]) # wrong reads
    
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
        reader = hotkeys.reader
        
        for row in SLOT_GRID: # we predict and store the first 4 rows.
            for slot in row:
                if kb.is_pressed('q'): 
                    return df
                item = predict_item(slot, reader, sct)
                if item["item_name"][0] == [""]: #detected nothing
                    return df, wdf
                if not item["item_name"][0] in ITEM_LIST:
                    wdf = pd.concat([wdf, pd.DataFrame(item)])
                    continue
                if df["item_name"].str.contains(item["item_name"][0]).any():
                    return df, wdf
                df = pd.concat([df, pd.DataFrame(item)])

        while True: # after the first 4 rows, we scroll, then predict until detect nothing
            mouse.scroll(0, -1) #scroll down
            time.sleep(0.5)
            for slot in SLOT_GRID[-1]:
                if kb.is_pressed('q'): 
                    return df, wdf
                item = predict_item(slot, reader, sct)
                if item["item_name"][0] == [""]: #detected nothing
                    return df, wdf
                if not item["item_name"][0] in ITEM_LIST:
                    wdf = pd.concat([wdf, pd.DataFrame(item)])
                    continue
                if df["item_name"].str.contains(item["item_name"][0]).any():
                    return df, wdf
                df = pd.concat([df, pd.DataFrame(item)])
    return df, wdf
def similar_item_name(word, max_distance=2):
    for w in ITEM_LIST:
        if Levenshtein.distance(word, w) <= max_distance:
            return w
    return word

def predict_item(slot, reader, sct):
    region = {
        "left":int(slot[0]),
        "top": int(slot[1]), 
        "width":int(SLOT_SIZE[0]),
        "height":int(SLOT_SIZE[1])
        }
    mouse.position = (int(slot[0]+SLOT_SIZE[0]/2), slot[1]) # move the mouse
    time.sleep(0.3)
    screenshot = sct.grab(region)
    img = np.array(screenshot)
    raw_text = reader.readtext(img, detail=0)
    item = process_raw_text(raw_text)

    if not (item["item_name"][0] in ITEM_LIST):
        item['item_name'] = [similar_item_name(item['item_name'])]
    if BEEP:
        winsound.Beep(500, 300)
    return item
                
def process_raw_text(raw_text):

    item = {"quantity":[1]}
    if len(raw_text) == 0:
        item["item_name"] = [""]
        return item
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
