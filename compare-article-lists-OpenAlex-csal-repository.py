"""
    This file is part of the  Swiss national licences preprocessing package.
    (c) ZHAW HSB <apps.hsb@zhaw.ch>

    For the full copyright and license information, please view the LICENSE
    file that was distributed with this source code.
"""
import configparser
import pandas as pd

# Read config.ini and get values
config = configparser.ConfigParser()
config.read("config.ini", "UTF-8")
file_combined = config.get("Publication", "file_combined")
file_repository = config.get("Repository", "file_repository")
file_csal = config.get("CSAL", "file_csal")
column_doi = config.get("Repository", "column_doi")
path_rep = config.get("Repository", "path")
path_open = config.get("Publication", "path")
path_csal = config.get("CSAL", "path")
file_ingest = config.get("Repository", "file_ingest")


# Open export of DOIs of articles in your repository to compare with Open Alex results
# Attention: export should consists of one DOI per cell per column 
df_repository = pd.read_csv(f"{path_rep}{file_repository}")

#add prefix "https://doi.org/" to repository dois, if prefix does not exists
for row in range(len(df_repository.index)): 
   if df_repository.loc[row, column_doi].startswith("10"):
      df_repository.loc[row, column_doi] = "https://doi.org/" + df_repository.loc[row, column_doi]

# Open combined journal's list of all Swiss national licences journal titles 
df_csal = pd.read_csv(f"{path_csal}{file_csal}")

# Open combined article list of OpenAlex results for institution 
df_openalex = pd.read_csv(f"{path_open}{file_combined}")
 
# compare found articles with articles in repository based on DOI in OpenAlex and DOIs in repository
# write the result of the comparison in new colum "in_repository"
df_openalex["in_repository"] = df_openalex["Doi"].isin(df_repository[column_doi]).astype(bool)

# delete all articles that are already indexed in repository from OpenAlex list
df_openalex.drop(df_openalex[df_openalex.in_repository == True].index, inplace=True)
  
#filter articles, that are not already in repository and OA in a new dataframe
df_oa = df_openalex.loc[df_openalex["OA"] == True]

# compare if ISSN of found article matches online ISSN in CSAL lists
df_openalex["issn_csal_o"] = df_openalex["ISSN"].isin(df_csal["online_identifier"]).astype(bool)

# compare if ISSN of found article matches print ISSN in CSAL lists
df_openalex["issn_csal_p"] = df_openalex["ISSN"].isin(df_csal["print_identifier"]).astype(bool)

#Filter dataframe for records that are not OA and where the ISSN matches one of the CSAL ISSNs 
df_openalex = df_openalex.loc[(df_openalex["OA"] == False)
                              & (df_openalex["issn_csal_p"] | df_openalex["issn_csal_o"]== True)]
df_openalex.reset_index(drop=True, inplace=True)
   

# compare if year of found articles matches period in CSAL lists
df_csal["date_first_issue_online"].astype(int)
df_csal["date_last_issue_online"].astype(int)
df_openalex["Year"].astype(int)

for row in range(len(df_openalex.index)):
   if df_openalex.at[row, "issn_csal_o"] == True:
      row_num = df_csal[df_csal["online_identifier"] == df_openalex.at[row, "ISSN"]].index[0]
      df_openalex.at[row, "period"] = (
         (df_csal.at[row_num, "date_first_issue_online"] <= df_openalex.at[row, "Year"]) 
         & (df_csal.at[row_num, "date_last_issue_online"] >= df_openalex.at[row, "Year"])
         )
   elif df_openalex.at[row, "issn_csal_p"] == True:
      row_num = df_csal[df_csal["print_identifier"] == df_openalex.at[row, "ISSN"]].index[0]
      df_openalex.at[row, "period"] = (
         (df_csal.at[row_num, "date_first_issue_online"] <= df_openalex.at[row, "Year"]) 
         & (df_csal.at[row_num, "date_last_issue_online"] >= df_openalex.at[row, "Year"])
         )
   else:
      df_openalex.at[row, "period"] == False


#filter records, that are in the self-archiving timeframe given in CSAL lists
df_archive = df_openalex.loc[(df_openalex["period"] == True)]

# combine the dataframes for missing closed published items and OA articles to be ingested in repository
df_ingest = pd.concat([df_archive, df_oa])

# Save results
df_ingest.to_csv(f"{path_rep}{file_ingest}", index=False, encoding="utf-8")
print(f"{file_ingest} saved in path: {path_rep}")
     