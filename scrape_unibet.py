"""Scraper for https://www.unibet.eu/"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_team_name

# Globals
URLS = [
    "https://www.unibet.eu/betting#filter/football/" + s
    for s in [
        "netherlands/eredivisie",
        "spain/la_liga",
        "germany/bundesliga",
        "england/premier_league",
        "france/ligue_1",
        "italy/serie_a",
    ]
]


def pause():
    # TODO: Maybe randomize the duration
    sleep(2)


def get_page_html(url):
    """Uses a webbrowser and returns the html code."""

    browser = webdriver.Firefox()
    browser.get(url)

    # Wait until the accept-cookies button is present
    element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept"))
    )
    pause()
    element.click()
    pause()

    # Find the dropdown bars, NOT the already expanded one
    dropdowns = browser.find_elements_by_css_selector(
        ".KambiBC-event-groups .KambiBC-collapsible-container:not(.KambiBC-expanded)"
    )

    # Click on them
    for dropdown in dropdowns:
        dropdown.click()
        pause()

    # Now get the beautiful source code
    html = browser.page_source

    # quit the browser
    browser.quit()

    return html


# The read_from and write_to are useful for debugging and not having to load the website
def scrape_unibet(url, verbose=True, read_from_html=None, write_to_html=None):
       
    if read_from_html:
        # Ignores url
        with open(read_from_html, 'r') as f:
            html = f.read()
    else:
        # Open a webbrowser, do some interaction and get the html
        html = get_page_html(url)

        # Store now for debugging later
        if write_to_html:
            with open(write_to_html,'w+') as f:
                f.write(html)


    soup = BeautifulSoup(html)

    # Find all matches
    matches = soup.find(class_="KambiBC-event-groups").find_all(
        "li", class_="KambiBC-event-item"
    )

    l = []
    for match in matches:
        d = {}
        #d["date"] = match.find(class_="KambiBC-event-item__start-time--date").text # <- Doesnt work..?
        teams = match.find_all(class_="KambiBC-event-participants__name")
        d["home_team"] = teams[0].text
        d["away_team"] = teams[1].text
        odds = match.find_all(class_="KambiBC-mod-outcome__odds")
        d["odd_home_win"] = float(odds[0].text)
        d["odd_tie"] = float(odds[1].text)
        d["odd_away_win"] = float(odds[2].text)
        
        # Add to the list
        l.append(d)

    df = pd.DataFrame(l)

    # Cleaning
    df["home_team"] = df["home_team"].apply(clean_team_name)
    df["away_team"] = df["away_team"].apply(clean_team_name)

  
    # # Change the team names so that they match the ones in the 538 data frame
    # changes_nl = {
    #     "fc groningen": "groningen",
    #     "fc twente": "twente",
    #     "sc heerenveen": "heerenveen",
    #     "fc utrecht": "utrecht",
    #     "fc emmen": "emmen",
    # }
    # changes_de = {
    #     "bayer leverkusen": "leverkusen",
    #     "borussia monchengladbach": "gladbach",
    #     "vfl wolfsburg": "wolfsburg",
    #     "borussia dortmund": "dortmund",
    #     "augsburg": "fc ausburg",
    # }
    # changes_es = {"deportiva las palmas": "las palmas", "fc barcelona": "barcelona"}
    # changes_en = {}
    # changes_fr = {"saint-etienne": "st etienne", "paris sg": "psg"}
    # changes_it = {"hellas verona": "verona"}
    # changes = {
    #     **changes_nl,
    #     **changes_de,
    #     **changes_es,
    #     **changes_en,
    #     **changes_fr,
    #     **changes_it,
    # }
    # for old, new in changes.items():
    #     # Replace!
    #     df["home_team"] = df["home_team"].str.replace(old, new)
    #     df["away_team"] = df["away_team"].str.replace(old, new)

    # Show
    if verbose:
        print('URL:', url)
        print("Number of matches found: ", len(matches))
        print('Shape:', df.shape)
        print(df.head())


def write_all_urls_to_htmls():
    for i in range(len(URLS)):
        scrape_unibet(URLS[i], write_to_html='tmp/page' + str(i) + '.html')



if __name__ == "__main__":
    
    # Run one
    scrape_unibet(URLS[2], write_to_html='tmp/page_2.html')

    # Run for all URLS
    #write_all_urls_to_htmls()
