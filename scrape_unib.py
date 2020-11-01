""" Scrape https://www.unibet.eu/betting/sports/filter/football for betting odds

Run this file to scrape all available odds for various soccer leagues. Results are stored in ./data/unib/

"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
import lxml.html
from time import sleep
from scrape_538 import clean_text


URLS_UNIB = [
    "https://www.unibet.eu/betting/sports/filter/football" + s
    for s in [
        # "/netherlands/eredivisie",
        # "/germany/bundesliga",
        # "/spain/la_liga",
        # "/england/premier_league",
        "/france/ligue_1",
        "/italy/serie_a",
    ]
]


def wait_for_page_ready(driver):
    # Why is conditional waiting so difficult...? Let's just sleep and check
    sleep(1)
    while driver.execute_script("return document.readyState") != "complete":
        sleep(1)
    sleep(1)


def get_html_from_url(url):
    # Open a webbrowser and return the html code
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(url)

    try:
        # Accept cookies - this is not needed I think
        # wait_for_page_ready(driver)
        # driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
        wait_for_page_ready(driver)
        html = driver.page_source
    finally:
        driver.quit()

    return html


def extract_info_from_html(html, verbose=True):
    # Debug? Open de html in de browser
    # lxml.html.open_in_browser(html)

    # Clean and open with lxml
    # clean_html = lxml.html.clean_html(html)
    doc = lxml.html.document_fromstring(html)

    # Find all matches, except the currently live matches
    # Class voor wedstrijddag .e385f
    # Class voor 1 wedstrijd .a9753
    # Class voor teamnamen .d74c2
    # Class voor de odds ._5a5c0
    matches = doc.cssselect(".e385f .a9753")

    if verbose:
        print("Number of matches found in html: ", len(matches))

    l = []
    for match in matches:
        d = {}
        try:
            # Date is missing sometimes :(
            d["date"] = match.find(class_="KambiBC-event-item__start-time--date").text
        except:
            d["date"] = None
        teams = match.cssselect(".d74c2")
        d["home_team"] = teams[0].text_content()
        d["away_team"] = teams[1].text_content()
        odds = match.cssselect("._5a5c0")
        # Odds are missing sometimes. Just skip the match then
        if not odds:
            continue
        d["odd_home_win"] = float(odds[0].text)
        d["odd_tie"] = float(odds[1].text)
        d["odd_away_win"] = float(odds[2].text)
        l.append(d)

    df = pd.DataFrame(l)

    # Cleaning
    df["home_team"] = df["home_team"].apply(clean_text)
    df["away_team"] = df["away_team"].apply(clean_text)
    return df


def scrape_unib(url, verbose=True):

    # Fire up a browser and actually scrape from the website
    html = get_html_from_url(url)

    # Extract information from the HTML code
    df = extract_info_from_html(html, verbose=verbose)

    df["url_unib"] = url

    if verbose:
        print("URL:", url)
        print("Shape:", df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    # Scrape all urls
    l = []
    for url in URLS_UNIB:
        l.append(scrape_unib(url, verbose=True))

    # Save results as 1 csv
    df = pd.concat(l)
    df.to_csv("./data/latest-scrape-unib.csv", index=False)
    print("Saved as: ./data/latest-scrape-unib.csv")
