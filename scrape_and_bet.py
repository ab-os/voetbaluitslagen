# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '../../../../tmp'))
	print(os.getcwd())
except:
	pass
#%% [markdown]
# # Scraper
# Scrapes odds from unibet, predictions from fivethirtyeight and shows you the best bets.

#%%
# choose a league (0-5)
currentLeague = 5

# create the url matrix
import pandas as pd
urlUnibet = ['https://www.unibet.eu/betting#filter/football/netherlands/eredivisie',
              'https://www.unibet.eu/betting#filter/football/spain/laliga',
              'https://www.unibet.eu/betting#filter/football/germany/bundesliga',
              'https://www.unibet.eu/betting#filter/football/england/premier_league',
              'https://www.unibet.eu/betting#filter/football/france/ligue_1',
              'https://www.unibet.eu/betting#filter/football/italy/serie_a']
url538 = ['https://projects.fivethirtyeight.com/soccer-predictions/eredivisie/',
           'https://projects.fivethirtyeight.com/soccer-predictions/la-liga/',
           'https://projects.fivethirtyeight.com/soccer-predictions/bundesliga/',
           'https://projects.fivethirtyeight.com/soccer-predictions/premier-league/',
           'https://projects.fivethirtyeight.com/soccer-predictions/ligue-1/',
           'https://projects.fivethirtyeight.com/soccer-predictions/serie-a/']
dfUrl = pd.DataFrame(data={'urlUnibet': urlUnibet, 'url538': url538})
#dfUrl

#%% [markdown]
# ## Odds from unibet

#%%
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep


#%%
# Start our headless (no GUI) browser
browser = webdriver.Firefox()


#%%
# Go to the URL
url = dfUrl.loc[currentLeague, 'urlUnibet']
print('Going to:', url)
browser.get(url)


#%%
# Wait until the accept-cookies button is present
element = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept"))
)

# If found, let's wait 1 sec
sleep(1)

# Click on it
element.click()

# no hurry please
sleep(np.sqrt(2))


#%%
# Find the dropdown bars, NOT the already expanded one
dropdowns = browser.find_elements_by_css_selector(".KambiBC-event-groups .KambiBC-collapsible-container:not(.KambiBC-expanded)")

# Click on them
for dropdown in dropdowns:
    dropdown.click()
    # lets just wait a bit in between
    sleep(np.sqrt(np.pi))


#%%
# Now get the beautiful source code
soup = BeautifulSoup(browser.page_source, 'html5lib')


#%%
# search for matches in the soup
matches = soup.find(class_="KambiBC-event-groups").find_all("li", class_="KambiBC-event-item")

# print amount found. Also remember this amount for getting the same amout from 538
numberOfMatches = len(matches)
print("Number of matches found: ", numberOfMatches)


#%%
# quit the browser
browser.quit()


#%%
# Create empty list
jobs = []

for match in matches:
    # Create empty dictionary
    job = {}
    
    # Find info on the page
    #job["date"] = match.find(class_="KambiBC-event-item__start-time--date").text # <- Doesnt work..?
    teams = match.find_all(class_="KambiBC-event-participants__name")
    job["home_team"] = teams[0].text
    job["away_team"] = teams[1].text
    odds = match.find_all(class_="KambiBC-mod-outcome__odds")
    job["odd_home_win"] = odds[0].text
    job["odd_tie"] = odds[1].text
    job["odd_away_win"] = odds[2].text
    
    # Add to the list
    jobs.append(job)


#%%
# Make a data frame
dfOdds = pd.DataFrame(jobs)

# Show
#dfOdds

#%% [markdown]
# ### Data transformation

#%%
# Change team names to lowercase
dfOdds["home_team"] = dfOdds["home_team"].str.lower()
dfOdds["away_team"] = dfOdds["away_team"].str.lower()

# Remove all accents
dfOdds["home_team"] = dfOdds["home_team"].str.normalize('NFKD').str.encode(encoding='ascii',errors='ignore').str.decode('utf-8')
dfOdds["away_team"] = dfOdds["away_team"].str.normalize('NFKD').str.encode(encoding='ascii',errors='ignore').str.decode('utf-8')

# Change the team names so that they match the ones in the 538 data frame
changes_nl = {'fc groningen': 'groningen',
              'fc twente': 'twente',
              'sc heerenveen': 'heerenveen',
              'fc utrecht': 'utrecht',
              'fc emmen': 'emmen'}
changes_de = {'bayer leverkusen': 'leverkusen',
             'borussia monchengladbach': 'gladbach',
             'vfl wolfsburg': 'wolfsburg',
             'borussia dortmund': 'dortmund',
             'augsburg': 'fc ausburg'}
changes_es = {'deportiva las palmas': 'las palmas',
             'fc barcelona': 'barcelona'}
changes_en = {}
changes_fr = {'saint-etienne': 'st etienne',
             'paris sg': 'psg'}
