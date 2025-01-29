import time
import easyocr
import numpy as np
import mss
import market_api as mapi
import pandas as pd

reader = easyocr.Reader(["en"], gpu=True)

def predict_opened_relic_names():
    """Predicts the names of the opened relics. If can't detect, you suck (not really, it takes a screenshot from a 
       specific location from your screen, it might be different for the different ascpect ratios)

    Returns:
        list: containing the name strings
    """
    time.sleep(1)
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width, height = monitor["width"], monitor["height"]
        region = {"top": int(height * 0.35), 
                  "left":int(width * 0.24),
                  "width":int(width * 0.50),
                  "height":int(height * 0.08)}
        screenshot = sct.grab(region)
    img = np.array(screenshot)  # Gyors numpy tömbé alakítás
   
    return reader.readtext(img, detail=0)

def main(*args, **kvargs):
    relic_names = predict_opened_relic_names()
    df = pd.DataFrame()
    for name in relic_names:
        try:
            df = pd.concat([df, pd.DataFrame(mapi.get_item_price(name),index=[0])])
        except Exception as e:
            print(f"couldn\'t load: {e}")
    # TODO: fix can't load error
    print(df)

if __name__ == '__main__':
    main()