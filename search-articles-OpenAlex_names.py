"""
    This file is part of the  Swiss national licences preprocessing package.
    (c) ZHAW HSB <apps.hsb@zhaw.ch>

    For the full copyright and license information, please view the LICENSE
    file that was distributed with this source code.
"""
import configparser
import requests
import json
import pandas as pd

# Read config.ini and get values
config = configparser.ConfigParser()
config.read("config.ini", "UTF-8")
names = config.get("Institution", "names")
publishers = config.get("Publisher", "publishers")
date_start = config.get("Publication", "from_published_date")
date_end = config.get("Publication", "to_published_date")
email = config.get("Institution", "email")
file_names = config.get("Publication", "file_names")
path = config.get("Publication", "path")

def build_institution_works(names, publishers):
    """Create a searchquery for OpenAlex API with ror id and return query."""
    # specify endpoint
    endpoint = "works"

    # build the "filter" parameter
    filters = (
        f"raw_affiliation_string.search:{names}",
        "is_paratext:false",
        "type:article", 
        f"from_publication_date:{date_start},to_publication_date:{date_end}",
        "primary_location.source.has_issn:true",
        f"primary_location.source.publisher_lineage:{publishers}"
    )
    
    # build the "select" parameter
    select = (
        "id",
        "doi",
        "title",
        "publication_year",
        "primary_location",
        "authorships"
    )

    # put the URL together
    return f"https://api.openalex.org/{endpoint}?filter={','.join(filters)}&select={','.join(select)}&page={page}&mailto={email}"

def corresponding(authorships):
    """
    Loop through all authorship objects for every article. 
    Return only institutions of corresponding authors.
    """
    return[element["institutions"] 
           for element in authorships if element["is_corresponding"] == True]

def institution_corresponding(affiliation_complete):
    """
    Loop through all lists of institutions of the correspondings authors. 
    Return the element "display_name".
    """
    affiliations = []
    for x in range(len(affiliation_complete)):
        for i in range(len(affiliation_complete[x])):
            try:
                affiliations.append(affiliation_complete[x][i]["display_name"])
            except Exception:
                pass
        return affiliations

def institution_corresponding_raw(authorships):
    """
    Loop through all authorship objects for every article.
    Return only the raw_affiliation_string of corresponding authors.
    """
    return[element["raw_affiliation_string"] 
           for element in authorships if element["is_corresponding"] == True]

# dataframe for results
df = pd.DataFrame(columns=("Doi", 
                           "Title", 
                           "Year", 
                           "OA", 
                           "Publisher", 
                           "Journal", 
                           "ISSN", 
                           "Affiliation_corr.author", 
                           "Affiliation_corr.author_raw"
                           ))

# position of index for new rows in dataframe
row = 0

# url with a placeholder for page number
page = 1
has_more_pages = True
fewer_than_10k_results = True

# loop through pages
while has_more_pages and fewer_than_10k_results:
    
    # set page value and request page from OpenAlex
    example_url_with_page = build_institution_works(names, publishers)
    url = example_url_with_page.format(page)
    page_with_results = requests.get(url).json()
    
    # loop through partial list of results and write selected elements in dataframe
    results = page_with_results["results"]
    for i,work in enumerate(results):
        doi = work["doi"]
        title = work["title"]
        year = work["publication_year"]
        is_oa = work.get("primary_location", {}).get("is_oa")
        host = work.get("primary_location", {}).get("source", {}).get("host_organization_name")
        journal = work.get("primary_location", {}).get("source", {}).get("display_name")
        issn = work.get("primary_location", {}).get("source", {}).get("issn_l")
        authorships = work.get("authorships")
        affiliation_complete = corresponding(authorships)
        affiliation = institution_corresponding(affiliation_complete)
        affiliation_raw = institution_corresponding_raw(authorships)
        df.loc[i+row] = [doi, 
                         title, 
                         year, 
                         is_oa, 
                         host, 
                         journal, 
                         issn, 
                         affiliation, 
                         affiliation_raw]
        i +=1

    # next page
    page += 1
    row += 25
    
    # end loop when either there are no more results on the requested page 
    # or the next request would exceed 10,000 results
    per_page = page_with_results["meta"]["per_page"]
    has_more_pages = len(results) == per_page
    fewer_than_10k_results = per_page * page <= 10000

# Save the output as CSV
df.to_csv(f"{path}{file_names}", index=False, encoding="utf-8")
print(f"{file_names} saved in path: {path}")