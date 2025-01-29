import time
import easyocr
import numpy as np
import mss
import market_api as mapi

reader = easyocr.Reader(["en"])

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
        print(width, height)
        region = {"top": int(height * 0.35), 
                  "left":int(width * 0.24),
                  "width":int(width * 0.50),
                  "height":int(height * 0.08)}
        screenshot = sct.grab(region)
    img = np.array(screenshot)  # Gyors numpy tömbé alakítás
   
    return reader.readtext(img, detail=0)

def main(*args, **kwargs):
    relic_names = predict_opened_relic_names()
    
    '''for name in relic_names:
        try:
            mapi.get_item_price(name)
        except Exception as e:
            print("couldn\'t load")
    print("Hello te geci")'''

    print(relic_names)
    
if __name__ == '__main__':
    main()