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
file_names = config.get("Publication", "file_names")
file_ror = config.get("Publication", "file_ror")
file_combined = config.get("Publication", "file_combined")
path = config.get("Publication", "path")


# merge all files from Openalex results into one
df = pd.concat(
   map(pd.read_csv, [f"{path}{file_names}", 
                     f"{path}{file_ror}"]), ignore_index=True)
# Reset Index
df.reset_index(drop=True, inplace=True)

# Delete double entries
df.drop_duplicates(subset="Doi", inplace=True)
# Reset Index
df.reset_index(drop=True, inplace=True)

df.to_csv(f"{path}{file_combined}", index=False, encoding="utf-8")
print(f"{file_combined} saved in path: {path}")