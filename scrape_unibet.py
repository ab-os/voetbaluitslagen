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

# Globals
URLS = [
    "https://www.unibet.eu/betting#filter/football/" + s
    for s in [
        "netherlands/eredivisie",
        "spain/laliga",
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
    """Returns soup"""

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


def scrape_unibet(url, verbose=True):

    print("Going to:", url) if verbose else None
    
    # For debugging
    DONT_SCRAPE = True
    
    if DONT_SCRAPE:
        with open('tmp/page.html', 'r') as f:
            html = f.read()
    else:
        # Open a webbrowser, do some interaction and get the html
        html = get_page_html(url)

        # Store now for debugging?
        with open('tmp/page.html','w+') as f:
            f.write(html)


    soup = BeautifulSoup(html)

    # search for matches in the soup
    matches = soup.find(class_="KambiBC-event-groups").find_all(
        "li", class_="KambiBC-event-item"
    )

    # print amount found. Also remember this amount for getting the same amout from 538
    numberOfMatches = len(matches)
    print("Number of matches found: ", numberOfMatches)

    # Create empty list
    jobs = []

    for match in matches:
        # Create empty dictionary
        job = {}

        # Find info on the page
        # job["date"] = match.find(class_="KambiBC-event-item__start-time--date").text # <- Doesnt work..?
        teams = match.find_all(class_="KambiBC-event-participants__name")
        job["home_team"] = teams[0].text
        job["away_team"] = teams[1].text
        odds = match.find_all(class_="KambiBC-mod-outcome__odds")
        job["odd_home_win"] = odds[0].text
        job["odd_tie"] = odds[1].text
        job["odd_away_win"] = odds[2].text

        # Add to the list
        jobs.append(job)

    dfOdds = pd.DataFrame(jobs)

    # Show
    # dfOdds

    # Change team names to lowercase
    dfOdds["home_team"] = dfOdds["home_team"].str.lower()
    dfOdds["away_team"] = dfOdds["away_team"].str.lower()

    # Remove all accents
    dfOdds["home_team"] = (
        dfOdds["home_team"]
        .str.normalize("NFKD")
        .str.encode(encoding="ascii", errors="ignore")
        .str.decode("utf-8")
    )
    dfOdds["away_team"] = (
        dfOdds["away_team"]
        .str.normalize("NFKD")
        .str.encode(encoding="ascii", errors="ignore")
        .str.decode("utf-8")
    )

    # Change the team names so that they match the ones in the 538 data frame
    changes_nl = {
        "fc groningen": "groningen",
        "fc twente": "twente",
        "sc heerenveen": "heerenveen",
        "fc utrecht": "utrecht",
        "fc emmen": "emmen",
    }
    changes_de = {
        "bayer leverkusen": "leverkusen",
        "borussia monchengladbach": "gladbach",
        "vfl wolfsburg": "wolfsburg",
        "borussia dortmund": "dortmund",
        "augsburg": "fc ausburg",
    }
    changes_es = {"deportiva las palmas": "las palmas", "fc barcelona": "barcelona"}
    changes_en = {}
    changes_fr = {"saint-etienne": "st etienne", "paris sg": "psg"}
    changes_it = {"hellas verona": "verona"}
    changes = {
        **changes_nl,
        **changes_de,
        **changes_es,
        **changes_en,
        **changes_fr,
        **changes_it,
    }
    for old, new in changes.items():
        # Replace!
        dfOdds["home_team"] = dfOdds["home_team"].str.replace(old, new)
        dfOdds["away_team"] = dfOdds["away_team"].str.replace(old, new)

    # Make 3-letter code names
    dfOdds["home_code"] = dfOdds["home_team"].str[:3]
    dfOdds["away_code"] = dfOdds["away_team"].str[:3]

    # Convert to numbers
    dfOdds["odd_home_win"] = pd.to_numeric(dfOdds["odd_home_win"])
    dfOdds["odd_away_win"] = pd.to_numeric(dfOdds["odd_away_win"])
    dfOdds["odd_tie"] = pd.to_numeric(dfOdds["odd_tie"])

    # Show
    dfOdds


if __name__ == "__main__":
    scrape_unibet(URLS[0])
