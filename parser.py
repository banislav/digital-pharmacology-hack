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


def find_toxicity(content: str) -> Dict[str, Dict[Any, Any]]:
    toxicity_dict = {'Human-Toxicity': {}, 'Non-Human-Toxicity': {}}

    soup = BeautifulSoup(content, features='lxml')
    human_tv = soup.find_all('section', attrs={'id': 'Human-Toxicity-Values'})
    nonhuman_tv = soup.find_all('section', attrs={'id': 'Non-Human-Toxicity-Values'})

    toxicity_dict['Human-Toxicity'] = \
        [ht.find_all('div', attrs={'class': 'section-content-item'})[0].find_all('p')[0].text for ht in human_tv]
    toxicity_dict['Non-Human-Toxicity'] = \
        [nht.find_all('div', attrs={'class': 'section-content-item'})[0].find_all('p')[0].text for nht in nonhuman_tv]

    return toxicity_dict
