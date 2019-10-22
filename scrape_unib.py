import numpy as np
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_team_name
from urls import URLS_UNIB
import credentials


def wait_for_page_ready(driver):
    # Why is waiting so difficult...?
    sleep(1)
    while driver.execute_script("return document.readyState") != "complete":
        sleep(1)
    sleep(1)


def get_html(url):
    """Open a webbrowser, visit Unib and return the html code."""

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(url)

    try:
        # Accept cookies
        # driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()

        wait_for_page_ready(driver)
        html = driver.page_source
    finally:
        driver.quit()
    
    return html


def extract_info_from_html(html, verbose=True):

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
        d["date"] = match.find(class_="KambiBC-event-item__start-time--date").text
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
    df["home_team"] = df["home_team"].apply(clean_team_name)
    df["away_team"] = df["away_team"].apply(clean_team_name)
    return df


def scrape_unib(url, verbose=True, read_from_html=None, write_to_html=None):
    # Use the read_from and write_to for debugging and not having to load the website in a browser

    if not read_from_html:
        html = get_html(url)

    if read_from_html:
        # If this happens url is completely ignored
        with open(read_from_html, "r") as f:
            html = f.read()

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
    # It's only tests here

    # Run for 1 or more specific URLS
    for i in [0]:
        scrape_unib(URLS_UNIB[i], write_to_html="tmp/page_" + str(i) + ".html")
        #scrape_unib(None, read_from_html="tmp/page_" + str(i) + ".html")
