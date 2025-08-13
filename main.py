import io
import socket
import threading
import urllib.request
from PIL import Image, ImageDraw
import pystray



def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/D"

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as resp:
            return resp.read().decode().strip()
    except Exception:
        return "N/D"

def copy_to_clipboard(text):
    import tkinter as tk
    r = tk.Tk()
    r.withdraw()
    try:
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
    finally:
        r.destroy()

 
def show_ips_window(priv, pub):
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    root.title("Tus IPs")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text=f"Private IP : {priv}").grid(row=0, column=0, sticky="w", pady=(0,4))
    ttk.Label(frm, text=f"Public IP: {pub}").grid(row=1, column=0, sticky="w", pady=(0,8))

    btns = ttk.Frame(frm)
    btns.grid(row=2, column=0, sticky="e")
    ttk.Button(btns, text="Copy private", command=lambda: copy_to_clipboard(priv)).pack(side="left", padx=(0,6))
    ttk.Button(btns, text="Copy public", command=lambda: copy_to_clipboard(pub)).pack(side="left")
    ttk.Button(frm, text="Close", command=root.destroy).grid(row=3, column=0, sticky="e", pady=(10,0))

    root.mainloop()


def make_icon_image():
    size = (16, 16)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    d.ellipse((1,1,15,15), fill=(0, 122, 204, 255))
    d.arc((3,3,13,13), start=0, end=360, fill=(255,255,255,255), width=2)
    d.line((4,8,12,8), fill=(255,255,255,255), width=2)
    d.line((8,4,8,12), fill=(255,255,255,255), width=2)
    return im

class IPTrayApp:
    def __init__(self):
        self.icon = pystray.Icon("IP Tray", make_icon_image(), "IP Viewer")
        self.priv = "N/D"
        self.pub = "N/D"
        self.lock = threading.Lock()

        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Show IPs", self.action_show),
            pystray.MenuItem("Copy public", self.action_copy_public),
            pystray.MenuItem("Copy private", self.action_copy_private),
            pystray.MenuItem("Update", self.action_refresh),
            pystray.MenuItem("Exit", self.action_quit)
        )

    def start(self):
        self.refresh()
        self.icon.title = f"Priv: {self.priv} | Pub: {self.pub}"
        self.icon.run()

    def refresh(self):
        with self.lock:
            self.priv = get_private_ip()
            self.pub = get_public_ip()
            self.icon.title = f"Priv: {self.priv} | Pub: {self.pub}"


    def action_show(self, icon, item):
        with self.lock:
            priv, pub = self.priv, self.pub
        threading.Thread(target=show_ips_window, args=(priv, pub), daemon=True).start()

    def action_copy_public(self, icon, item):
        with self.lock:
            copy_to_clipboard(self.pub)

    def action_copy_private(self, icon, item):
        with self.lock:
            copy_to_clipboard(self.priv)

    def action_refresh(self, icon, item):
        self.refresh()

    def action_quit(self, icon, item):
        self.icon.stop()

if __name__ == "__main__":
    IPTrayApp().start()
