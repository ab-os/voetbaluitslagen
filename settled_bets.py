import numpy as np
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from scrape_538 import clean_text
from urls import URLS_UNIB
import credentials  # <- Not for github!

# from scrape_unib import wait_for_page_ready, get_html

URL = "https://www.unibet.eu/betting/sports/bethistory/settled"


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

    return html


def show_more(driver):
    # Find show more button

    btn = driver.find_element_by_css_selector(
        "button.KambiBC-my-bets-summary__show-more-button"
    )
    while btn:
        break
        btn.click()
        wait_for_page_ready(driver)
        try:
            btn = driver.find_element_by_css_selector(
                "button.KambiBC-my-bets-summary__show-more-button"
            )
        except:
            btn = None


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

    # html = get_html(URL)

    # Read from temp file
    with open("tmp/my_bets.html", "r") as f:
        html = f.read()

    # Write html to temp file
    with open("tmp/my_bets.html", "w") as f:
        f.write(html)

    soup = BeautifulSoup(html, features="lxml")
    coupons = soup.select("li.KambiBC-my-bets-summary__item")

    # Extract info from each coupon
    for coupon in coupons:
        d = {}
        d["coupon-date"] = coupon.select_one(
            ".KambiBC-my-bets-summary__coupon-date"
        ).text
        d["status"] = coupon.select_one(".KambiBC-my-bets-summary__coupon-status").text
        fields = coupon.select(".KambiBC-my-bets-summary__field")
        assert len(fields) == 3
        d["label"] = fields[0].text
        d["stake"] = fields[
            1
        ].text  # Maybe cascade down to the value in .KambiBC-my-bets-summary__value
        d["odd"] = fields[2].text
        d["event-list-name"] = coupon.select_one(
            ".KambiBC-my-bets-summary-coupon__event-list-name"
        ).text
        d["cash-out"] = coupon.select_one(
            ".KambiBC-my-bets-summary-coupon__cash-out-wrapper"
        ).text

    print("E")
