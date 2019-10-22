from lxml import html
import requests
import re
import pandas as pd
import unicodedata
from urls import URLS_538


def convert_percentage_string_to_float(perc_str):
    # "45%" to 0.45
    # "<1%" to 0.01
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
        .replace("\n", "")
    )


def scrape_538(url, verbose=True):
    """Scrape one of the 538 pages. Returns a dataframe with the match predictions."""

    # Request the page html
    page = requests.get(url)
    tree = html.fromstring(page.content)

    # For debugging: Write the html to a file so you can view it in a browser
    # with open("tmp/page_538.html", "w") as f:
    #    f.write(str(page.content))

    # Extract all matches
    matches = tree.cssselect(".games-container.upcoming .match-container")

    # Extract useful info for every match
    l = []
    for match in matches:
        d = dict()
        d["date"] = match.cssselect(".date div")[0].text
        d["home_team"] = match.cssselect(".match-top .name")[0].text
        d["prob_home_win"] = match.cssselect(".match-top .prob")[0].text
        d["prob_tie"] = match.cssselect(".tie-prob div")[0].text
        d["away_team"] = match.cssselect(".match-bottom .name")[0].text
        d["prob_away_win"] = match.cssselect(".match-bottom .prob")[0].text
        l.append(d)

    df = pd.DataFrame(l)

    # Data processing
    df["prob_home_win"] = df["prob_home_win"].apply(convert_percentage_string_to_float)
    df["prob_tie"] = df["prob_tie"].apply(convert_percentage_string_to_float)
    df["prob_away_win"] = df["prob_away_win"].apply(convert_percentage_string_to_float)
    df["home_team"] = df["home_team"].apply(clean_team_name)
    df["away_team"] = df["away_team"].apply(clean_team_name)

    if verbose:
        print("URL:", url)
        print("Number of matches found: ", len(matches))
        print("Shape:", df.shape)
        print(df.head())

    return df


if __name__ == "__main__":
    # It's only tests here

    # Scrape all URLS
    for url in URLS_538:
        scrape_538(url)
