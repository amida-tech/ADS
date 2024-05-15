# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
import re
version = 'current'

## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "EXCEL SHEET NAME HERE"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'GI Cancer LOINC Keywords.xlsx'

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

# Pull the CUI Codes from UMLS
code_4 = []
name_4 = [] 
vocab_type_4 = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/search/"+version
    full_url = uri+content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'string':string,'apiKey':apikey, 'pageNumber':page, 'sabs': 'LNC'}
            query['includeObsolete'] = 'true'
            #query['includeSuppressible'] = 'true'
            #query['returnIdType'] = "sourceConcept"
            # query['sabs'] = "LNC"
            r = requests.get(full_url,params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs  = r.json()

            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                if page == 1:
                    #print('No results found.'+'\n')
                    break
                else:
                    break

            #print("Results for page " + str(page)+"\n")

            for result in items:
                code_4.append(result['ui'])
                name_4.append(result['name'])
                vocab_type_4.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
loinc_df = pd.DataFrame({"Coding Standard": vocab_type_4, "Code Value": code_4, "Code Description": name_4})

# Drop any codes that may have been picked up that are not LNC codes
loinc_df = loinc_df[loinc_df['Code Value'] != "LNC"]

# Converts the LOINC CUI codes from the chunk above into LOINC codes

cui_list = loinc_df["Code Value"]
base_uri = "https://uts-ws.nlm.nih.gov"

sabs = 'LNC'
LOINC_name = []
LOINC_code = []
LOINC_root = []
LOINC_term_type = []

def extract_code(url):
    result = re.search(r'/(\d+-\d+)$', url)
    if result:
        return result.group(1)
    else:
        return None

for cui in cui_list:
    content_endpoint = f"/rest/content/current/CUI/{cui}/atoms?"
    full_url = base_uri + content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'apiKey': apikey, 'ttys': 'LN,LC', 'pageNumber': page}
            query['sabs'] = "LNC"
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            results = r.json()

            for item in np.arange(0, len(results['result']), 1):
                LOINC_code.append(extract_code(results['result'][item]['code']))
                LOINC_name.append(results['result'][item]['name'])
                LOINC_root.append(results['result'][item]['rootSource'])
                LOINC_term_type.append(results['result'][item]['termType'])
                
            if len(results) == 0:
                if page == 1:
                    print('No results found for ' + cui)
                break

    except requests.exceptions.RequestException as req_err:
        # Some CUI code atoms don't have LN or LC codes, this addresses that error and skips it
        # print(f"Request error for CUI {cui}: {req_err}")
        # Skip to the next CUI
        continue

    except ValueError as val_err:
         # Some CUI code atoms don't have LN or LC codes, this also addresses that error and skips it
        # print(f"JSON decoding error for CUI {cui}: {val_err}")
        # Skip to the next CUI
        continue

loinc_trans_df = pd.DataFrame({"Coding Standard": LOINC_root, "Term Type": LOINC_term_type, "Code Value": LOINC_code, "Code Description": LOINC_name})

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
loinc_trans_df.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")

