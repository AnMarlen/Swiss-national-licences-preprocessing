Swiss national licences preprocessing
=========================

Project Description
--------------------------

The prototype aims to find all articles published in journals of the four publishers Springer, De Gruyter, Oxford University Press and Cambridge University Press that are affiliated with a Swiss university. It searches all articles on the condition that an author is affiliated with a given Swiss university, compares the result with the standardised title journal lists provided by the Consortium of Swiss Academic Libraries (CSAL) and checks whether the articles found can be uploaded to the repositories of CSAL members in accordance with the negotiated Swiss national licences.

The result is a list of bibliographic metadata that facilitates the inclusion of missing article metadata in Swiss university repositories and facilitates full-text searching for the respective articles.


**Download and merge CSAL journal lists**

The Python script "recent-CSAL-journal-lists" downloads the four first files provided on the website https://consortium.ch/title-lists-for-swiss-national-licences/?lang=en of the CSAL that are stored under a link beginning with"https://github.com/swissbib/metadataNationalLicences/raw/master/title-lists/".
The script merges all 4 files into one with the following columns from the original excel files.

- "print_identifier",
- "online_identifier",
- "date_first_issue_online",
- "num_first_vol_online",
- "num_first_issue_online",
- "date_last_issue_online", 
- "num_last_vol_online",
- "num_last_issue_online",
- "publisher_name"


**Search in OpenAlex Springer, De Gruyter, Oxford University Press and Cambridge University articles of authors belonging to a Swiss HEI**

The Python scripts "search-articles-OpenAlex-names" and "..._ror" build a search query for the API of OpenAlex working either with the ROR ID a search parameter or a phrase search based on name variants of an institution. The result list is looped through and added with information about the corresponding author's institution, if OpenAlex includes information about the correspondence status. All articles are exported into two CSV files. The table contains the following columns:

