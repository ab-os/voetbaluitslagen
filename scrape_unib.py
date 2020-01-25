""" Scrape https://www.unibet.eu/betting/sports/filter/football for betting odds

Run this file to scrape all available odds for various soccer leagues. Results are stored in ./data/unib/

"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_text


URLS_UNIB = [
    "https://www.unibet.eu/betting/sports/filter/football" + s
    for s in ["/netherlands", "/germany", "/spain", "/england", "/france", "/italy"]
]


def wait_for_page_ready(driver):
    # Why is waiting so difficult...? Let's just wait and sleep
    sleep(1)
    while driver.execute_script("return document.readyState") != "complete":
        sleep(1)
    sleep(1)


def get_html_from_url(url):
    # Open a webbrowser, visit Unib and return the html code
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
    # Load with bs4
    soup = BeautifulSoup(html, features="lxml")

    # Find all matches, except the currently live matches
    matches = soup.select(
        ".KambiBC-event-groups li.KambiBC-event-item:not(.KambiBC-event-item--live)"
    )

    if verbose:
        print("Number of matches found in html: ", len(matches))

    l = []
    for match in matches:
        d = {}
        try:
            # Date is missing sometimes :/
            d["date"] = match.find(class_="KambiBC-event-item__start-time--date").text
        except:
            d["date"] = None
        teams = match.find_all(class_="KambiBC-event-participants__name")
        d["home_team"] = teams[0].text
        d["away_team"] = teams[1].text
        odds = match.find_all(class_="KambiBC-mod-outcome__odds")
        d["odd_home_win"] = float(odds[0].text)
        d["odd_tie"] = float(odds[1].text)
        d["odd_away_win"] = float(odds[2].text)
        l.append(d)

    df = pd.DataFrame(l)

    # Cleaning
    df["home_team"] = df["home_team"].apply(clean_text)
    df["away_team"] = df["away_team"].apply(clean_text)
    return df


def scrape_unib(url, verbose=True, read_from_html=None, write_to_html=None):
    # Use the read_from and write_to for debugging and not having to load the website in Firefox

    if read_from_html:
        # If this happens url is completely ignored
        with open(read_from_html, "r") as f:
            html = f.read()
    else:
        # Fire up a browser and extract the html code
        html = get_html_from_url(url)

    if write_to_html:
        # Store now for debugging later
        with open(write_to_html, "w") as f:
            f.write(html)
            print("Html saved to:", write_to_html)

    # Extract information from the HTML code
    df = extract_info_from_html(html, verbose=verbose)

    if verbose:
        print("URL:", url)
        print("Shape:", df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    # Run for 1 or more specific URLS
    urls = URLS_UNIB[:]

    for url in urls:
        # Now choose to write to a html file or read from one or just scrape
        # args = {"write_to_html": "data/unib/" + re.split(r"/", url)[-1] + ".html"}
        args = {"read_from_html": "data/unib/" + re.split(r"/", url)[-1] + ".html"}
        # args = {}

        df = scrape_unib(url, verbose=True, **args)
        df.to_csv("data/unib/" + re.split(r"/", url)[-1] + ".csv")
        print("Saved as: data/unib/" + re.split(r"/", url)[-1] + ".csv")
