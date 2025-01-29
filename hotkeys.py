from pynput import keyboard
import json
import importlib


EXTRAS = ["alt_l", "alt_gr", "shift", "shift_r", "ctrl_r", "ctrl_l"]
extras_held = dict(zip(EXTRAS, [False]*len(EXTRAS)))
hotkeys = []
debug_mode = False
debug = None
escape = None

class Hotkey(object):

    def __init__(self, key, action, extras=[], params=None):
        self.key = key
        self.module = importlib.import_module(action)
        self.action = getattr(self.module, "main")
        self.extras = extras
        self.params = params

    def input(self, key_pressed, extras):
        if self.key == key_pressed and only_list_in_dict(list=self.extras,dict=extras): #checking if only self.extras are pressed
            self.action(self.params)


def main():

    global escape
    global debug

    with open('hotkeys/config.json','r') as open_json:
        json_config = json.load(open_json)

    escape = json_config["escape"]
    debug = json_config["debug"]

    print("To enter debug mode, hit:" + str(debug["key"]) +" " + " ".join(debug["extras"]))
    print("To escape, hit: " + str(escape["key"]) + " " +" ".join(escape["extras"]))
    print("Initialization...")
    with open('hotkeys/hotkeys.json','r') as open_json:
        json_list_of_hotkeys = json.load(open_json)
    
    for json_hotkey in json_list_of_hotkeys:
        hotkeys.append(Hotkey(key=json_hotkey["key"], action=json_hotkey["action"], extras=json_hotkey["extras"])) # initialize hotkeys

    print("Listening for keyboard input")
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()  # start to listen on a separate thread
    listener.join()  # remove if main thread is polling self.keys


def on_press(key):
    global debug_mode
    
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys

    if debug_mode:
        keys_to_print = [key for key, value in extras_held.items() if value] #gader all helf down extras
        if k in EXTRAS :  # to avoid printing out extras twice
            print(' '.join(keys_to_print))
        else:
            print(str(key) + " " + ' '.join(keys_to_print)) 

    for hotkey in hotkeys: #calling all hotkeys, to decide whether they do their action
        hotkey.input(key_pressed=k if not k == None else str(key), extras=extras_held)
   
    if k == escape["key"] and only_list_in_dict(list=escape["extras"], dict=extras_held):  # test if program should finish 
        return False
    
    elif k in extras_held.keys(): # check if an extra was pressed
        extras_held[k] = True

    elif k == debug["key"] and only_list_in_dict(list=debug["extras"], dict=extras_held):
        debug_mode = not debug_mode
        print("Debug mode: " + "enabled" if debug_mode else "disabled")

    
def on_release(key):
    
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    
    if k in extras_held.keys(): # check if an extra was released
        extras_held[k] = False


def only_list_in_dict(list,dict):
    """
    return True if only the list elements used as keys have true values in the dict
    """
    return all(dict[key] for key in list) and all(not dict[key] for key in dict if key not in list)

if __name__ == "__main__":
    main()

#Point(x=475, y=380)
#Point(x=1438, y=458)
#Point(x=1919, y=1079)