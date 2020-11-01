import pandas as pd
from scrape_538 import scrape_538, URLS_538
from scrape_unib import scrape_unib, URLS_UNIB
import re
from datetime import date


# Map team names from 538 to those of unib
MAP = {
    # NL
    "twente": "fctwente",
    "groningen": "fcgroningen",
    "psv": "psveindhoven",
    "heerenveen": "scheerenveen",
    "rkc": "rkcwaalwijk",
    "vvv-venlo": "vvvvenlo",
    "emmen": "fcemmen",
    "sparta": "spartarotterdam",
    "utrecht": "fcutrecht",
    "heracles": "heraclesalmelo",
    # DE
    "scpaderborn": "scpaderborn07",
    "schalke04": "fcschalke04",
    "eintracht": "eintrachtfrankfurt",
    "mainz": "mainz05",
    "hoffenheim": "tsghoffenheim",
    "unionberlin": "1.fcunionberlin",
    "gladbach": "borussiamonchengladbach",
    "dortmund": "borussiadortmund",
    "fortuna": "fortunadusseldorf",
    "wolfsburg": "vflwolfsburg",
    "leverkusen": "bayerleverkusen",
    "bayernmunich": "bayernmunchen",
    # ES
    "barcelona": "fcbarcelona",
    "athleticbilbao": "athleticclubbilbao",
    "granada": "granadacf",
    # EN
    "norwich": "norwichcity",
    "man.city": "manchestercity",
    "sheffieldutd": "sheffieldunited",
    "brighton": "brighton&hovealbion",
    "leicester": "leicestercity",
    "man.united": "manchesterunited",
    "wolves": "wolverhamptonwanderers",
    "newcastle": "newcastleunited",
    # FR
    "psg": "parissg",
    "stetienne": "saint-etienne",
    "dijonfco": "dijon",
    "nimes": "nimesolympique",
    # IT
    "verona": "hellasverona",
    "intermilan": "inter",
}


def select_profit_bets(df_538, df_unib, threshold):
    # Team names from 538 and unib are a different :(
    # print(set(df_538["home_team"]))
    # print(set(df_unib["home_team"]))
    df_538["home_team"].replace(MAP, inplace=True)
    df_538["away_team"].replace(MAP, inplace=True)

    # Check for unmatched team names
    no_match = (set(df_unib["home_team"]) | set(df_unib["away_team"])) - (
        set(df_538["home_team"]) | set(df_538["away_team"])
    )
    if no_match:
        print("No team name match found for:", no_match)

    # Now merge
    df = df_unib.merge(df_538, on=["home_team", "away_team"])

    # Calculate the expected value of each match outcome
    df.insert(3, "expected_home_win", df["prob_home_win"] * df["odd_home_win"])
    df.insert(4, "expected_tie", df["prob_tie"] * df["odd_tie"])
    df.insert(5, "expected_away_win", df["prob_away_win"] * df["odd_away_win"])

    # Select profitable matches: expectation value above threshold
    # Note: 1 match could give 2 bets
    df_0 = df[df["expected_home_win"] > threshold]
    df_0.insert(3, "bet_on", "home_win")
    df_1 = df[df["expected_tie"] > threshold]
    df_1.insert(3, "bet_on", "tie")
    df_2 = df[df["expected_away_win"] > threshold]
    df_2.insert(3, "bet_on", "away_win")
    df_selected = pd.concat([df_0, df_1, df_2])

    # Sort them by index, makes it easier to read
    df_selected.sort_index(inplace=True)
    print(df_selected.shape)
    print(df_selected)
    return df_selected


if __name__ == "__main__":

    # Lezen van CSV die al gescraped zijn
    df_538 = pd.read_csv("./data/latest-scrape-538.csv")
    df_unib = pd.read_csv("./data/latest-scrape-unib.csv")
    df_selected = select_profit_bets(df_538, df_unib, 1.1)

    print(df_selected.head())
    print()
