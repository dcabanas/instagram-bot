from selenium import webdriver
import time
_ = time; del _
from utility_methods.utility_methods import *
import urllib.request
import os
import main

class InstaBot:

    def __init__(self):
        """"
        Creates an instance of InstaBot class.
        """

        #options = webdriver.ChromeOptions()
        #options.add_argument('headless')
        self.driver = webdriver.Chrome(config['ENVIRONMENT']['CHROMEDRIVER_PATH'])
        self.new_height = self.driver.execute_script("return document.body.scrollHeight")
        self.last_height = self.new_height
        self.username = config['IG_AUTH']['USERNAME']
        self.password = config['IG_AUTH']['PASSWORD']

        self.login_url = config['IG_URLS']['LOGIN']
        self.nav_user_url = config['IG_URLS']['NAV_USER']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']
        self.user_tags = config['IG_USERS']['TAGS']

        self.logged_in = False

    @insta_method
    def login(self):
        """
        Logs a user into Instagram via the web portal
        """

        self.driver.get(self.login_url)
        # accept Cookies popup
        self.driver.find_element_by_xpath("//*[text()='Accept']").click()
        time.sleep(2)

        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_element_by_xpath("//*[text()='Log In']").click()
        time.sleep(5)

        # dont save auth info
        self.driver.find_element_by_xpath("//*[text()='Not Now']").click()
        time.sleep(2)
        # dont turn on notifications
        self.driver.find_element_by_xpath("//*[text()='Not Now']").click()

    @insta_method
    def search_tag(self, tag):
        """
        Navigates to a search for posts with a specific tag on IG.

        Args:
            tag:str: Tag to search for
        """

        self.driver.get(self.get_tag_url.format(tag))

    @insta_method
    def nav_user(self, user):
        """
        Navigates to a users profile page

        Args:
            user:str: Username of the user to navigate to the profile page of
        """

        self.driver.get(self.nav_user_url.format(user))

    @insta_method
    def follow_user(self, user):
        """
        Follows user(s)

        Args:
            user:str: Username of the user to follow
        """

        self.nav_user(user)

        follow_buttons = self.find_buttons('Follow')

        for btn in follow_buttons:
            btn.click()

    @insta_method
    def unfollow_user(self, user):
        """
        Unfollows user(s)

        Args:
            user:str: Username of user to unfollow
        """

        self.nav_user(user)

        unfollow_btns = self.find_buttons('Following')

        if unfollow_btns:
            for btn in unfollow_btns:
                btn.click()
                unfollow_confirmation = self.find_buttons('Unfollow')[0]
                unfollow_confirmation.click()
        else:
            print('No {} buttons were found.'.format('Following'))

    @insta_method
    def download_user_images(self, user):
        """
        Downloads all images from a users profile.
        """

        self.nav_user(user)

        img_srcs = []
        finished = False
        while not finished:
            finished = self.infinite_scroll()  # scroll down

            img_srcs.extend(
                [img.get_attribute('src') for img in self.driver.find_elements_by_class_name('FFVAD')])  # scrape srcs

        img_srcs = list(set(img_srcs))  # clean up duplicates

        for idx, src in enumerate(img_srcs):
            self.download_image(src, idx, user)

    @insta_method
    def like_latest_posts(self, user, n_posts, like=True):
        """
        Likes a number of a users latest posts, specified by n_posts.

        Args:
            user:str: User whose posts to like or unlike
            n_posts:int: Number of most recent posts to like or unlike
            like:bool: If True, likes recent posts, else if False, unlikes recent posts

        TODO: Currently maxes out around 15.
        """

        action = 'Like' if like else 'Unlike'

        self.nav_user(user)

        imgs = []
        imgs.extend(self.driver.find_elements_by_class_name('_9AhH0'))

        for img in imgs[:n_posts]:
            img.click()
            time.sleep(1)
            try:
                self.driver.find_element_by_xpath("//*[@aria-label='{}']".format(action)).click()
            except Exception as e:
                print(e)

            # self.comment_post('beep boop testing bot')
            self.driver.find_elements_by_class_name('ckWGn')[0].click()

    @insta_method
    def comment_post(self, url, tags):
        """
        Comments on a post
        """

        self.driver.get(url)
        for tag in tags:
            comment_input = self.driver.find_element_by_xpath("//*[@aria-label='Add a comment…']")
            comment_input.click()
            comment_input = self.driver.find_element_by_xpath("//*[@aria-label='Add a comment…']")
            comment_input.send_keys(tag)
            self.driver.find_element_by_xpath("//*[text()='Post']").click()
            time.sleep(2)

    @staticmethod
    def download_image(src, image_filename, folder):
        """
        Creates a folder named after a user to to store the image, then downloads the image to the folder.
        """

        folder_path = './{}'.format(folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        img_filename = 'image_{}.jpg'.format(image_filename)
        urllib.request.urlretrieve(src, '{}/{}'.format(folder, img_filename))

    def infinite_scroll(self):
        """
        Scrolls to the bottom of a users page to load all of their media

        Returns:
            bool: True if the bottom of the page has been reached, else false

        """

        SCROLL_PAUSE_TIME = 1

        self.last_height = self.driver.execute_script("return document.body.scrollHeight")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(SCROLL_PAUSE_TIME)

        if self.new_height == self.last_height:
            return True

        return False

    def find_buttons(self, button_text):
        """
        Finds buttons for following and unfollowing users by filtering follow elements for buttons.
        Defaults to finding follow buttons.

        Args:
            button_text: Text that the desired button(s) has 
        """

        buttons = self.driver.find_elements_by_xpath("//*[text()='{}']".format(button_text))

        return buttons


if __name__ == '__main__':
    # loads GUI
    main.start()

    # config loading
    config_file_path = './config.ini'
    logger_file_path = './bot.log'
    config = init_config(config_file_path)
    logger = get_logger(logger_file_path)

    # main script
    bot = InstaBot()
    bot.login()
    bot.comment_post(main.url, bot.user_tags.split(","))
