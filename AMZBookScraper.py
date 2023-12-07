#!/usr/bin/env python3
import os
import re
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import pyautogui


class AmazonScraper:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument('--headless')

    def __init__(self):
        self.driver = webdriver.Chrome(options=self.options)

    def get_product_links(self, url, book_format, product_category):
        print('Loading ...')
        actions = ActionChains(self.driver)
        index = 34
        for subject in range(index, 34):
            self.driver.get(url)
            sleep(3)
            Select(self.driver.find_element_by_name('field-binding_browse-bin')).select_by_visible_text(book_format)
            print("Selected Subject Index:", subject)
            Select(self.driver.find_element_by_name('node')).select_by_index(subject)
            self.driver.find_element_by_name('Adv-Srch-Books-Submit').click()
            sleep(3)
            pages = self.driver.find_element_by_class_name('a-pagination').find_elements_by_class_name('a-disabled')[1].text
            print('Pages:', pages)
            pages = int(pages)
            for page in range(1, pages):
                product_links = {product_category: [p.get_attribute('href') for p in self.driver.find_elements_by_css_selector('.a-link-normal.a-text-normal')]}
                df = pd.DataFrame.from_dict(product_links)
                # if file does not exist write header
                if not os.path.isfile(product_category + 'links.csv'):
                    df.to_csv(product_category + 'links.csv', index=None)
                else:  # else if exists so append without writing the header
                    df.to_csv(product_category + 'links.csv', mode='a', header=False, index=None)
                # button_next = self.driver.find_element_by_link_text('Next')
                button_next = self.driver.find_element_by_class_name('a-last')
                actions.move_to_element(button_next)
                button_next.click()
                sleep(1)

    def get_products(self, url, product_category):
        # actions = ActionChains(self.driver)
        df = pd.read_csv(product_category + "links60.csv", index_col=None)
        counter = 0
        for index, row in df.iterrows():
            counter += 1
            book = {}
            print('Product number:', index)
            if 1 < counter < 4:
                continue
            if counter >= 4:
                counter = 0
            self.driver.get(url=row[product_category])
            try:
                best_seller_rank = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, 'SalesRank')))
                best_seller_rank = best_seller_rank.text
                best_seller_rank = re.sub(',', '', best_seller_rank)
                best_seller_rank = re.findall(r'(\d+)', best_seller_rank)
                if len(best_seller_rank) > 0:
                    best_seller_rank = int(best_seller_rank[0])
                else:
                    continue
            except:
                continue
            print('BSR:', best_seller_rank)
            if best_seller_rank < 500000:
                try:
                    book_title = self.driver.find_element_by_id('title').text
                    price = self.driver.find_element_by_css_selector('.a-size-base.a-color-price.a-color-price').text
                    print('Price:', price)
                    # Click on used price
                    try:
                        self.driver.find_element_by_css_selector('.olp-used.olp-link').click()
                        sleep(0.3)
                        used_price = self.driver.find_element_by_css_selector('.a-size-large.a-color-price.olpOfferPrice.a-text-bold').text
                    except: used_price = 0
                    try:
                        self.driver.find_element_by_name('olpCheckbox_primeEligible').click()
                        prime_price = self.driver.find_element_by_css_selector('.a-size-large.a-color-price.olpOfferPrice.a-text-bold').text
                    except: prime_price = 0
                    book["Title"] = [book_title]
                    book["StartURL"] = [row[product_category]]
                    book["Price"] = [price]
                    book["Amazon Best Seller"] = [best_seller_rank]
                    book["Used Price"] = [used_price]
                    book["Prime Price"] = [prime_price]
                    df = pd.DataFrame.from_dict(book)
                    # if file does not exist write header
                    if not os.path.isfile(product_category + '.csv'):
                        df.to_csv(product_category + '.csv', index=None)
                    else:  # else if exists so append without writing the header
                        df.to_csv(product_category + '.csv', mode='a', header=False, index=None)
                except:
                    continue
            else: continue

    def finish(self):
        self.driver.close()
        self.driver.quit()


def main():
    main_url = 'https://www.amazon.co.uk/Book-Search-Books/b?ie=UTF8&node=125552011'
    amazonscraper = AmazonScraper()
    books = 'Books'
    url = 'StartURL'
    book_formats = ['paperback', 'Hardcover']
    # for book_format in book_formats:
    #     amazonscraper.get_product_links(url=main_url, book_format=book_format, product_category=books)
    # amazonscraper.get_products(url=main_url, product_category=books)
    amazonscraper.finish()


if __name__ == '__main__':
    main()