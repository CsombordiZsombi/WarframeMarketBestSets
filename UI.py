import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser

hotkeys_process = None
streamlit_process = None

def hotkeys_on():
    global hotkeys_process
    if hotkeys_process is None:
        try:
            hotkeys_process = subprocess.Popen(["python", "hotkeys.py"])
        except FileNotFoundError:
            messagebox.showerror("Hiba", "Nem található a hotkeys.py fájl!")
    else:
        messagebox.showinfo("Hotkeys", "Hotkeys már be van kapcsolva!")


def hotkeys_off():
    global hotkeys_process
    if hotkeys_process is not None:
        hotkeys_process.terminate()
        hotkeys_process = None
    else:
        messagebox.showinfo("Hotkeys", "Hotkeys már ki van kapcsolva!")


def open_inventory():
    global streamlit_process
    if streamlit_process is None:
        try:
            # Streamlit indítása
            streamlit_process = subprocess.Popen(["streamlit", "run", "inventory_UI.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            messagebox.showerror("Hiba", "Nem található az inventory_UI.py fájl vagy a Streamlit nincs telepítve.")
    else:
        # Mindig böngésző megnyitása újra
        webbrowser.open("http://localhost:8502/")



# Fő ablak létrehozása
root = tk.Tk()
root.title("Warframe scraper ui")
root.geometry("400x300")

btn_hotkeys_on = tk.Button(root, text="Hotkeys ON", command=hotkeys_on, width=20)
btn_hotkeys_off = tk.Button(root, text="Hotkeys OFF", command=hotkeys_off, width=20)
btn_open_inventory = tk.Button(root, text="Open Inventory", command=open_inventory, width=20)

btn_hotkeys_on.pack(pady=20)
btn_hotkeys_off.pack(pady=20)
btn_open_inventory.pack(pady=20)

root.mainloop()
