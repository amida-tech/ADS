#!/usr/bin/env python
# coding: utf-8
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
excel_file_keywords = 'GI Cancer SNOMED Keywords.xlsx'

# Keyword Column Name
column_name = 'Keywords'

## DO NOT CHANGE BELOW THIS LINE ##

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


# Keep in mind this pulls the CUI code for SNOMEDCT from UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code = []
name = [] 
vocab_type = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/search/"+version
    full_url = uri+content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'string':string,'apiKey':apikey, 'pageNumber':page}
            query['includeObsolete'] = 'true'
            #query['includeSuppressible'] = 'true'
            #query['returnIdType'] = "sourceConcept"
            query['sabs'] = "SNOMEDCT_US"
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
                code.append(result['ui'])
                name.append(result['name'])
                vocab_type.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
snomed_df = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": vocab_type, "Code Value": code, "Code Description": name})


# Converts the SNOMED-CT CUI Codes from the chunk above into SNOMEDCT_US Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = snomed_df["Code Value"]

sabs = 'SNOMEDCT_US'
SNOMEDCT_name = []
SNOMEDCT_code = []
SNOMEDCT_root = []

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
                SNOMEDCT_code.append(item['ui'])
                SNOMEDCT_name.append(item['name'])
                SNOMEDCT_root.append(item['rootSource'])

snomed_trans_df = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": SNOMEDCT_root, "Code Value": SNOMEDCT_code, "Code Description": SNOMEDCT_name})


# Get children of SNOMED-CT 
# This works, it just takes a while to run
# If you want more responses, change 'children' to 'descendants' this will run a lot slower, but will return more SNOMEDCT_US values

decend_names = []
decend_values = []
decend_root = []

for x in np.arange(0,len(SNOMEDCT_code),1):
    source = 'SNOMEDCT_US'
    identifier = str(SNOMEDCT_code[x])
    operation = 'children'
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/"+operation

    pageNumber=0

    try:
        while True:
            pageNumber += 1
            query = {'apiKey':apikey,'pageNumber':pageNumber}
            r = requests.get(uri+content_endpoint,params=query)
            r.encoding = 'utf-8'
            items  = r.json()

            if r.status_code != 200:
                if pageNumber == 1:
                    # print('No results found.'+'\n')
                    break
                else:
                    break

            # print("Results for page " + str(pageNumber)+"\n")

            for result in items["result"]:
                decend_values.append(result["ui"])
                decend_names.append(result["name"])
                decend_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
SNOMED_decend = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": decend_root, "Code Value": decend_values, "Code Description": decend_names})
SNOMED_trans_decend = pd.concat([SNOMED_decend, snomed_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

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
SNOMED_trans_decend.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")

