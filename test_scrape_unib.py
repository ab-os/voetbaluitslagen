""" Scrape https://www.unibet.eu/betting/sports/filter/football for betting odds

Run this file to scrape all available odds for various soccer leagues. Results are stored in ./data/unib/

"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
import lxml.html
from time import sleep
from pathlib import Path
from scrape_538 import clean_text
from scrape_unib import wait_for_page_ready, get_html_from_url, extract_info_from_html, scrape_unib

URLS_UNIB = [
    "https://www.unibet.eu/betting/sports/filter/football" + s
    for s in [
        # "/netherlands/eredivisie",
        # "/germany/bundesliga",
        "/spain/la_liga",
        # "/england/premier_league",
        # "/france/ligue_1",
        # "/italy/serie_a",
    ]
]


def download_page_as_local_html_file(url):

    # Scrape from online
    html = get_html_from_url(url)
    
    filepath = Path(f"./data/html/unib-{get_league_from_url(url)}.html")
    with open(filepath, "w") as f:
        f.write(html)


def read_from_local_html_file(url):
    filepath = Path(f"./data/html/unib-{get_league_from_url(url)}.html")
    with open(filepath, "r") as f:
        html = f.read()
    return html


def get_league_from_url(url):
    return url.split('/')[-1]


if __name__ == "__main__":
    # Scrape all urls
    l = []
    for url in URLS_UNIB:
        
        # Open een browser en download de html code 
        # Doe dit maar 1 keer en lees de volgende keren van het lokale bestand
        # download_page_as_local_html_file(url)

        # Read from html file
        html = read_from_local_html_file(url)

        # Get info
        df = extract_info_from_html(html, verbose=True)
        l.append(df)
        
    df = pd.concat(l)
    print(df.head())
