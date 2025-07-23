"""
conftest.py: Pytest fixtures for Selenium driver and logger
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as chromeservice
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from utils.logger import setup_logger


@pytest.fixture
def logger(request):
    test_name = request.node.name
    return setup_logger(test_name)


@pytest.fixture
def driver():
    ua = UserAgent()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument(f'user-agent={ua.random}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=chromeservice(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    yield driver
    driver.quit()
        