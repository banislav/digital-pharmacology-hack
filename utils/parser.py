import re
import urllib.parse
from time import sleep
from typing import List

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

TIME_TO_LOAD_PAGE = 5
SOURCE_URL = "https://pubchem.ncbi.nlm.nih.gov/"


def get_search_page(query: str) -> List[str]:
    params = {
        "query": query
    }

    encoded_params = urllib.parse.urlencode(params)
    url = SOURCE_URL + "#" + encoded_params

    with webdriver.Chrome(ChromeDriverManager().install()) as driver:
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