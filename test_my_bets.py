from pathlib import Path
import pandas as pd
import re
import lxml.html
from lxml.html.clean import Cleaner
import my_bets


def download_my_bets_html(f):
    html = my_bets.download_my_bets()
    with open(f, "w") as fd:
       fd.write(html)


if __name__ == "__main__":

    # Html file storage location
    html_filename = Path('./data/html/my_bets.html')

    # Open a browser to download the html code
    # Comment this line when debugging with local the html file
    #download_my_bets_html(html_filename)

    # Read
    with open(html_filename, "r") as f:
        html = f.read()

    # Parse the html
    doc = lxml.html.document_fromstring(html)
    df = my_bets.scrape_info_from_html(html)
    df = my_bets.data_prep(df)
