import numpy as np
import pandas as pd
import re
from pprint import pprint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import lxml.html
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_team_names
import credentials  # <- Not for github!
from scrape_unib import wait_for_page_ready


def show_more(driver):
    # Find and click the Show more button until all is shown
    while True:
        try:
            btn = driver.find_element_by_css_selector(
                "button.KambiBC-my-bets-summary__show-more-button"
            )
            btn.click()
            wait_for_page_ready(driver)
        except NoSuchElementException:
            # Done
            break


def login(driver):
    # Log in
    driver.find_element_by_css_selector("input[name=username]").send_keys(
        credentials.usr
    )
    driver.find_element_by_css_selector("input[name=password]").send_keys(
        credentials.pswd
    )
    driver.find_element_by_css_selector("button[data-test-name=btn-login]").click()

    
def download_my_bets():
    # Open a browser
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("https://www.unibet.eu/betting/sports/bethistory/")

    # Accept cookies if not already done
    if False: #not driver.get_cookie("CookieConsent"):
        # Cookie bar animation is slow
        sleep(10)
        driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
        wait_for_page_ready(driver)

    # Do all browser handling in a try-finally block
    try:
        wait_for_page_ready(driver)
        login(driver)
        wait_for_page_ready(driver)
        show_more(driver)
        html = driver.page_source
    finally:
        driver.quit()
    
    # Clean
    html = lxml.html.clean.clean_html(html)

    return html


def scrape_info_from_html(html):
        # Parse the html
    doc = lxml.html.document_fromstring(html)
    coupons = doc.cssselect("li.KambiBC-my-bets-summary__item")

    # Extract info from each coupon
    # fmt: off
    l = []
    for coupon in coupons:
        d = {}
        d["coupon-date"] = coupon.cssselect("span.KambiBC-my-bets-summary__coupon-date")[0].text
        d["status"] = coupon.cssselect("span.KambiBC-my-bets-summary__coupon-status")[0].text
        
        # Various fields with the same class
        fields = coupon.cssselect("""
            div.KambiBC-my-bets-summary__field > 
            span.KambiBC-my-bets-summary__value
        """)
        d["bet-on"] = fields[0].text
        d["stake"] = fields[1].text
        d["odds"] = fields[2].text
        d["coupon-id"] = fields[3].text

        d["event-list-name"] = coupon.cssselect(".KambiBC-my-bets-summary-coupon__event-list-name")[0].text

        # Info alleen relevant voor open bets
        if d['status'] == "Open":
            d["potential-payout"] = fields[4].text
            d["cash-out"] = coupon.cssselect("span.KambiBC-react-cash-out-button__value > span")[1].text

        # Info alleen relevant voor gesloten bets
        if d['status'] in ("Won", "Void", "Cash Out confirmed"):
            d['payout'] = coupon.cssselect("span.KambiBC-my-bets-summary-payout__value")[0].text
        
        l.append(d)

    # Make a dataframe
    return pd.DataFrame(l)


def data_prep(df):
    for c in ("stake", "odds", "cash-out", "potential-payout", "payout"):
        df[c] = df[c].apply(get_float_from_string)
    
    teamnames = df["event-list-name"].str.split(" - ", expand=True)
    df["home-team"] = teamnames[0]
    df["away-team"] = teamnames[1]
    return df


def get_float_from_string(s):
    # €3.45 to 3.45
    # (2.34) to 2.34
    m = re.search(r"\d+\.\d+", str(s))
    if m:
        return float(m.group(0))
    else:
        return None


if __name__ == "__main__":
    # Open a browser and download the website with my bets
    html = download_my_bets()

    # Scrape useful info
    df = scrape_info_from_html(html)

    # Data preparation
    df = data_prep(df)

    # Done & save
    print(df.shape)
    print(df.head())
    df.to_csv("./data/my_bets.csv")
