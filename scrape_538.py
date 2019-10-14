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
    # "45%" to 0.45
    m = re.search("\d+", perc_str)
    return float(m.group()) / 100 if m else None


def clean_team_name(team_name):
    # "Atlético Madrid" to "atleticomadrid"
    return (
        unicodedata.normalize("NFKD", team_name)
        .encode(encoding="ascii", errors="ignore")
        .decode("utf-8")
        .lower()
        .replace(" ", "")
    )


def scrape_538(url, verbose=True):
    """Scrape one of the 538 pages. Returns a dataframe with the predictions."""

    # Request the page html
    page = requests.get(url)
    tree = html.fromstring(page.content)

    # See the page (for debugging)
    # with open("page.html", "w+") as f:
    #    f.write(str(page.content))

    # Extract all matches
    matches = tree.cssselect(".games-container.upcoming .match-container")

    # Extract useful info from every match
    l = []
    for match in matches:
        d = dict()
        # d["date"] = match.cssselect(".date div")[0].text   # The date is useless because it misses the year
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

    # Text cleaning
    df["home_team"] = df["home_team"].apply(clean_team_name)
    df["away_team"] = df["away_team"].apply(clean_team_name)

    if verbose:
        print('URL:', url)
        print("Number of matches found: ", len(matches))
        print('Shape:', df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    for url in URLS:
        scrape_538(url)
