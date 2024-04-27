import os
import json

from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def get_paths() -> tuple[str, str]:
    install_dir = '/snap/firefox/current/usr/lib/firefox'
    driver_loc = os.path.join(install_dir, "geckodriver")
    binary_loc = os.path.join(install_dir, "firefox")
    return binary_loc, driver_loc


def get_browser() -> webdriver.Firefox:
    opts = webdriver.FirefoxOptions()
    try:
        br_service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=br_service, options=opts)
    except WebDriverException:
        print('GeckoDriverManager из webdriver_manager не запустился...')
    opts.binary_location, driver_loc = get_paths()
    return webdriver.Firefox(service=Service(driver_loc), options=opts)


def get_redirect_uri(app_id: str) -> str:
    url = ('https://oauth.vk.com/authorize'
           f'?client_id={app_id}'
           '&display=page&redirect_uri=https://oauth.vk.com/blank.html'
           '&scope=1030&response_type=token&v=5.191&state=123456')
    with get_browser() as browser:
        browser.get(url)
        try:
            WebDriverWait(browser, 180).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//body/b[1][text()="не копируйте"]')
                )
            )
            return browser.current_url
        finally:
            browser.quit()
            print('завершилась работа браузра')


def get_token(token: str, app_id: str) -> str:
    if token is None:
        redirect_uri = get_redirect_uri(app_id)
        return redirect_uri.split('=')[1].replace('&expires_in', '')
    else:
        return token


class User:

    def __init__(self, name, surname, vk_id):
        self.first_name: str = name
        self.last_name = surname
        self.vk_id: int = vk_id
        self.city: str | None = None
        self.is_favorite = False
        self.photos = {}

    def get_user_data(self) -> json:
        user_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'vk_id': self.vk_id
        }
        return json.dumps(user_data)
