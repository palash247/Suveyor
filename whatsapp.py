import time
import datetime as dt
import json
import os
import requests
import shutil
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import pyautogui
from models.whatsapp import WhatsAppModel
from models.group import GroupModel
import logging

logger = logging.getLogger(__name__)

pyautogui.PAUSE = 1


class WhatsApp:
    """
    Unofficial API for WhatsApp.
    """
    emoji = {}  # This dict will contain all emojies needed for chatting
    # we are using chrome as our webbrowser
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-data-dir=/home/palash/.config/google-chrome")
    timeout = 10  # The timeout is set for about ten seconds

    # This constructor will load all the emojies present in the json file and it will initialize the webdriver
    def __init__(self, wait, screenshot=None):
        self.browser = webdriver.Chrome(executable_path='./chromedriver', options=self.options,)
        self.browser.get("https://web.whatsapp.com/")
        session_open = None
        try:
            session_open = self.browser.find_element_by_xpath(
            "//DIV[@class='_1WZqU PNlAR xh-highlight'][text()='Use Here']")
            session_open.click()
        except NoSuchElementException:
            logger.info('No session is opened up right now. Opening new one.')
        # emoji.json is a json file which contains all the emojis
        with open("emoji.json") as emojies:
            # This will load the emojies present in the json file into the dict
            self.emoji = json.load(emojies)
        WebDriverWait(self.browser, wait).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="side"]/div[2]/div/label/input')))
        if screenshot:
            # This will save the screenshot to the specified file location
            self.browser.save_screenshot(screenshot)

    def check_update(self):
        WebDriverWait(self.browser, 50).until(EC.presence_of_element_located(
            (By.XPATH, "//DIV[@id='pane-side']//DIV[@class='_3j7s9']")))
        chats = self.browser.find_elements_by_xpath(
            "//DIV[@id='pane-side']//DIV[@class='_3j7s9']")
        for chat in chats   :
            chat.click()
            WebDriverWait(self.browser, 50).until(EC.presence_of_element_located(
                (By.CLASS_NAME, '_3AwwN')))
            # collect name of the group
            group_name = self.browser.find_element_by_xpath(
                "//HEADER[@class='_3AwwN']//SPAN[@dir='auto']")
            # whatsapp_group = WhatsAppModel.find_by_name(group_name)
            # check the membership 
            is_removed = None
            try:
                is_removed = self.browser.find_element_by_xpath(
                    "//DIV[@class='_2XiC1']")
            except NoSuchElementException:
                logger.info('No one removed bot from group.')
            if is_removed:
                # if whatsapp_group:
                #     whatsapp_group.delete_from_db()
                self.browser.find_element_by_xpath(
                    "(//SPAN[@data-icon='menu'])[2]"
                ).click()
                self.browser.find_element_by_xpath(
                    "//DIV[@class='_3lSL5 _2dGjP'][text()='Delete group']"
                ).click()
                self.browser.find_element_by_xpath(
                    "//DIV[@class='_1WZqU PNlAR'][text()='Delete']"
                ).click()
                try:
                    self.browser.find_element_by_xpath(
                        "//DIV[@class='_3I_df']"
                    ).click()
                    self.browser.find_element_by_xpath(
                        "//DIV[@class='_1WZqU PNlAR'][text()='Clear']"
                    ).click()
                except:
                    logger.info('')
                continue
            # if whatsapp_group:
            #     continue
            self.browser.find_element_by_class_name('_3AwwN').click()
            WebDriverWait(self.browser, 50).until(EC.presence_of_element_located(
                (By.CLASS_NAME, '_1xGbt')))
            chat_type = self.browser.find_element_by_class_name('_1xGbt').text
            if chat_type == 'Group info':
                # check if the bot is member of the group or not. if new membership
                # is found add the the membership to the database. if removal of 
                # membership is noticed then reflect the same on the database.
                logger.info('new group found')
                # group_model = GroupModel('whatsapp',group_identifier=group_name)
                # group_model.save_to_db()
                # group_fk = group_model.id
                # whatsapp_group = WhatsAppModel(group_name,group_fk)
                # whatsapp_group.save_to_db()

    # This method is used to send the message to the individual person or a group
    # will return true if the message has been sent, false else
    def send_message(self, name, message):
        # this will emojify all the emoji which is present as the text in string
        message = self.emojify(message)
        search = self.browser.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[2]/div/div[2]/div/label/input')
        # we will send the name to the input key box
        search.send_keys(name+Keys.ENTER)
        current_time = time.time()
        try:
            send_msg = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div/div[3]/div/footer/div[1]/div[2]/div/div[2]")))
            send_msg.send_keys(message+Keys.ENTER)  # send the message
            return True
        except TimeoutException:
            raise TimeoutError(
                "Your request has been timed out! Try overriding timeout!")
        except NoSuchElementException:
            return False
        except Exception:
            return False

    # This method will count the no of participants for the group name provided
    def participants_for_group(self, group_name):
        search = self.browser.find_element_by_xpath(
            '//*[@id="side"]/div[2]/div/label/input')
        # we will send the name to the input key box
        search.send_keys(group_name+Keys.ENTER)
        # some say this two try catch below can be grouped into one
        # but I have some version specific issues with chrome [Other element would receive a click]
        # in older versions. So I have handled it spereately since it clicks and throws the exception
        # it is handled safely
        try:
            click_menu = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, "//INPUT[@type='text']")))
            click_menu.click()
        except TimeoutException:
            raise TimeoutError(
                "Your request has been timed out! Try overriding timeout!")
        except NoSuchElementException as e:
            return "None"
        except Exception as e:
            return "None"
        current_time = dt.datetime.now()
        participants_xpath = "/html/body/div/div/div/div[1]/div[3]/span/div/span/div/div/div/div[4]/div[1]/div/div/div/span"
        while True:
            try:
                participants_count = self.browser.find_element_by_xpath(
                    participants_xpath).text
                if "participants" in participants_count:
                    return participants_count
            except Exception as e:
                pass
            new_time = dt.datetime.now()
            elapsed_time = (new_time - current_time).seconds
            if elapsed_time > self.timeout:
                return "NONE"

    # This method is used to get the main page
    def goto_main(self):
        self.browser.get("https://web.whatsapp.com/")

    # get the status message of a person
    # TimeOut is approximately set to 10 seconds
    def get_status(self, name):
        search = self.browser.find_element_by_xpath(
            '//*[@id="side"]/div[2]/div/label/input')
        # we will send the name to the input key box
        search.send_keys(name+Keys.ENTER)
        try:
            group_xpath = "/html/body/div/div/div/div[3]/header/div[1]/div/span/img"
            click_menu = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, group_xpath)))
            click_menu.click()
        except TimeoutException:
            raise TimeoutError(
                "Your request has been timed out! Try overriding timeout!")
        except NoSuchElementException:
            return "None"
        except Exception:
            return "None"
        try:
            # This is the css selector for status
            status_css_selector = ".drawer-section-body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1)"
            WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, status_css_selector)))
            status = self.browser.find_element_by_css_selector(
                status_css_selector).text
            # We will try for 100 times to get the status
            for i in range(10):
                if len(status) > 0:
                    return status
                else:
                    time.sleep(1)  # we need some delay
            return "None"
        except TimeoutException:
            raise TimeoutError(
                "Your request has been timed out! Try overriding timeout!")
        except NoSuchElementException:
            return "None"
        except Exception:
            return "None"

    # to get the last seen of the person
    def get_last_seen(self, name, timeout=10):
        search = self.browser.find_element_by_xpath(
            '//*[@id="side"]/div[2]/div/label/input')
        # we will send the name to the input key box
        search.send_keys(name+Keys.ENTER)
        last_seen_css_selector = ".O90ur"
        start_time = dt.datetime.now()
        try:
            WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, last_seen_css_selector)))
            while True:
                last_seen = self.browser.find_element_by_css_selector(
                    last_seen_css_selector).text
                if last_seen and "click here" not in last_seen:
                    return last_seen
                end_time = dt.datetime.now()
                elapsed_time = (end_time-start_time).seconds
                if elapsed_time > 10:
                    return "None"
        except TimeoutException:
            raise TimeoutError(
                "Your request has been timed out! Try overriding timeout!")
        except NoSuchElementException:
            return "None"
        except Exception:
            return "None"

    # This method does not care about anything, it sends message to the currently active chat
    # you can use this method to recursively send the messages to the same person
    def send_blind_message(self, message):
        try:
            message = self.emojify(message)
            send_msg = self.browser.find_element_by_xpath(
                "/html/body/div/div/div/div[3]/div/footer/div[1]/div[2]/div/div[2]")
            send_msg.send_keys(message+Keys.ENTER)  # send the message
            return True
        except NoSuchElementException:
            return "Unable to Locate the element"
        except Exception as e:
            return False

    # This method will send you the picture
    # This is a windows specific function, somebody PR for Mac and Linux
    def send_picture(self, name, picture_location, caption=None):
        search = self.browser.find_element_by_xpath(
            '//*[@id="side"]/div[2]/div/label/input')
        # we will send the name to the input key box
        search.send_keys(name+Keys.ENTER)
        try:
            self.browser.find_element_by_xpath(
                "/html/body/div/div/div/div[3]/div/header/div[3]/div/div[2]/div/span").click()
        except NoSuchElementException:
            return "Unable to Locate the element"
        pyautogui.press("down")
        pyautogui.press("enter")
        pyautogui.typewrite(picture_location)
        pyautogui.press("enter")
        try:
            if caption is not None:
                message = self.browser.find_element_by_xpath(
                    "/html/body/div/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/div/span/div/div[2]/div/div[3]/div[1]/div[2]")
                message.send_keys(caption)
            self.browser.find_element_by_xpath(
                "/html/body/div/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/span[2]/div/div/span").click()
        except NoSuchElementException:
            return "Cannot Send the picture"

    # override the timeout

    def override_timeout(self, new_timeout):
        self.timeout = new_timeout

    # This method is used to emojify all the text emoji's present in the message
    def emojify(self, message):
        for emoji in self.emoji:
            message = message.replace(emoji, self.emoji[emoji])
        return message

    def get_profile_pic(self, name):
        search = self.browser.find_element_by_xpath(
            '//*[@id="side"]/div[2]/div/label/input')
        search.send_keys(name+Keys.ENTER)
        try:
            open_profile = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div/div[3]/div/header/div[1]/div/img")))
            open_profile.click()
        except:
            print("nothing found")
        try:
            open_pic = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div/div[1]/div[3]/span/div/span/div/div/div/div[1]/div[1]/div/img")))
            open_pic.click()
        except:
            print("Nothing found")
        try:
            img = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div[2]/div/div/div/div/img')))
        except:
            print("Couldn't find the URL to the image")
        img_src_url = img.get_attribute('src')
        self.browser.get(img_src_url)
        self.browser.save_screenshot(name+"_img.png")

    # This method is used to quit the browser
    def quit(self):
        self.browser.quit()


whatsapp = WhatsApp(50)
