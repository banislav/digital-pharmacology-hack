import re
import urllib.parse
from typing import Dict
from time import sleep
from typing import List

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

TIME_TO_LOAD_PAGE = 3
PUBCHEM_SOURCE_URL = "https://pubchem.ncbi.nlm.nih.gov/"
NCCOS_SOURCE_PAGE = "https://products.coastalscience.noaa.gov/peiar/search.aspx"


def get_search_page(driver: selenium.webdriver, query: str) -> List[str]:
    params = {
        "query": query
    }

    encoded_params = urllib.parse.urlencode(params)
    url = PUBCHEM_SOURCE_URL + "#" + encoded_params

    driver.get(url)
    sleep(2.5)
    source = driver.page_source

    soup = BeautifulSoup(source, 'lxml')
    target_divs = soup.find_all('div', {'class': 'f-medium'})
    a_elements = [div.find_all('a') for div in target_divs if div.find('a')]
    hrefs = [a_el[0]['href'] for a_el in a_elements]

    compounds_links = []

    for link in hrefs:
        match = re.match(r"https://pubchem.ncbi.nlm.nih.gov/compound/\d+", link)

        if match:
            compounds_links.append(match.group())

    return compounds_links


def get_page_content(driver: selenium.webdriver, url: str) -> str:
    driver.get(url)
    sleep(TIME_TO_LOAD_PAGE)
    content = driver.page_source

    return content


def find_toxicity(content: str) -> Dict[str, Dict[str, int]]:
    toxicity_dict = {'Human-Toxicity': {}, 'Non-Human-Toxicity': {}}

    soup = BeautifulSoup(content, features='lxml')
    human_tv = soup.find_all('section', attrs={'id': 'Human-Toxicity-Values'})
    nonhuman_tv = soup.find_all('section', attrs={'id': 'Non-Human-Toxicity-Values'})

    human_tv = [ht.find_all('div', attrs={'class': 'section-content-item'}) for ht in human_tv]
    human_tv = [ht.find_all('p')[0].text for ht in human_tv[0]]

    nonhuman_tv = [nht.find_all('div', attrs={'class': 'section-content-item'}) for nht in nonhuman_tv]
    nonhuman_tv = [ht.find_all('p')[0].text for ht in nonhuman_tv[0]]

    for tv in human_tv:
        match = re.findall(r'([A-Z][A-Z]50 \D*)\s+(\d+)\s+[M|m][G|g]/[K|k][G|g]', tv)
        if match:
            key, val = match[0]
            toxicity_dict['Human-Toxicity'][key] = int(val)

    for tv in nonhuman_tv:
        match = re.findall(r'([A-Z][A-Z]50 \D*)\s+(\d+)\s+[M|m][G|g]/[K|k][G|g]', tv)
        if match:
            key, val = match[0]
            toxicity_dict['Non-Human-Toxicity'][key] = int(val)

    return toxicity_dict


def extract_table_data(page_source:str):
    pass


def parse_nccos(driver: selenium.webdriver):
    driver.get(NCCOS_SOURCE_PAGE)

    query_from_select = driver.find_element(By.XPATH, '//*[@id="middleplaceholder_maincontent_ddl1"]')
    query_from_select = Select(query_from_select)

    query_from_select.select_by_value('2')

    drug_category_select = driver.find_element(By.XPATH, '//*[@id="middleplaceholder_maincontent_ddl3"]')
    drug_category_select = Select(drug_category_select)
    drug_category_options = list(drug_category_select.options)[1:]

    for drug_category in drug_category_options:
        drug_category_select.select_by_value(drug_category.get_attribute('value'))

        sleep(0.5)

        sub_category_select = driver.find_element(By.XPATH, '//*[@id="middleplaceholder_maincontent_ddlb2"]')

        if sub_category_select:
            sub_category_select = Select(sub_category_select)
            sub_category_options = list(sub_category_select.options)[1:]

            for sub_category in sub_category_options:
                sub_category_select.select_by_value(sub_category.get_attribute('value'))

                sleep(0.5)

                sort_by_select = driver.find_element(By.XPATH, '//*[@id="middleplaceholder_maincontent_ddlb3"]')

                if sort_by_select:
                    sort_by_select = Select(sort_by_select)
                    sort_by_options = list(sort_by_select.options)[1:]
                    sort_by_options = [option for option in sort_by_options if 'toxicity' in option.text.lower()]

                    for sort_by_option in sort_by_options:
                        sort_by_select.select_by_value(sort_by_option.get_attribute('value'))

                        submit_button = driver.find_element(By.XPATH, '//*['
                                                                      '@id="middleplaceholder_maincontent_btnSubmit2"]')

                        submit_button.click()
                        sleep(TIME_TO_LOAD_PAGE)

                        extract_table_data(driver.page_source)
