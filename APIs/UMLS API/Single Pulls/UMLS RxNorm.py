# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
version = 'current'

## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "EXCEL SHEET NAME HERE"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'GI Cancer Med Keywords.xlsx'

# Keyword Column Name
column_name = 'Keywords'

## End of Requested Inputs ##

# Read the Excel file
excel_file_path = excel_file_keywords
df = pd.read_excel(excel_file_path)

# Extract the column as a Pandas Series
column_series = df[column_name]

# Convert the Pandas Series to a list and exclude the column name as the first element
column_list = column_series.tolist()

string_list = column_list

# Now column_list contains the column data with the column name as the first element
print(string_list)

# Collect Data Pulled 
ui_code_RxNorm = []
rootSource_RxNorm = []
name_RxNorm = []

for x in np.arange(0, len(string_list), 1):
    value = string_list[x]
    URL = f"https://uts-ws.nlm.nih.gov/rest/search/current?apiKey={apikey}&string={value}&sabs=RXNORM&returnidType=code&pageSize=2000"
    response = requests.get(URL)
    variable = response.json()
    
    if 'result' in variable:
        # Pull ui code
        for y in np.arange(0, len(variable['result']['results']), 1):
            ui_code_RxNorm.append(variable['result']['results'][y]['ui'])

        # Pull rootSource code
        for y in np.arange(0, len(variable['result']['results']), 1):
            rootSource_RxNorm.append(variable['result']['results'][y]['rootSource'])

        # Pull RxNorm name code
        for y in np.arange(0, len(variable['result']['results']), 1):
            name_RxNorm.append(variable['result']['results'][y]['name'])
    else: 
        continue

RxNorm_pd = pd.DataFrame({"Data Concept": "RxNorm Code", "Data Sub-Concept": "N/A", "Coding Standard": rootSource_RxNorm, "Code Value": ui_code_RxNorm, "Code Description": name_RxNorm}).drop_duplicates().reset_index(drop=True)
# RxNorm_pd

# Converts the SNOMED-CT CUI Codes from the chunk above into SNOMEDCT_US Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = RxNorm_pd["Code Value"]

sabs = 'RXNORM'
RXNORM_name = []
RXNORM_code = []
RXNORM_root = []

for cui in cui_list:
        page = 0
        
        # o.write('SEARCH CUI: ' + cui + '\n' + '\n')
        
        while True:
            page += 1
            path = '/search/'+version
            query = {'apiKey':apikey, 'string':cui, 'sabs':sabs, 'returnIdType':'code', 'pageNumber':page}
            output = requests.get(base_uri+path, params=query)
            output.encoding = 'utf-8'
            #print(output.url)
        
            outputJson = output.json()

            results = (([outputJson['result']])[0])['results']
            
            if len(results) == 0:
                if page == 1:
                    #print('No results found for ' + cui +'\n')
                    # o.write('No results found.' + '\n' + '\n')
                    break
                else:
                    break
                    
            for item in results:
                RXNORM_code.append(item['ui'])
                RXNORM_name.append(item['name'])
                RXNORM_root.append(item['rootSource'])
        else: 
            continue
                
RXNORM_trans_df = pd.DataFrame({"Data Concept": "RxNorm Code", "Data Sub-Concept": "N/A", "Coding Standard": RXNORM_root, "Code Value": RXNORM_code, "Code Description": RXNORM_name})

# Find the parent folder "GitHub Saved Progress"
parent_folder_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))

# Define the output folder path
output_folder_path = os.path.join(parent_folder_path, "output")

# Check if the output folder exists, if not, create it
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)
    print(f"output folder created successfully.")

# Define the path for the output Excel file
excel_path = os.path.join(output_folder_path, f'{Excel_Sheet_Name}.xlsx')

# Write DataFrame to the Excel file
RXNORM_trans_df.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")


