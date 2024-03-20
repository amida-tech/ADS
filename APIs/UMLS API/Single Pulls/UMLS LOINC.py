#!/usr/bin/env python
# coding: utf-8

## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "EXCEL SHEET NAME HERE"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'GI Cancer LOINC Keywords.xlsx'

# Keyword Column Name
column_name = 'Keywords'


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


## DO NOT CHANGE BELOW THIS LINE ##
import requests 
import argparse
import numpy as np
import pandas as pd
import os
version = 'current'

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

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
            query = {'string':string,'apiKey':apikey, 'pageNumber':page}
            query['includeObsolete'] = 'true'
            #query['includeSuppressible'] = 'true'
            #query['returnIdType'] = "sourceConcept"
            query['sabs'] = "LNC"
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
        
loinc_df = pd.DataFrame({"Data Concept": "Observation Code", "Data Sub-Concept": "N/A", "Coding Standard": vocab_type_4, "Code Value": code_4, "Code Description": name_4})


# Converts the LOINC CUI codes from the chunk above into LOINC

base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = loinc_df["Code Value"]

sabs = 'LNC'
LOINC_name = []
LOINC_code = []
LOINC_root = []

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
                LOINC_code.append(item['ui'])
                LOINC_name.append(item['name'])
                LOINC_root.append(item['rootSource'])

loinc_trans_df = pd.DataFrame({"Data Concept": "Observation Code", "Data Sub-Concept": "N/A", "Coding Standard": LOINC_root, "Code Value": LOINC_code, "Code Description": LOINC_name})

# Get Children of LNC
decend_LOINC_names = []
decend_LOINC_values = []
decend_LOINC_root = []

for x in np.arange(0,len(LOINC_code),1):
    source = 'LNC'
    identifier = str(LOINC_code[x])
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
                decend_LOINC_values.append(result["ui"])
                decend_LOINC_names.append(result["name"])
                decend_LOINC_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
loinc_decend = pd.DataFrame({"Data Concept": "Observation Code", "Data Sub-Concept": "N/A", "Coding Standard": decend_LOINC_root, "Code Value": decend_LOINC_values, "Code Description": decend_LOINC_names})
loinc_trans_decend = pd.concat([loinc_decend, loinc_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)


# Folder name
folder_name = "output"

# Create the "output" folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"Folder '{folder_name}' created successfully.")

# Define the excel file name with its path
excel_name = os.path.join(folder_name, f'{Excel_Sheet_Name}.xlsx')

# Write DataFrame to an Excel file in the output folder
loinc_trans_decend.to_excel(excel_name)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the '{folder_name}' folder.")

