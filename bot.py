import pyautogui
import time
import keyboard
import tkinter as tk
from threading import Thread
import json
import os

# Default settings
default_settings = {
    "loop_speed": 0.1,
    "hotkey": "F5",
    "screen_width": 1920,
    "screen_height": 1080,
    "image_paths": [
        'icon.png',
        'icon2.png',
        'icon3.png',
        'icon4.png',
        'icon5.png'
    ]
}

settings_file = "settings.json"

# Load settings from file or use defaults
if os.path.exists(settings_file):
    with open(settings_file, "r") as f:
        settings = json.load(f)
else:
    settings = default_settings

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Take Aller")
        self.root.geometry("400x400")

        self.label = tk.Label(root, text="Press the set hotkey to start/stop the automation.")
        self.label.pack(pady=10)

        self.running = False

        # Screen width
        self.screen_width_label = tk.Label(root, text="Screen Width:")
        self.screen_width_label.pack()
        self.screen_width_entry = tk.Entry(root)
        self.screen_width_entry.insert(0, settings["screen_width"])
        self.screen_width_entry.pack()

        # Screen height
        self.screen_height_label = tk.Label(root, text="Screen Height:")
        self.screen_height_label.pack()
        self.screen_height_entry = tk.Entry(root)
        self.screen_height_entry.insert(0, settings["screen_height"])
        self.screen_height_entry.pack()

        # Loop speed
        self.loop_speed_label = tk.Label(root, text="Loop Speed (seconds):")
        self.loop_speed_label.pack()
        self.loop_speed_entry = tk.Entry(root)
        self.loop_speed_entry.insert(0, settings["loop_speed"])
        self.loop_speed_entry.pack()

        # Hotkey
        self.hotkey_label = tk.Label(root, text="Hotkey:")
        self.hotkey_label.pack()
        self.hotkey_entry = tk.Entry(root)
        self.hotkey_entry.insert(0, settings["hotkey"])
        self.hotkey_entry.pack()

        # Image paths
        self.image_paths_label = tk.Label(root, text="Image Paths (comma-separated):")
        self.image_paths_label.pack()
        self.image_paths_entry = tk.Entry(root, width=50)
        self.image_paths_entry.insert(0, ','.join(settings["image_paths"]))
        self.image_paths_entry.pack()

        self.start_button = tk.Button(root, text="Start", command=self.start_automation)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_automation)
        self.stop_button.pack(pady=10)

        # Bind hotkey to start/stop the automation
        keyboard.add_hotkey(settings["hotkey"], self.toggle_automation)

    def toggle_automation(self):
        if self.running:
            self.stop_automation()
        else:
            self.start_automation()

    def start_automation(self):
        if not self.running:
            try:
                self.loop_speed = float(self.loop_speed_entry.get())
                self.hotkey = self.hotkey_entry.get()
                self.screen_width = int(self.screen_width_entry.get())
                self.screen_height = int(self.screen_height_entry.get())
                self.image_paths = self.image_paths_entry.get().split(',')
                
                # Update search region to the right half of the screen
                self.search_region = (self.screen_width // 2, 0, self.screen_width // 2, self.screen_height)
                
                self.running = True
                self.label.config(text="Automation is running.")
                self.thread = Thread(target=self.automation_loop)
                self.thread.start()

                # Save settings
                settings["loop_speed"] = self.loop_speed
                settings["hotkey"] = self.hotkey
                settings["screen_width"] = self.screen_width
                settings["screen_height"] = self.screen_height
                settings["image_paths"] = self.image_paths
                with open(settings_file, "w") as f:
                    json.dump(settings, f)

                # Rebind hotkey
                keyboard.remove_hotkey(self.toggle_automation)
                keyboard.add_hotkey(self.hotkey, self.toggle_automation)

            except ValueError:
                self.label.config(text="Invalid input. Please check your entries.")

    def stop_automation(self):
        if self.running:
            self.running = False
            self.label.config(text="Automation stopped.")

    def automation_loop(self):
        while self.running:
            try:
                for image_path in self.image_paths:
                    icon_location = pyautogui.locateOnScreen(
                        image_path.strip(),
                        region=self.search_region,
                        grayscale=True,
                        confidence=0.9
                    )
                    if icon_location is not None:
                        print(f"I can see {image_path} at", icon_location)
                        icon_center = pyautogui.center(icon_location)
                        pyautogui.click(icon_center)
                        # Small sleep to allow the click action to register
                        time.sleep(0.1)
                    else:
                        print(f"I am unable to see {image_path}")
                # Use the user-defined loop speed
                time.sleep(self.loop_speed)
            except Exception as e:
                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