- Doi 
(data type: string ; example: https://doi.org/10.1038/s41380-022-01661-0)
- Title 
(data type: string ; example: The serotonin theory of depression: a systematic umbrella review of the evidence)                  
- Year 
(data type integer ; pattern YYYY; example: 2022)
- OA 
(data type: boolean ; True in case the articles is published Open Access by the publisher, False in case article is published closed)
- Publisher 
(data type: string ; example: Springer Nature)
- Journal
(data type: string ; example: Molecular psychiatry)
- ISSN 
(data type: string ; pattern XXXX-XXXX, example: 1359-4184)
- Affiliation_corr.author 
(multiple affiliations are seperated with "," data type: list, example: ['ZHAW Zurich University of Applied Sciences'])
- Affiliation_corr.author_raw 
(multiple affiliations are seperated with ";" , data type: list, example: ['Environmental Genomics and Systems Biology Research Group, Institute for Natural Resource Sciences, Zurich University of Applied Sciences (ZHAW), Wädenswil, Switzerland'])

Both CSV files are merged together with the script "combine-article-lists-OpenAlex". Duplicates based on values in the column "Doi" are deleted and saved as a single CSV.


**Compare OpenAlex results with journal lists of CSAL and articles already indexed in the institutional repository**

The Python script "compare-article-lists-OpenAlex-repository-csal" compares the DOIs in the OpenAlex list with a list of DOIs of publications already indexed in a repository. It adds the column "in-repository" to the OpenAlex article-list with the boolean value "True" if the ApenALex-DOI can be found in the repository DOIs as well or "False" in case it could not be found. Afterwards, it deletes all articles that are already in the repository. 
It then saves all articles published as Open Access articles in a separate data frame. The articles left are checked if they were published in a journal covered by a Swiss national licence based on the print or online ISSN and if the article was published in a period covered by the Swiss national licence based on the publication year. The article list is filtered again for those articles where both conditions are True (in journal and in correct period published). At the end, the data frame with all articles already published OA and the articles covered by the national licences are put in one data frame and saved as CSV. These articles could be stored in the repository afterwards, after a final manual check (especially for corresponding authors of Springer articles).

- Doi 
(data type: string ; example: https://doi.org/10.1038/s41380-022-01661-0)
- Title 
(data type: string ; example: The serotonin theory of depression: a systematic umbrella review of the evidence)                  
- Year 
(data type integer ; pattern YYYY; example: 2022)
- OA 
(data type: boolean ; "True" in case the articles is published Open Access by the publisher, "False" in case article is published closed)
- Publisher 
(data type: string ; example: Springer Nature)
- Journal
(data type: string ; example: Molecular psychiatry)
- ISSN 
(data type: string ; pattern XXXX-XXXX, example: 1359-4184)
- Affiliation_corr.author 
(multiple affiliations are seperated with "," data type: list, example: ['ZHAW Zurich University of Applied Sciences'])
- Affiliation_corr.author_raw 
(multiple affiliations are seperated with ";" , data type: list, example: ['Environmental Genomics and Systems Biology Research Group, Institute for Natural Resource Sciences, Zurich University of Applied Sciences (ZHAW), Wädenswil, Switzerland'])
- in_repository
(data type: boolean ; True in case the articles is already published in institutional repository, False in case article is not)
- issn_csal_o
(data type: boolean ; True in case the articles is published in a journal with a E-ISSN matches print ISSN in CSAL list, False in case article is not)
- issn_csal_p
(data type: boolean ; True in case the articles is published in a journal with a print ISSN matches print ISSN in CSAL list, False in case article is not)
- period
(data type: boolean ; True in case the articles is published in a timeframe that is covered in national licence, False in case article is not)

The following columns, along with their respective values, were added with the help of the Python script:




How to Install and Run the Projects
--------------------------

_Before running the scripts, follow these steps:_

- Check the configuration (config.ini) and adjust the file according to your needs.

These variables should be changed in any case:

[Institution]

- list of name variants of Swiss higher education institution, names that consist of more than one word need to be written in parentheses, separator is "|" ; example: names = ZHAW|"Zurich University of Applied Sciences"|"Zürcher Hochschule für Angewandte Wissenschaften"
- ROR-ID of the authors' institution publications are searched ; example: ror_id = https://ror.org/05pmsvm27
- contact e-mail for authentification in OpenAlex API request ; example: email = xyz@zhaw.ch


[Publication]

-time span of the creation date of publications searched, formatted as yyyy-mm-dd ; example: from_published_date = 2015-01-01


[Repository]

- name of CSV where DOIs of repository are stored ; example: file_repository = digitalcollection.csv
- header of column in CSV-file, where DOI of article in repository is stored for comparison with OpenAlex results ; example: column_doi = DOI_ZHAW
- name of file of final results of articles to be ingested in repository ; example: file_ingest = ingest-national-licences.csv


- The download of the CSAL files is based on web scraping, so it should be checked that the website mentioned above is still designed with the latest Excel files of the journal lists at the beginning of the page and that the prefix of the file path is still the same.
- The script works with relative file paths and the given folder structure to save the results as CSV. This can be changed if necessary.
- The DOIs of the publications already indexed in the institutional repository should be stored in a CSV file, the column where the DOIs are stored should contain only one DOI per cell.


_Prerequisites_

- Python 3.11.7

**additional packages**

- requests (version 2.31.0)
- beautifulsoup4 (version 4.12.3)
- pandas (version 2.2.2)
- urllib3 (version 2.2.1)

**Limitations**

The label "is_corresponding" to indicate whether or not an author is the corresponding author of a paper in OpenAlex data is a new feature, and the information may be missing for many papers. It is therefore recommended to check the corresponding author if the information is missing for articles published by Springer.

Filtering OpenAlex results by "from_publication_date" is not a reliable way to retrieve recently updated and created works, due to the way publishers assign publication dates. It is recommended to use from_created_date or from_updated_date to retrieve recent changes in OpenAlex, but this field requires an OpenAlex Premium subscription to access.

Basic paging has been used to retrieve all results returned by the API request, this only works for the first 10,000 results of each list. If you want to see more than 10,000 results, you'll need to use cursor paging (https://github.com/ourresearch/openalex-api-tutorials/blob/main/notebooks/getting-started/paging.ipynb). It is strongly recommended that you test how many results your API request will return with a basic search (https://openalex.org/works) before running the scripts for the first time. You could use the Institution, Publisher, Type and Year filters.

The check to see if an article was published in a period covered by the national licence is based solely on the year of publication, even if there are a few titles where the coverage of the journal starts somewhere in the middle of the year. As the information in the columns "num_first_issue_online" and "num_last_issue_online" in the CSAL journal lists is not normalised to the datatype integer, it is too complicated at the moment to use it as an additional check criterion.


**Sources**

- OpenAlex documentation of their API, especially for the entity works: https://docs.openalex.org/api-entities/works 
- CSAL documentation about Swiss national licences: https://consortium.ch/nationallizenzen/?lang=en


**Contributing**

Feel free to contribute by opening pull requests or reporting issues.
