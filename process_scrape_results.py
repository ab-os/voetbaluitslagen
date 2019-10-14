

# # Merge
# First check if team names are missed in the data transformation




def has_duplicate_3_letter_codes(list_of_team_names):
    unique_team_names = set(list_of_team_names)
    team_codes = [name for name in unique_team_names]
    return len(team_codes) != len(set(team_codes))


def team_name_to_team_code(team_name):
    team_code = team_name.replace(" ", "")
    team_code = team_code[:5]
    return team_code



    # Make 3-letter codes
    df["home_code"] = df["home_team"].apply(team_name_to_team_code)
    df["away_code"] = df["away_team"].apply(team_name_to_team_code)

    # Unique team names and team codes should match
    assert len(set(df["home_team"])) == len(set(df["home_code"]))



# check for missing matches for Unibet
dfCheck = df538.merge(dfOdds, how="outer", on=["home_code", "away_code"], indicator=True)
dfCheck[dfCheck._merge != 'both']


# Merge by 3-letter codes
dfMerge = df538.merge(dfOdds, how="inner", on=["home_code", "away_code"], suffixes=('', '_uni'))

# print
print('Number of matches succesfully merged:', len(dfMerge))

# # Analyse

# Calculate the expected profits for win, tie and loss
dfMerge["expect_home"] = dfMerge["home_win"] * dfMerge["odd_home_win"]
dfMerge["expect_away"] = dfMerge["away_win"] * dfMerge["odd_away_win"]
dfMerge["expect_tie"] = dfMerge["tie"] * dfMerge["odd_tie"]

# Set threshold
threshold = 1.2

# Show
theGames = dfMerge.query('expect_home>@threshold or expect_away>@threshold or expect_tie>@threshold')                    [["date", "home_team", "away_team", "expect_home", "expect_tie", "expect_away"]]
display(theGames)

# # Print to CSV

# first add the date of today
from datetime import datetime
now = datetime.now()
theGames['date_of_bet'] = '%s-%s-%s' % (now.day, now.month, now.year)

# append to book.csv
#theGames.to_csv('./book.csv', index=False, sep=',', float_format='%.3f', mode='a', header=False)

