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
from scrape_538 import get_league_from_url
from scrape_unib import wait_for_page_ready, get_htmls_from_urls, scrape_info_from_html, URLS_UNIB


def download_pages(urls, paths):

    # Scrape from online
    htmls = get_htmls_from_urls(urls)

    for (h, p) in zip(htmls, paths):
        # Wegschrijven
        with open(p, "w") as f:
            f.write(h)


if __name__ == "__main__":

    # Html local storage location
    html_filenames = [
        f"./data/html/unib-{get_league_from_url(u)}.html" for u in URLS_UNIB
    ]

    # Download pages en opslaan as html file
    # Comment als dit niet meer hoeft te gebeuren
    # download_pages(URLS_UNIB, html_filenames)

    # Inlezen html bestanden
    htmls = []
    for html_filename in html_filenames:
        with open(html_filename, "r") as f:
            print(f"Reading {html_filename}...")
            h = f.read()
            htmls.append(h)

    # Pak info
    dfs = [scrape_info_from_html(h) for h in htmls]

    # Voeg elke url toe als kolom aan het dataframe
    [d.insert(0, "league", get_league_from_url(u)) for (d, u) in zip(dfs, URLS_UNIB)]

    df = pd.concat(dfs)
    print(len(df))
    print(df.head())
