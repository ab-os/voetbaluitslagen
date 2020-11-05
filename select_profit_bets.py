import pandas as pd
import re
from datetime import date


# Map team names from 538 to those of unib
MAP = {
    # NL
    "twente": "fc_twente",
    "groningen": "fc_groningen",
    "psv": "psv_eindhoven",
    "heerenveen": "sc_heerenveen",
    "rkc": "rkc_waalwijk",
    "vvv-venlo": "vvv_venlo",
    "sparta": "sparta_rotterdam",
    "utrecht": "fc_utrecht",
    "heracles": "heracles_almelo",
    "emmen": "fc_emmen",
    # DE
    "schalke_04": "fc_schalke_04",
    "eintracht": "eintracht_frankfurt",
    "mainz": "mainz_05",
    "hoffenheim": "tsg_hoffenheim",
    "union_berlin": "1._fc_union_berlin",
    "gladbach": "borussia_monchengladbach",
    "dortmund": "borussia_dortmund",
    "wolfsburg": "vfl_wolfsburg",
    "leverkusen": "bayer_leverkusen",
    "bayern_munich": "bayern_munchen",
    "arminia": "arminia_bielefeld",
    # ES
    "barcelona": "fc_barcelona",
    "athletic_bilbao": "athletic_club_bilbao",
    "granada": "granada_cf",
    # EN
    "man._city": "manchester_city",
    "man._united": "manchester_united",
    "sheffield_utd": "sheffield_united",
    "brighton": "brighton_&_hove_albion",
    "leicester": "leicester_city",
    "wolves": "wolverhampton_wanderers",
    "newcastle": "newcastle_united",
    "west_brom": "west_bromwich",
    # # FR
    "psg": "paris_sg",
    "st_etienne": "saint-etienne",
    "dijon_fco": "dijon",
    "nimes": "nimes_olympique",
    # IT
    "verona": "hellas_verona",
    "inter_milan": "inter",
}


def select_profit_bets(df_538, df_unib, threshold):
    # Team names from 538 and unib are a different :(
    # print(set(df_538["home_team"]))
    # print(set(df_unib["home_team"]))
    df_538["home_team"].replace(MAP, inplace=True)
    df_538["away_team"].replace(MAP, inplace=True)

    # Check for unmatched team names
    no_match = set(df_unib.loc[:, ["home_team", "away_team"]].values.flatten()) ^ set(df_538.loc[:, ["home_team", "away_team"]].values.flatten())
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
