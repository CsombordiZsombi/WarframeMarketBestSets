import time
import numpy as np
import mss
import market_api as mapi
import pandas as pd
import hotkeys
from hotkeys import parse_inventory as prs
from pynput.mouse import Button
import winsound

reader = hotkeys.reader
SLOTS = None
SLOT_SIZE = None
def predict_opened_relic_names():
    """Predicts the names of the opened relics, and jumps the cursor to the one with the highest price

    Returns:
        list: containing the name strings
    """
    beep = prs.BEEP
    prs.BEEP = True
    
    time.sleep(1)
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width, height = monitor["width"], monitor["height"]
        global SLOT_SIZE
        SLOT_SIZE = (int(width*0.127), int(height*0.09))
        global SLOTS
        SLOTS = [
            (int(width*0.248), int(height*0.33)),
            (int(width*0.388), int(height*0.33)),
            (int(width*0.502), int(height*0.33)),
            (int(width*0.628), int(height*0.33))
        ]
        df = pd.DataFrame(columns=["item_name","quantity"])
        for slot in SLOTS:
            item, match = prs.predict_item(slot, SLOT_SIZE, sct)
            #print(f'item:{item}, match:{match}')
            if match:
                df = pd.concat([df, pd.DataFrame(item)], ignore_index=True)
                #print(item["item_name"])
            else:
                #print(item["item_name"], " amúgy gecire nem kéne hozzáfűznie itt semmi értelmeset")
                df = pd.concat([df, pd.DataFrame({"item_name":[""], "quantity":[0]})], ignore_index=True)

    prs.BEEP = beep
    return df

def main(*args, **kvargs):
    relic_names = predict_opened_relic_names()
    df = pd.DataFrame()
    for name in relic_names["item_name"]:
        #print(name)
        try:
            if name == "":
                raise ValueError("Nem igazán error de mindegy")
            df = pd.concat([df, pd.DataFrame(mapi.fetch_item_price(name),index=[0])])
        except Exception as e:
            df = pd.concat([df, pd.DataFrame({"item_url":[name], "min_sell":[0], "max_buy":[0]})])
            #print(f"couldn\'t load: {e}")
    df.reset_index(inplace = True, drop = True)

    if df["max_buy"].sum() == 0:
        # TODO: if no one wants to buy them, should pick the highest ducat value item
        winsound.Beep(1000, 300)
        time.sleep(0.1)
        winsound.Beep(1000, 300)
        return
    
    slot = SLOTS[df["max_buy"].idxmax()]
    prs.mouse.position = (int(slot[0]+SLOT_SIZE[0]/2), slot[1])
    time.sleep(0.1)
    prs.mouse.click(Button.left, 1)
    winsound.Beep(500, 300)


if __name__ == '__main__':
    main()


    """
    Mouse position: x=477, y=363, thats=width*0.248, height*0.336
    Mouse position: x=712, y=456, thats=width*0.371, height*0.422
    Mouse position: x=745, y=389, thats=width*0.388, height*0.36
    Mouse position: x=963, y=384, thats=width*0.502, height*0.356
    Mouse position: x=1205, y=361, thats=width*0.628, height*0.334
    """