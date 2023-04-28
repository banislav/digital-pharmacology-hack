import re
from typing import Dict, Any
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_page_content(url: str) -> str:
    with webdriver.Chrome(ChromeDriverManager().install()) as driver:
        driver.get(url)
        sleep(2)
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
