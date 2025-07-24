from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TE, NoSuchElementException as NE
# import tkinter as tk
import time
from database import db


class SearchAmazon:
    def __init__(self, driver):
        # self.root = tk.Tk()
        # self.screen_height = self.root.winfo_screenheight()
        self.driver = driver
        self.url = 'https://www.amazon.com/'
        self.wait = WebDriverWait(self.driver, 30)
        self.search_locator = (By.NAME, 'k') # uses for japan
        self.alternate_search = (By.NAME, 'field-keywords')
        self.alternate_search_two = (By.ID, 'nav-bb-search')
        self.search_results = (By.CLASS_NAME, 's-search-results')
        self.search_results_try = (By.CLASS_NAME, 's-main-slot')
        self.today_deals_dismiss = (By.CLASS_NAME, 'a-button-input')
        self.continue_shopping_check = (By.CLASS_NAME, 'a-button-text')
        self.product_name_locator_one = (By.CLASS_NAME, 'a-text-normal')
        self.product_name_locator_two = (By.CSS_SELECTOR, 'a-text-normal')
        self.data_indexes = []
        self.product_search = 1000
        self.product_attributes = {
            'product index': [],
            'title': [],
            'price': [],
            'rating': [],
            'url': []
        }
    

    def load(self):
        return self.driver.get(self.url)
    

    def remove_adds(self, element_locator):
        try:
            dismiss_button = self.wait.until(EC.presence_of_element_located(element_locator))
            if dismiss_button.is_displayed():
                self.driver.execute_script("arguments[0].click();", dismiss_button)
            else:
                return None
        except TE:
            pass


    def dismiss_today_deals(self):
        try:
            dismiss_button = self.wait.until(EC.presence_of_element_located(self.today_deals_dismiss))
            if dismiss_button.is_displayed():
                self.driver.execute_script("arguments[0].click();", dismiss_button)
            else:
                return None
        except TE:
            pass

    def _send_text_to_box(self, box, text):
        box.clear()
        box.send_keys(text)
        box.send_keys(Keys.RETURN)

    def fill_search_box(self, product):
        self.remove_adds(self.continue_shopping_check)
        self.dismiss_today_deals()
        try:
            search_box = self.wait.until(EC.presence_of_element_located(self.search_locator))
            self._send_text_to_box(search_box, product)
        except TE:
            try:
                search_box = self.wait.until(EC.presence_of_element_located(self.alternate_search_two))
                self._send_text_to_box(search_box, product)
            except TE:
                try:
                    search_box = self.wait.until(EC.presence_of_element_located(self.alternate_search))
                    self._send_text_to_box(search_box, product)
                except TE:
                    pass

    def _get_details(self, product, **kwargs):
        selectors = {
            'title':[
            'h2.a-size-base-plus span',  # Standard product
            'h2.a-size-mini span',       # Alternative layout
            'h2 span',                  # Fallback
            'h2.a-size-base-plus'
            ],
        'price': [
            'span.a-price span.a-offscreen', 
            'span.a-price .a-offscreen',
            'span.a-price',
            '.a-price-symbol', 
            '.a-price[data-a-size="l"]',
            '.a-price[data-a-color="base"]'
            ],
        'rating': [
            'span.a-icon-all',             
            'i.a-icon-star-small span',    
            "[data-cy='reviews-ratings-slot'] span", 
            "[aria-label*='out of 5 stars']", 
            '.a-popover-trigger span'
        ], 
        'url': [
            'a.a-link-normal.s-line-clamp-2.s-link-style.a-text-normal',
            'a.a-link-normal.a-text-normal',                              
        '   h2.a-size-mini a'
        ]
        }

        for key, is_requested in kwargs.items():
            if not is_requested and key not in selectors:
                continue
            for selector in selectors[key]:
                try:
                    element = product.find_element(By.CSS_SELECTOR, selector)
                    product_detail = element.get_attribute('textContent').strip() if key == 'price' else element.text.strip()
                    if key == 'price':
                        if product_detail == '$':
                            whole_price = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price-whole')))
                            fraction_price = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price-fraction')))
                            product_detail = f"${whole_price.text}.{fraction_price.text}"
                        elif 'a-offscreen' in selector:
                            pass
                        else:
                            try:
                                visible_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price-symbol, .a-price-whole, .a-price-fraction')))
                                product_detail = visible_element.text
                            except NE:
                                pass
                    if key == 'rating':
                        try:
                            if 'out of 5 stars' in element.text:
                                product_detail = element.text
                            if 'out of 5 stars' in element.get_attribute('innerText'):
                                product_detail = element.get_attribute('innerText')
                            if 'out of 5 stars' in element.get_attribute('textContent'):
                                product_detail = element.get_attribute('textContent')
                        except NE:
                            continue
                    if key == 'title':
                        try:
                            product_detail = element.text.encode('ascii', errors='ignore').decode()
                        except UnicodeEncodeError:
                            continue
                    if key == 'url':
                        try:
                            product_detail = element.get_attribute('href')
                        except NE:
                            continue
                except NE:
                    continue
                except UnicodeEncodeError:
                    try:
                        product_detail = element.text.encode('ascii', errors='ignore').decode()
                    except NE:
                        continue
                return product_detail
    

    def extract_details(self):
        # Get all data-index values
        product_ind = set()
        tracker = 0
        product_details = []
        product_attributes = {
            'title': [],
            'price': [],
            'rating': [],
            'url': []
        }
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while tracker < self.product_search: 
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            # self.driver.execute_script(f'window.scrollBy(0, {self.screen_height/15})', '')
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            product_indexes = self.driver.execute_script("""
            return Array.from(
                document.querySelectorAll('div[data-component-type="s-search-result"][data-index]')
            ).map(el => el.getAttribute('data-index'));
        """)
            product_ind.update(product_indexes)
            tracker += 1
            for index in product_ind:
                if index not in product_details:
                    product_details.append(index)
                    try:
                        product = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[data-component-type="s-search-result"][data-index="{index}"]')))
                        title = self._get_details(product=product, title=True)
                        product_attributes['title'].append(title)
                        price = self._get_details(product=product, price=True)
                        product_attributes['price'].append(price)
                        rating = self._get_details(product=product, rating=True)
                        product_attributes['rating'].append(rating)
                        url = self._get_details(product=product, url=True)
                        product_attributes['url'].append(url)
                    except TE:
                        pass
                else:
                    pass

        return product_attributes
    

    def send_to_db(self):
        data = self.extract_details()
        conn = db.get_connection()
        cur = conn.cursor()
        for detail in range(len(data['title'])):    
            cur.execute("""
                INSERT INTO products (title, price, rating, url)
                VALUES (%s, %s, %s, %s)
            """, (
                data['title'][detail],
                data['price'][detail],
                data['rating'][detail],
                data['url'][detail]
            ))
        conn.commit()
        cur.close()
        conn.close()

