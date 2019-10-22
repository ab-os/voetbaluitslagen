import pandas as pd
from selenium import webdriver
import credentials
from scrape_538 import scrape_538, URLS_538, clean_team_name
from scrape_unib import scrape_unib, URLS_UNIB, wait_for_page_ready
from select_profit_bets import select_profit_bets

# Global constants
THRESHOLD = 1.1
AMOUNT_EURO = 0.5


def login(driver):
    # Accept cookies
    #driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()

    # Log in
    driver.find_element_by_css_selector("input[name=username]").send_keys(
        credentials.usr
    )
    driver.find_element_by_css_selector("input[name=password]").send_keys(
        credentials.pswd
    )
    driver.find_element_by_css_selector("button[data-test-name=btn-login]").click()


def find_all_matches(driver):
    matches = driver.find_elements_by_css_selector(".KambiBC-event-groups li.KambiBC-event-item:not(.KambiBC-event-item--live)")

    matches_teams = [m.find_element_by_css_selector(".KambiBC-event-participants").text for m in matches]
    matches_teams = [clean_team_name(mt) for mt in matches_teams]
    matches_teams.index("willemiirkcwaalwijk")
    matches[1].find_element_by_css_selector("button.KambiBC-mod-outcome").click()

    return matches



if __name__ == "__main__":

    # Scrape and select the matches I want to bet on
    i = 0
    df_538 = scrape_538(URLS_538[i], verbose=False)
    df_unib = scrape_unib(
        None, read_from_html="tmp/page_" + str(i) + ".html", verbose=False
    )
    df_selected = select_profit_bets(df_538, df_unib, THRESHOLD)

    # Open the browser, login and place some bets!
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(URLS_UNIB[i])

    try:
        wait_for_page_ready(driver)
        #login(driver)
        wait_for_page_ready(driver)
        find_all_matches(driver)

    finally:
        driver.quit()

