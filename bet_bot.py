import pandas as pd
import re
from time import sleep
from selenium import webdriver
from scrape_538 import scrape_538, URLS_538, clean_text
from scrape_unib import scrape_unib, URLS_UNIB, wait_for_page_ready
from select_profit_bets import select_profit_bets
import credentials  # <- Not for github!

# Global constants
THRESHOLD = 1.1
AMOUNT_EURO = 0.1


def login(driver):
    # Log in
    driver.find_element_by_css_selector("input[name=username]").send_keys(
        credentials.usr
    )
    sleep(1)
    driver.find_element_by_css_selector("input[name=password]").send_keys(
        credentials.pswd
    )
    sleep(1)
    driver.find_element_by_css_selector("button[data-test-name=btn-login]").click()


def find_all_matches(driver):
    elem_matches = driver.find_elements_by_css_selector(
        ".KambiBC-event-groups li.KambiBC-event-item:not(.KambiBC-event-item--live)"
    )

    team_names = [
        m.find_element_by_css_selector(".KambiBC-event-participants").text
        for m in elem_matches
    ]

    # Separate team names with "-"
    team_names = [mt.replace("\n", "-") for mt in team_names]
    team_names = [clean_text(mt) for mt in team_names]

    # Construct dictionary with the webpage elements
    d = dict(zip(team_names, elem_matches))
    return d


def place_bets(driver, df_selected, d_matches):

    # Combine team names
    df_selected["team_names"] = df_selected["home_team"] + "-" + df_selected["away_team"]

    # Search first bet
    for (team_names, bet_on) in zip(df_selected["team_names"], df_selected["bet_on"]):

        #
        elem_match = d_matches[team_names]

        elem_buttons = elem_match.find_elements_by_css_selector(".KambiBC-bet-offer button")
        
        # Scroll the buttons into view
        # Dont use location_once_scrolled_into_view because it may change without warning
        # https://selenium-python.readthedocs.io/api.html#selenium.webdriver.remote.webelement.WebElement.location_once_scrolled_into_view
        sleep(1)
        driver.execute_script("return arguments[0].scrollIntoView();", elem_buttons[0])
        sleep(1)
        driver.execute_script("window.scrollBy(0, -150);")
        sleep(1)

        if bet_on == "home_win":
            elem_buttons[0].click()
        elif bet_on == "tie":
            elem_buttons[1].click()
        elif bet_on == "away_win":
            elem_buttons[2].click()
        else:
            raise Exception("Unknown bet_on value")
        sleep(1)
        elem_betslip = driver.find_element_by_css_selector("input.mod-KambiBC-stake-input")
        elem_betslip.send_keys(str(AMOUNT_EURO))
        sleep(1)

        # Place bet
        driver.find_element_by_css_selector("button.mod-KambiBC-betslip__place-bet-btn").click()
        print("Bet placed:", team_names, bet_on)
        sleep(1)

        # Close the betslip
        driver.find_element_by_css_selector("button.mod-KambiBC-betslip-receipt__close-button").click()
        sleep(1)


    return 0



if __name__ == "__main__":

    # Scrape and select the matches I want to bet on
    i = 1
    url_538 = URLS_538[i]
    url_unib = URLS_UNIB[i]

    df_538 = scrape_538(url_538, verbose=True)
    df_unib = scrape_unib(
        url_unib,
        read_from_html=None, #"data/unib/" + re.split(r"/", url_unib)[-1] + ".html",
        verbose=True,
    )
    df_selected = select_profit_bets(df_538, df_unib, THRESHOLD)

    if df_selected.empty:
        raise Exception()

    # Open the browser, login and place some bets!
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(url_unib)

    # try:
    wait_for_page_ready(driver)

    # Accept cookies
    driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()

    wait_for_page_ready(driver)
    login(driver)
    wait_for_page_ready(driver)
    d_matches = find_all_matches(driver)

    place_bets(driver, df_selected, d_matches)

    # finally:
    driver.quit()
