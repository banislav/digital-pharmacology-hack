import re
import urllib.parse
from typing import Dict
from time import sleep
from typing import List

import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

TIME_TO_LOAD_PAGE = 3
SOURCE_URL = "https://pubchem.ncbi.nlm.nih.gov/"


def get_search_page(driver: selenium.webdriver, query: str) -> List[str]:
    params = {
        "query": query
    }

    encoded_params = urllib.parse.urlencode(params)
    url = SOURCE_URL + "#" + encoded_params

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
