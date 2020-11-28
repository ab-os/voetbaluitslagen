""" Scrape Unib for betting odds

Run this file to scrape all available odds for various soccer leagues. Results are stored in ./data/

"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
import lxml.html
from lxml.html.clean import Cleaner
from time import sleep
from scrape_538 import clean_team_names, get_league_from_url


URLS_UNIB = [
    "https://www.unibet.eu/betting/sports/filter/football" + s
    for s in [
        "/netherlands/eredivisie",
        "/germany/bundesliga",
        "/spain/la_liga",
        "/england/premier_league",
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


def get_htmls_from_urls(urls):
    # Initialize a webbrowser
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)

    # Loop over alle urls
    htmls = []
    try:
        for url in urls:
            # Browse to url
            driver.get(url)
            wait_for_page_ready(driver)

            # Accept cookies if not already done
            if not driver.get_cookie("CookieConsent"):
                # Cookie bar animation is slow
                sleep(10)
                #driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
                wait_for_page_ready(driver)

            # Get html code
            htmls.append(driver.page_source)
    finally:
        # Zorg dat de browser altijd wordt gesloten, zelfs bij een KeyboardInterrupt
        driver.quit()

    # Clean the html code to remove scripts and styling
    # Keep the forms because the odds are in buttons
    cleaner = Cleaner(forms=False)
    htmls = [cleaner.clean_html(h) for h in htmls]

    return htmls


def scrape_info_from_html(html, verbose=True):
    # Debug? Open de html in de browser
    # lxml.html.open_in_browser(html)

    # Find all matches
    doc = lxml.html.document_fromstring(html)
    matches = doc.cssselect("div.e385f div.a9753")

    if verbose:
        print("Number of matches found in html: ", len(matches))

    l = []
    for match in matches:
        # Skip live matches (has div with class _4f9f4 or f118a)
        if match.cssselect("div._4f9f4") or match.cssselect("div.f118a"):
            continue

        d = {}
        teams = match.cssselect("div.af24c")
        d["home_team"] = teams[0].text
        d["away_team"] = teams[1].text
        odds = match.cssselect("span._5a5c0")
        d["odd_home_win"] = float(odds[0].text)
        d["odd_tie"] = float(odds[1].text)
        d["odd_away_win"] = float(odds[2].text)
        l.append(d)

    df = pd.DataFrame(l)

    # Cleaning
    df["home_team"] = df["home_team"].apply(clean_team_names)
    df["away_team"] = df["away_team"].apply(clean_team_names)
    return df


if __name__ == "__main__":

    # Haal eerst de html code van elke website op
    htmls = get_htmls_from_urls(URLS_UNIB)

    # Pak info
    dfs = [scrape_info_from_html(h) for h in htmls]

    # Voeg elke league toe als kolom aan het dataframe
    [d.insert(0, "league", get_league_from_url(u)) for (d, u) in zip(dfs, URLS_UNIB)]

    # Save results as 1 csv
    df = pd.concat(dfs)
    df.to_csv("./data/latest-scrape-unib.csv", index=False)
    print("Saved as: ./data/latest-scrape-unib.csv")