changes_it = {'hellas verona': 'verona'}
changes = {**changes_nl, **changes_de, **changes_es, **changes_en, **changes_fr, **changes_it}
for old,new in changes.items():
    # Replace!
    dfOdds["home_team"] = dfOdds["home_team"].str.replace(old, new)
    dfOdds["away_team"] = dfOdds["away_team"].str.replace(old, new)

# Make 3-letter code names
dfOdds["home_code"] = dfOdds["home_team"].str[:3]
dfOdds["away_code"] = dfOdds["away_team"].str[:3]

# Convert to numbers
dfOdds["odd_home_win"] = pd.to_numeric(dfOdds["odd_home_win"])
dfOdds["odd_away_win"] = pd.to_numeric(dfOdds["odd_away_win"])
dfOdds["odd_tie"] = pd.to_numeric(dfOdds["odd_tie"])

# Show
dfOdds

#%% [markdown]
# ## Predictions from five thirty eight

#%%
# so easy site, just use a basic scraper
from lxml import html
from lxml.cssselect import CSSSelector
import requests
import re
import pandas as pd


#%%
# Go to the URL
url = dfUrl.loc[currentLeague, 'url538']
page = requests.get(url)

# Get the source code
tree = html.fromstring(page.content)


#%%
# it shows all matches of the season here. Let's stick to the same number as from Unibet
matches = tree.cssselect('.games-container.upcoming .match-container')[:numberOfMatches]
print("Number of matches found: ", len(matches))


#%%
# prepare empty data frame
cols = ['date', 'home_team', 'away_team', 'home_win', 'tie', 'away_win']
df538 = pd.DataFrame(columns=cols)

# fill data frame with match info
for idx in range(len(matches)):
    match = matches[idx]
    
    df538.at[idx, 'date'] = match.cssselect(".date div")[0].text
    df538.at[idx, 'home_team'] = match.cssselect(".match-top .name")[0].text
    df538.at[idx, 'home_win'] = match.cssselect(".match-top .prob")[0].text
    df538.at[idx, 'tie'] = match.cssselect(".tie-prob div")[0].text
    df538.at[idx, 'away_team'] = match.cssselect(".match-bottom .name")[0].text
    df538.at[idx, 'away_win'] = match.cssselect(".match-bottom .prob")[0].text
    
#df538

#%% [markdown]
# ### Some data transformation

#%%
# Turn percentages into floats
df538['home_win'] = pd.to_numeric(df538['home_win'].str.replace("%",""))/100
df538['tie'] = pd.to_numeric(df538['tie'].str.replace("%",""))/100
df538['away_win'] = pd.to_numeric(df538['away_win'].str.replace("%",""))/100

# Drop the date column
#del df538["date"]

# Change team names to lowercase
df538["home_team"] = df538["home_team"].str.lower()
df538["away_team"] = df538["away_team"].str.lower()

# Remove all accents
df538["home_team"] = df538["home_team"].str.normalize('NFKD').str.encode(encoding='ascii',errors='ignore').str.decode('utf-8')
df538["away_team"] = df538["away_team"].str.normalize('NFKD').str.encode(encoding='ascii',errors='ignore').str.decode('utf-8')

# Make 3-letter code names
df538["home_code"] = df538["home_team"].str[:3]
df538["away_code"] = df538["away_team"].str[:3]

# SHow
df538

#%% [markdown]
# # Merge
# First check if team names are missed in the data transformation

#%%
# check for missing matches for Unibet
dfCheck = df538.merge(dfOdds, how="outer", on=["home_code", "away_code"], indicator=True)
dfCheck[dfCheck._merge != 'both']


#%%
# Merge by 3-letter codes
dfMerge = df538.merge(dfOdds, how="inner", on=["home_code", "away_code"], suffixes=('', '_uni'))

# print
print('Number of matches succesfully merged:', len(dfMerge))

#%% [markdown]
# # Analyse

#%%
# Calculate the expected profits for win, tie and loss
dfMerge["expect_home"] = dfMerge["home_win"] * dfMerge["odd_home_win"]
dfMerge["expect_away"] = dfMerge["away_win"] * dfMerge["odd_away_win"]
dfMerge["expect_tie"] = dfMerge["tie"] * dfMerge["odd_tie"]

# Set threshold
threshold = 1.2

# Show
theGames = dfMerge.query('expect_home>@threshold or expect_away>@threshold or expect_tie>@threshold')                    [["date", "home_team", "away_team", "expect_home", "expect_tie", "expect_away"]]
display(theGames)

#%% [markdown]
# # Print to CSV

#%%
# first add the date of today
from datetime import datetime
now = datetime.now()
theGames['date_of_bet'] = '%s-%s-%s' % (now.day, now.month, now.year)


#%%
# append to book.csv
#theGames.to_csv('./book.csv', index=False, sep=',', float_format='%.3f', mode='a', header=False)

