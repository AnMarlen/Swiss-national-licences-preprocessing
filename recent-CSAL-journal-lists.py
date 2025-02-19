"""
    This file is part of the  Swiss national licences preprocessing package.
    (c) ZHAW HSB <apps.hsb@zhaw.ch>

    For the full copyright and license information, please view the LICENSE
    file that was distributed with this source code.
"""

# Import standard python library package
import configparser
import re


# Import additional packages
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib import request

# Read config.ini and get values
config = configparser.ConfigParser()
config.read("config.ini")
url = config.get("CSAL", "url")
phrase_link = config.get("CSAL", "phrase_link")
limit_links = config.getint("CSAL", "links")
file_csal = config.get("CSAL", "file_csal")
path = config.get("CSAL", "path")


# open url of website of CSAL and 
page = requests.get(url)

links = [] # list of all links to files to be downloaded later
file_names = [] # list of all file names to be downloaded later

#parse html code of website for first x links to Excel files with journal lists
soup_search = BeautifulSoup(page.content, "html.parser")  
try: 
    for link in soup_search.find_all('a', 
                                     attrs={'href': re.compile(phrase_link)}, 
                                     limit=limit_links):
        link = link.get("href")
        links.append(link)
        file_names.append(link.removeprefix(phrase_link))

except Exception as error:
    print("An error occurred while writing link", 
        "\nreason: ", error)

# Download all journal lists
for i in range(len(links)):
    file = f"{path}{file_names[i]}"
    request.urlretrieve(links[i], file)
    print(f"{file_names[i]} saved in path: {path}")

# normalize every CSAL excel to the same column names and column set needed
dataframes = []
for i in range(len(file_names)):
    df = pd.read_excel(f"{path}{file_names[i]}")
    
    if "degruyter" or "Degruyter" in file_names[i]:
        df.columns = df.columns.str.lower()
        df.drop(df[pd.isnull(df.date_first_issue_online) == True].index, inplace=True)
        df.drop(df[pd.isnull(df.date_last_issue_online) == True].index, inplace=True)
        df["date_first_issue_online"] = df["date_first_issue_online"].astype(str) 
        df["date_first_issue_online"] = df["date_first_issue_online"].str.split("-").str[0]
        df["date_first_issue_online"] = df["date_first_issue_online"].astype(int)
        df["date_last_issue_online"] = df["date_last_issue_online"].astype(str)  
        df["date_last_issue_online"] = df["date_last_issue_online"].str.split("-").str[0] 
        df["date_last_issue_online"] = df["date_last_issue_online"].astype(int)  
    df = df[["publication_title",
             "print_identifier",
             "online_identifier",
             "date_first_issue_online",
             "num_first_vol_online",
             "num_first_issue_online",
             "date_last_issue_online", 
             "num_last_vol_online",
             "num_last_issue_online",
             "publisher_name"]]
    df.drop(df[pd.isnull(df.date_first_issue_online) == True].index, inplace=True)
    df.drop(df[pd.isnull(df.date_last_issue_online) == True].index, inplace=True)
    df["date_first_issue_online"] = df["date_first_issue_online"].astype(int)
    df["date_last_issue_online"] = df["date_last_issue_online"].astype(int)
    dataframes.append(df)

# Combine all lists into one
df_all = pd.concat(dataframes, ignore_index=True)

# Save combined list as CSV
df_all.to_csv(f"{path}{file_csal}", index=False)
print(f"{file_csal} saved in path: {path}")

