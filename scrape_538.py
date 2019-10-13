"""Scraper for https://projects.fivethirtyeight.com/soccer-predictions/

"""

from lxml import html
from lxml.cssselect import CSSSelector
import requests
import re
import pandas as pd
import unicodedata

# Global constants
URLS = [
    "https://projects.fivethirtyeight.com/soccer-predictions/" + s
    for s in [
        "eredivisie/",
        "bundesliga/",
        "la-liga/",
        "premier-league/",
        "ligue-1/",
        "serie-a/",
    ]
]


def percentage_string_to_float(perc_str):
    # "45%"" to 0.45
    m = re.search("\d+", perc_str)
    return float(m.group()) / 100 if m else None


def clean_team_name(team_name):
    team_name = team_name.lower()
    unicodedata.normalize("NFKD", team_name)
    team_name = team_name.encode(encoding="ascii", errors="ignore")
    team_name = team_name.decode("utf-8")
    return team_name


def has_duplicate_3_letter_codes(list_of_team_names):
    unique_team_names = set(list_of_team_names)
    team_codes = [name for name in unique_team_names]
    return len(team_codes) != len(set(team_codes))


def team_name_to_team_code(team_name):
    team_code = team_name.replace(" ", "")
    team_code = team_code[:5]
    return team_code


def scrape_538(url, verbose=True):
    """Scrape one of the 538 pages. Returns a dataframe with the predictions."""

    page = requests.get(url)
    tree = html.fromstring(page.content)

    # Debugging
    # with open("page.html", "w+") as f:
    #    f.write(str(page.content))

    # Extract matches
    matches = tree.cssselect(".games-container.upcoming .match-container")
    print("Number of matches found: ", len(matches)) if verbose else None

    # Extract info from every match
    l = []
    for match in matches:
        d = dict()
        d["date"] = match.cssselect(".date div")[0].text
        d["home_team"] = match.cssselect(".match-top .name")[0].text
        d["home_win"] = match.cssselect(".match-top .prob")[0].text
        d["tie"] = match.cssselect(".tie-prob div")[0].text
        d["away_team"] = match.cssselect(".match-bottom .name")[0].text
        d["away_win"] = match.cssselect(".match-bottom .prob")[0].text
        l.append(d)

    df = pd.DataFrame(l)

    # Data processing
    df["home_win"] = df["home_win"].apply(percentage_string_to_float)
    df["tie"] = df["tie"].apply(percentage_string_to_float)
    df["away_win"] = df["away_win"].apply(percentage_string_to_float)

    # The date column is useless because it misses the year
    del df["date"]

    # Text cleaning
    df["home_team"] = df["home_team"].apply(clean_team_name)
    df["away_team"] = df["away_team"].apply(clean_team_name)

    # Make 3-letter codes
    df["home_code"] = df["home_team"].apply(team_name_to_team_code)
    df["away_code"] = df["away_team"].apply(team_name_to_team_code)

    # Unique team names and team codes should match
    assert len(set(df["home_team"])) == len(set(df["home_code"]))

    if verbose:
        print(df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    for url in URLS:
        scrape_538(url)
