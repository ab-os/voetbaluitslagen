""" Scrape https://projects.fivethirtyeight.com for football predictions

Run this file to scrape all available predictions for various leagues. Results are stored in ./data/538/scrape-latest.csv

"""

import lxml.html
import requests
import re
import pandas as pd
import unicodedata


URLS_538 = [
    "https://projects.fivethirtyeight.com/soccer-predictions" + s
    for s in [
        "/eredivisie",
        "/bundesliga",
        "/la-liga",
        "/premier-league",
        "/ligue-1",
        "/serie-a",
    ]
]


def convert_percentage_string_to_float(perc_str):
    # "45%" to 0.45
    # "<1%" to 0.01
    m = re.search("\d+", perc_str)
    return float(m.group()) / 100 if m else None


def clean_text(text):
    # "Atlético Madrid" to "atletico_madrid"
    return (
        unicodedata.normalize("NFKD", text)
        .encode(encoding="ascii", errors="ignore")
        .decode("ascii")
        .lower()
        .replace(" ", "_")
    )

def get_league_from_url(url):
    return url.split("/")[-1]



def scrape_538(url, verbose=True):
    """Scrape one of the 538 pages. Returns a dataframe with the match predictions."""

    # Get the page html
    # https://docs.python-guide.org/scenarios/scrape/
    page = requests.get(url)
    tree = lxml.html.document_fromstring(page.content)

    # For debugging: View it in a browser
    # lxml.html.open_in_browser(tree)

    # Extract all matches
    matches = tree.cssselect(".games-container.upcoming .match-container")

    # Extract useful info for every match
    l = []
    for match in matches:
        d = dict()
        d["date"] = match.cssselect(".date div")[0].text
        d["home_team"] = match.cssselect(".match-top .name")[0].text
        d["away_team"] = match.cssselect(".match-bottom .name")[0].text
        d["prob_home_win"] = match.cssselect(".match-top .prob")[0].text
        d["prob_tie"] = match.cssselect(".tie-prob div")[0].text
        d["prob_away_win"] = match.cssselect(".match-bottom .prob")[0].text
        l.append(d)

    df = pd.DataFrame(l)

    # Data processing
    df["prob_home_win"] = df["prob_home_win"].apply(convert_percentage_string_to_float)
    df["prob_tie"] = df["prob_tie"].apply(convert_percentage_string_to_float)
    df["prob_away_win"] = df["prob_away_win"].apply(convert_percentage_string_to_float)
    df["home_team"] = df["home_team"].apply(clean_text)
    df["away_team"] = df["away_team"].apply(clean_text)

    # Add the website url as a static column
    df["league"] = get_league_from_url(url)

    if verbose:
        print("URL:", url)
        print("Number of matches found: ", len(matches))
        print("Shape:", df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    # Scrape all URLS
    l = []
    for url in URLS_538:
        l.append(scrape_538(url, verbose=True))

    df = pd.concat(l)
    df.to_csv("./data/latest-scrape-538.csv", index=False)
    print("Saved as: ./data/latest-scrape-538.csv")
