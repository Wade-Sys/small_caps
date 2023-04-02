import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#import numpy as np
import pandas as pd
import pickle
import csv
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------------------------------------------------
def open_and_confirm_dsvgo(headless = True, url='https://www.ariva.de/') -> webdriver:    
    webdriver_options = webdriver.FirefoxOptions()
    if headless:
        webdriver_options.add_argument('-headless')
    browser = webdriver.Firefox(options=webdriver_options)
    browser.get(url)
    time.sleep(8)
    dsvgo_iframe = browser.find_element_by_xpath('/html/body/div[6]/iframe')
    browser.switch_to.frame(dsvgo_iframe)
    browser.find_element_by_xpath('/html/body/div/div[2]/div[3]/div[1]/div[3]/div/button').click()
    time.sleep(5)
    browser.switch_to.default_content()
    return browser
# ---------------------------------------------------------------------------------------------------------------------
def extract_instrument_name_from_url(url:str = None):
    splitted_slash = url.split('/')
    last_part = splitted_slash[-1]
    splitted_question = last_part.split('?')
    instrument_name = splitted_question[0]
    return instrument_name
# ---------------------------------------------------------------------------------------------------------------------
def extract_instrumet_names(ariva_name_url_list:list = None):
    ariva_name_list_without_url = {}
    for item, value in ariva_name_url_list.items():
        ariva_name_list_without_url[item] = extract_instrument_name_from_url(value)
    return ariva_name_list_without_url
# ---------------------------------------------------------------------------------------------------------------------
def get_ariva_instrument_names(instrument_list:list = []) -> list:
    ariva_instrument_names = {}
    browser = open_and_confirm_dsvgo(headless=False)  
    for instrument in instrument_list:
        browser.find_element_by_xpath('//*[@id="livesearch"]').send_keys(instrument)
        time.sleep(1)
        browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[5]/div[1]/form/span[2]/input[1]').click()
        time.sleep(4)
        browser.find_element_by_xpath('//*[@id="livesearch"]').clear()
        print(instrument + ' ' + str(browser.current_url))
        ariva_instrument_names[instrument] = str(browser.current_url)
    browser.close()
    return ariva_instrument_names
# ---------------------------------------------------------------------------------------------------------------------
def dump_to_pickle(file_name:str = None, object=None):
    with open(file_name, 'wb') as file:
        pickle.dump(object, file)
    return None
# ---------------------------------------------------------------------------------------------------------------------
def load_from_pickle(file_name:str = None):
    with open(file_name, 'rb') as file_name:
        loaded_obj = pickle.load(file_name)
    return loaded_obj
# ---------------------------------------------------------------------------------------------------------------------
def extract_fundamental_kennzahlen(file_name:str = None, ariva_name_list_without_url:list = None):
    with open(file_name, 'a', newline='\n') as csvfile:
        fa_knz_csv_file = csv.writer(csvfile, delimiter=';',quotechar='"')
        fa_knz_csv_file.writerow(['WKN','ARIVA_NAME','JAHR','JAHRES_UEBERSCHUSS','KGV'])
        browser = open_and_confirm_dsvgo(headless = True)
        for wkn, instrument_name in ariva_name_list_without_url.items():
            url = f'https://www.ariva.de/aktien/{instrument_name}/kennzahlen/fundamentale-kennzahlen'
            print(url)
            browser.get(url)
            time.sleep(3)
            tr_years = browser.find_elements_by_xpath('/html/body/div[1]/div[3]/div[8]/div/div[3]/ariva-root/div/app-stock/app-stock-keydata/ariva-stock-keydata-fundamental/div/ariva-section[1]/section/ariva-table/div/table/thead/tr//th')
            tr_jahres_ueberschusses = browser.find_elements_by_xpath('/html/body/div[1]/div[3]/div[8]/div/div[3]/ariva-root/div/app-stock/app-stock-keydata/ariva-stock-keydata-fundamental/div/ariva-section[1]/section/ariva-table/div/table/tbody/tr[1]//td')
            tr_kgvs = browser.find_elements_by_xpath('/html/body/div[1]/div[3]/div[8]/div/div[3]/ariva-root/div/app-stock/app-stock-keydata/ariva-stock-keydata-fundamental/div/ariva-section[1]/section/ariva-table/div/table/tbody/tr[3]//td')
            years = [str(tr_year.text) for tr_year in tr_years] 
            jahres_ueberschuss = [str(tr_jahres_ubers.text) for tr_jahres_ubers in tr_jahres_ueberschusses]
            kgv = [str(tr_kgv.text) for tr_kgv in tr_kgvs] 
            fundamentalte_kennzahlen =  [list(item) for item in zip(years[1:], jahres_ueberschuss, kgv)]                
            [row.insert(0,wkn) for row in fundamentalte_kennzahlen]
            [row.insert(1,instrument_name) for row in fundamentalte_kennzahlen]
            [fa_knz_csv_file.writerow(fa_kennzahl) for fa_kennzahl in fundamentalte_kennzahlen]                            
    browser.close()
    return None
# ---------------------------------------------------------------------------------------------------------------------
def extract_numbers(input_text:str = None):
    output_number = 0
    for text in input_text.split():
        try:
            output_number = float(text)
            break
        except ValueError:
            pass
    return output_number
# ---------------------------------------------------------------------------------------------------------------------