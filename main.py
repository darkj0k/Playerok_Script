import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class AutoReseller:
    def __init__(self, config_file):
        self.logger = self.setup_logger()
        self.config_file = config_file
        self.load_config()
        self.driver = self.setup_driver()
        self.logger.info("Bot initialized successfully.")

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
                self.logger.info("Configuration loaded successfully.")
        except FileNotFoundError:
            print("Configuration file not found. Please provide a valid JSON file.")
            exit()
        except json.JSONDecodeError:
            print("Invalid JSON file. Please check the format.")
            exit()

    def setup_driver(self):
        options = Options()
        options.debugger_address = "localhost:9222"
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            return driver
        except Exception:
            print("Please start Chrome thought bash with parametres '--remote-debugging-port=9222' and login Playerok")
            input("Press Enter to continue...")
            exit()

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("bot.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def check_completed_item(self):
        while True:
            self.logger.info("Checking for completed items...")
            self.driver.get(f"https://playerok.com/profile/{self.config['target_item']['user']}/products")
            time.sleep(5)
            self.driver.get(f"https://playerok.com/profile/{self.config['target_item']['user']}/products/completed")
            time.sleep(5)
            number_completed = self.driver.find_element(By.CSS_SELECTOR,
                                                        self.config['classes']["number_completed"]).text
            if int(number_completed) == 1:
                item = self.driver.find_element(By.CLASS_NAME, self.config['classes']["item_name"])
            else:
                time.sleep(5)
                continue

            title = item.find_element(By.CSS_SELECTOR, self.config['classes']['item_title']).text
            if self.config['target_item']['name'].lower() == title.lower():
                self.logger.info(f"Found {title} completed item.")
                return item

    def run(self):
        retries = 0
        max_retries = self.config['target_item']['max_retries']
        while retries < max_retries:
            completed_item = self.check_completed_item()

            self.republish_item(completed_item)

            retries += 1
            self.logger.info(f"Retry {retries}/{max_retries} completed.")

        self.logger.info("Bot finished execution.")
        self.driver.quit()

    def republish_item(self, item):
        try:
            item.click()
            time.sleep(4)
            relist_button = self.driver.find_element(By.CSS_SELECTOR, self.config['classes']['republish_button'])
            relist_button.click()
            time.sleep(2)

            if self.config['target_item']['type'] == "common":
                self.driver.find_element(By.CSS_SELECTOR, self.config['classes']['common_button']).click()

            confirm_button = self.driver.find_element(By.CSS_SELECTOR, self.config['classes']['confirm_button'])
            confirm_button.click()
            time.sleep(2)

            self.logger.info("Item republish successfully.")

        except Exception as e:
            self.logger.error(f"Failed to republish item: {str(e)}")


if __name__ == "__main__":
    import argparse
    import platform
    import subprocess

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, help="Name of the item to republish")
    parser.add_argument("--type", type=str, default="common", help="Type of item to republish")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum number of times to republish item")
    parser.add_argument("--user", type=str, help="Username to show products")
    config_path = "config.json"
    args = parser.parse_args()
    with open(config_path, 'r') as config_read:
        config = json.load(config_read)
        config["target_item"]["name"] = args.name
        config["target_item"]["max_retries"] = args.max_retries
        if args.type == "common" or args.type == "premium":
            config["target_item"]["type"] = args.type
        else:
            print("Type must be either 'common' or 'premium'")
        config["target_item"]["user"] = args.user
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file)
    if platform.system() == "Windows":
        try:
            subprocess.run(['"C:\Program Files\Google\Chrome\Application\chrome.exe"', "--remote-debugging-port=9222"])
        except File
    bot = AutoReseller(config_path)
    bot.run()
