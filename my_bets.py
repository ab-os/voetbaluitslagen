import numpy as np
import pandas as pd
import re
from pprint import pprint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_text
import credentials  # <- Not for github!
from scrape_unib import wait_for_page_ready


def show_more(driver):
    # Find and click the show more button
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
    # Accept cookies
    # driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()

    # Log in
    driver.find_element_by_css_selector("input[name=username]").send_keys(
        credentials.usr
    )
    driver.find_element_by_css_selector("input[name=password]").send_keys(
        credentials.pswd
    )
    driver.find_element_by_css_selector("button[data-test-name=btn-login]").click()


if __name__ == "__main__":
    # Skip browser action for debugging
    skip = True
    if not skip:
        # Open a browser
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get("https://www.unibet.eu/betting/sports/bethistory/")

        # Do all browser handling in a try-finally block
        try:
            wait_for_page_ready(driver)
            # Accept cookies
            driver.find_element_by_css_selector(
                "#CybotCookiebotDialogBodyButtonAccept"
            ).click()
            wait_for_page_ready(driver)
            login(driver)
            wait_for_page_ready(driver)
            show_more(driver)
            html = driver.page_source
        finally:
            driver.quit()

    # For debugging: write to or read from temporary source file
    # with open("tmp/my_bets.html", "w") as f:
    #    f.write(html)
    with open("tmp/my_bets.html", "r") as f:
        html = f.read()

    # Parse the html
    soup = BeautifulSoup(html, features="lxml")
    coupons = soup.select("li.KambiBC-my-bets-summary__item")

    # Extract info from each coupon
    l = []
    for coupon in coupons:
        d = {}
        d["coupon-date"] = coupon.select_one(
            ".KambiBC-my-bets-summary__coupon-date"
        ).text
        d["status"] = coupon.select_one(".KambiBC-my-bets-summary__coupon-status").text
        fields = coupon.select(".KambiBC-my-bets-summary__field")
        d["label"] = fields[0].text
        d["stake"] = fields[
            1
        ].text  # Maybe only use the value in .KambiBC-my-bets-summary__value
        d["odds"] = fields[2].text
        d["potential-payout"] = fields[3].text if len(fields) >= 4 else None
        d["event-list-name"] = coupon.select_one(
            ".KambiBC-my-bets-summary-coupon__event-list-name"
        ).text
        d["cash-out"] = coupon.select_one(
            ".KambiBC-my-bets-summary-coupon__cash-out-wrapper"
        ).text
        l.append(d)

    # Make a dataframe
    df = pd.DataFrame(l)

    # Data processing
    df.stake = df.stake.apply(lambda s: float(s.replace("Stake: €", "")))
    df.odds = df.odds.apply(
        lambda s: float(s.replace("Odds: ", "").replace("(", "").replace(")", ""))
    )
    df["cash-out"] = df["cash-out"].apply(
        lambda s: s.replace("Cash Out", "").replace("€", "")
    )
    teamnames = df["event-list-name"].str.split(" - ", expand=True)
    df["home-team"] = teamnames[0]
    df["away-team"] = teamnames[1]

    ### TODO:
    # Potential payout and payout in hetzelfde vakje?
    # Bepaal home-win, away-win of tie
    # Bereken cumulatieve payout

    print(df.shape)
    pprint(df.head())
    df.to_csv("my_bets_20200218.csv")
    print("End")
