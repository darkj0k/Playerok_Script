import json
import subprocess
import time
import logging
import tkinter as tk
from os import path

from tkinter import filedialog, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class AutoResellerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Reseller Bot")
        self.logger = self.setup_logger()
        self.driver = None
        self.config = None

        # GUI Elements
        self.create_gui_elements()

    def create_gui_elements(self):
        # Configuration file section
        tk.Label(self.root, text="Config File:").pack(pady=5)
        self.config_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.config_path_var, width=50).pack(pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_config_file).pack(pady=5)

        # Start button
        tk.Button(self.root, text="Start Bot", command=self.start_bot).pack(pady=10)

        # Log output
        tk.Label(self.root, text="Logs:").pack(pady=5)
        self.log_output = scrolledtext.ScrolledText(self.root, height=20, width=80, state='disabled')
        self.log_output.pack(pady=10)

    def browse_config_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.config_path_var.set(file_path)

    def log(self, message, level="INFO"):
        self.log_output.configure(state='normal')
        self.log_output.insert(tk.END, f"[{level}] {message}\n")
        self.log_output.configure(state='disabled')
        self.log_output.see(tk.END)
        if level == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)

    def setup_logger(self):
        logger = logging.getLogger("AutoResellerGUI")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("bot_gui.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        return logger

    def load_config(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
                self.log("Configuration loaded successfully.")
        except FileNotFoundError:
            self.log("Configuration file not found. Please provide a valid JSON file.", level="ERROR")
            messagebox.showerror("Error", "Configuration file not found.")
        except json.JSONDecodeError:
            self.log("Invalid JSON file. Please check the format.", level="ERROR")
            messagebox.showerror("Error", "Invalid JSON file.")

    def setup_driver(self):
        options = Options()
        options.debugger_address = "localhost:9222"
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.log("Web driver initialized successfully.")
        except Exception:
            self.log(
                "Failed to start Chrome with remote debugging. Ensure Chrome is running with '--remote-debugging-port=9222'.",
                level="ERROR")
            messagebox.showerror("Error",
                                 "Failed to start Chrome. Ensure it is running with '--remote-debugging-port=9222'.")
            self.driver = None

    def start_bot(self):
        config_path = self.config_path_var.get()
        if not config_path:
            messagebox.showwarning("Warning", "Please select a configuration file.")
            return
        if path.exists("C://Program Files/Google/Chrome/Application/chrome.exe"):
            self.log("Chrome executable file found.", level="INFO")
            subprocess.run(["C://Program Files/Google/Chrome/Application/chrome.exe", "--remote-debugging-port=9222"])

        self.load_config(config_path)
        if not self.config:
            return

        self.setup_driver()
        if not self.driver:
            return

        self.run_bot()

    def run_bot(self):
        retries = 0
        max_retries = self.config['target_item']['max_retries']
        while retries < max_retries:
            try:
                self.log("Checking for completed items...")
                self.driver.get(f"https://playerok.com/profile/{self.config['target_item']['user']}/products")
                time.sleep(30)
                self.driver.get(f"https://playerok.com/profile/{self.config['target_item']['user']}/products/completed")
                time.sleep(10)
                number_completed = self.driver.find_element(By.CSS_SELECTOR,
                                                            self.config['classes']["number_completed"]).text
                if int(number_completed) == int(self.config['target_item']['number_completed']):
                    items = self.driver.find_elements(By.CLASS_NAME, self.config['classes']["item_name"])
                    self.log(f"Found {len(items)} completed items.")
                    for item in items:
                        self.republish_item(item)
                else:
                    self.log("No new completed items found.")
                    time.sleep(10)
                    continue

                retries += 1
                self.log(f"Retry {retries}/{max_retries} completed.")
            except Exception as e:
                self.log(f"An error occurred during bot execution: {e}", level="ERROR")
                break

        self.log("Bot finished execution.")
        if self.driver:
            self.driver.quit()

    def republish_item(self, item):
        try:
            item.click()
            time.sleep(4)
            relist_button = self.driver.find_element(By.CSS_SELECTOR, self.config['classes']['republish_button'])
            relist_button.click()
            time.sleep(2)

            confirm_button = self.driver.find_element(By.CSS_SELECTOR, self.config['classes']['confirm_button'])
            confirm_button.click()
            time.sleep(2)

            self.log("Item republish successfully.")
        except Exception as e:
            self.log(f"Failed to republish item: {e}", level="ERROR")


if __name__ == '__main__':
    root = tk.Tk()
    app = AutoResellerGUI(root)
    root.mainloop()
