import os
import sys
import traceback

from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def get_paths() -> tuple[str, str]:
    """Функция возвращает пути расположения firefox и geckodriver"""
    install_dir = '/snap/firefox/current/usr/lib/firefox'
    driver_loc = os.path.join(install_dir, "geckodriver")
    binary_loc = os.path.join(install_dir, "firefox")
    return binary_loc, driver_loc


def get_browser(binary_loc: str | None = None,
                driver_loc: str | None = None) -> webdriver.Firefox:
    """Возращает объект webdriver Firefox.

    Функция создаёт и возвращает драйвер Firefox. Первоначально происходит
    попытка создания драйвера с использованием GeckoDriverManager из
    библиотеки webdriver_manager, в случае неуспешной попытки (на Linux c
    применением snap пакетов, создание объекта управления драйвером может
    потерпеть неудачу, т.к. snap пакет использует свой драйвер) функция
    попробует создать объект webdriver.Firefox на базе драйвера пакета snap,
    используя значения переданных параметров для отыскания установленных
    компонентов. (Работае только в случае, если в системе установлен snap
    пакет Firefox).
    :param binary_loc: путь к компоненту firefox
    :type binary_loc: str or None
    :param driver_loc: путь к компоненту geckodriver
    :type driver_loc: str
    :exception WebDriverException:
    :return:
    """
    opts = webdriver.FirefoxOptions()
    try:
        br_service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=br_service, options=opts)
    except WebDriverException:
        print('GeckoDriverManager из webdriver_manager не запустился...')
    opts.binary_location = binary_loc
    return webdriver.Firefox(service=Service(driver_loc), options=opts)


def get_vk_redirect_uri(app_id: int, browser: webdriver.Firefox) -> str:
    """Возвращает строковое представление адрессной строки Вконтакте.

    Использую объект переданного webdriver-a, функция запускает процедуру
    регистрации Вконтакте, после её прохождения - функция переходит на
    указанную в запросе страницу, содержащую в адреснной строке токен
    и id пользователя. Эту строку функция и возвращает. (На регистрацию
    выделяется 180 сек).
    :param app_id: app_id Standalone-приложения
    :type app_id: int
    :param browser: объект WebDriver: Firefox, Chrome, Safari...
    :type browser: WebDriver
    :return:
    :exception WebDriverException:
    """
    url = ('https://oauth.vk.com/authorize'
           f'?client_id={app_id}'
           '&display=page&redirect_uri=https://oauth.vk.com/blank.html'
           '&scope=1030&response_type=token&v=5.191&state=123456')
    browser.get(url)
    try:
        WebDriverWait(browser, 180).until(
            ec.presence_of_element_located(
                (By.XPATH, '//body/b[1][text()="не копируйте"]')
            ),
            message='Превышено время ожидания авторицации...'
        )
        return browser.current_url
    finally:
        browser.quit()


def get_token_and_id(redirect_uri: str) -> tuple[str, int]:
    """Возвращает кортеж из токена и id пользователя Вконтакте

    На вход подаётся строковое представление адрессной строки страницы
    регистрации Вконтакте
    :param redirect_uri: адресная строка страницы переадресации при регистрации
    :return:
    """
    token = redirect_uri.split('=')[1].replace('&expires_in', '')
    user_id = redirect_uri.split('=')[3].replace('&state', '')
    return token, int(user_id)


def perform_authorization(app_id: int) -> tuple[str, int]:
    try:
        browser = get_browser(*get_paths())
        redirect_uri = get_vk_redirect_uri(app_id, browser)
        token, user_id = get_token_and_id(redirect_uri)
    except (WebDriverException, ValueError):
        traceback.print_exc()
        print('Не получилось выполнить авторизацию пользователя в '
              'ВКонтакте...')
        sys.exit(1)
    else:
        return token, user_id
