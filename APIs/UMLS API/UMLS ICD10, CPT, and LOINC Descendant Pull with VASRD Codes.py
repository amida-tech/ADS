# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
import re
version = 'current'

## CHANGE INPUTS HERE ##
apikey = 'PUT API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "Hip Keyword Call"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'Hip Keywords.xlsx'

# Keyword Column Name
column_name = 'keyword'

## End of Requested Inputs ##

def extract_code(url):
    result = re.search(r'/(\d+-\d+)$', url)
    if result:
        return result.group(1)
    else:
        return None
    
def extract_cpt_code(url):
    # Use a regular expression to match the pattern at the end of the URL
    match = re.search(r'/([^/]+)$', url)
    if match:
        return match.group(1)
    return None
    
base_uri = 'https://uts-ws.nlm.nih.gov'

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

# Get ICD10 Codes from another API source
# This is because UMLS is lacking alone in their ICD10 call

clin_table_ICD10_code = []
clin_table_ICD10_name = []
dc_code_ICD_10 = []
names = []

for x in np.arange(0, len(string_list),1):
    list_item = string_list[x]
    names.append(list_item.replace(" ", "_"))
    
for x in np.arange(0, len(names),1):
    value = names[x]
    string = str(string_list[x])
    DC_code = df["DC Code"][df['keyword'] == string].to_list()[0]
    URL = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={value}&maxList=500"
    response = requests.get(URL)
    variable = response.json()
    
    for y in np.arange(0, len(variable[3]),1):
        clin_table_ICD10_code.append(variable[3][y][0])
    
    for y in np.arange(0, len(variable[3]),1):
        clin_table_ICD10_name.append(variable[3][y][1])
        dc_code_ICD_10.append(DC_code)
        
clin_table_test_pd = pd.DataFrame({"VASRD Code": dc_code_ICD_10, "CFR Criteria": "N/A", "Code Set": "ICD10", "Code": clin_table_ICD10_code, "Code Description": clin_table_ICD10_name}).drop_duplicates().reset_index(drop=True)

# This pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated ICD10, LNC, and CPT codes

code_2 = []
name_2 = [] 
vocab_type_2 = []
dc_code_2 = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    DC_code = df["DC Code"][df['keyword'] == string].to_list()[0]
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/search/"+version
    full_url = uri+content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'string':string, 'sabs': 'ICD10', 'apiKey':apikey, 'pageNumber':page}
            query['includeObsolete'] = 'true'
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
                dc_code_2.append(DC_code)
                code_2.append(result['ui'])
                name_2.append(result['name'])
                vocab_type_2.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
icd_df = pd.DataFrame({"VASRD Code": dc_code_2, "CFR Criteria": "N/A", "Code Set": vocab_type_2, "Code": code_2, "Code Description": name_2})

# Converts the ICD10 CUI Codes from the chunk above into ICD10 Codes (Atoms)
cui_list = icd_df["Code"]
dc_code_list = icd_df["VASRD Code"]

ICD10_name = []
ICD10_code = []
ICD10_root = []
ICD_10_VASRD_Code = []

for x in np.arange(0, len(cui_list),1):
    cui = cui_list[x]
    dc_code = dc_code_list[x]
    content_endpoint = f"/rest/content/current/CUI/{cui}/atoms?"
    full_url = base_uri + content_endpoint
    page = 0
    
    try:
        while True:
            page += 1
            query = {'apiKey': apikey, 'sabs': 'ICD10', 'pageNumber': page}
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            results = r.json()

            for item in np.arange(0, len(results['result']), 1):
                ICD_10_VASRD_Code.append(dc_code)
                ICD10_code.append(extract_cpt_code(results['result'][item]['code']))
                ICD10_name.append(results['result'][item]['name'])
                ICD10_root.append(results['result'][item]['rootSource'])
                
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

icd10_trans_df = pd.DataFrame({"VASRD Code": ICD_10_VASRD_Code, "CFR Criteria": "N/A", "Code Set": ICD10_root, "Code": ICD10_code, "Code Description": ICD10_name})

# Combine the ICD10 pull from a different API and merge it with the UMLS pull 
ICD10_full = pd.concat([clin_table_test_pd, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_3 = []
name_3 = [] 
vocab_type_3 = []
dc_code_3 = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    DC_code = df["DC Code"][df['keyword'] == string].to_list()[0]
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/search/"+version
    full_url = uri+content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'string':string,'apiKey':apikey, 'sabs': 'CPT', 'pageNumber':page}
            query['includeObsolete'] = 'true'
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
                dc_code_3.append(DC_code)
                code_3.append(result['ui'])
                name_3.append(result['name'])
                vocab_type_3.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
cpt_df = pd.DataFrame({"VASRD Code": dc_code_3, "CFR Criteria": "N/A", "Code Set": vocab_type_3, "Code": code_3, "Code Description": name_3})

# Converts the CPT CUI Codes from the chunk above into CPT Codes (Atoms)
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = cpt_df["Code"]
dc_code_list = cpt_df["VASRD Code"]

CPT_name = []
CPT_code = []
CPT_root = []
CPT_DC_Code = []

for x in np.arange(0, len(cui_list),1):
    cui = cui_list[x]
    dc_code = dc_code_list[x]
    content_endpoint = f"/rest/content/current/CUI/{cui}/atoms?"
    full_url = base_uri + content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'apiKey': apikey, 'sabs': 'CPT', 'pageNumber': page}
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            results = r.json()

            for item in np.arange(0, len(results['result']), 1):
                CPT_DC_Code.append(dc_code)
                CPT_code.append(extract_cpt_code(results['result'][item]['code']))
                CPT_name.append(results['result'][item]['name'])
                CPT_root.append(results['result'][item]['rootSource'])
                
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

CPT_trans_df = pd.DataFrame({"VASRD Code": CPT_DC_Code, "CFR Criteria": "N/A", "Code Set": CPT_root, "Code": CPT_code, "Code Description": CPT_name})


# LOINC CUI Codes
code_4 = []
name_4 = [] 
vocab_type_4 = []
dc_code_loinc = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    DC_code = df["DC Code"][df['keyword'] == string].to_list()[0]
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
                dc_code_loinc.append(DC_code)
                code_4.append(result['ui'])
                name_4.append(result['name'])
                vocab_type_4.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
loinc_df = pd.DataFrame({"VASRD Code": dc_code_loinc, "CRF Criteria": "N/A", "Code Set": vocab_type_4, "Code": code_4, "Code Description": name_4})

loinc_df = loinc_df[loinc_df['Code Set'] == "LNC"]

cui_list = loinc_df["Code"].to_list()
dc_code_list = loinc_df["VASRD Code"].to_list()

LOINC_name = []
LOINC_code = []
LOINC_root = []
LOINC_DC_Code = []

for x in np.arange(0, len(cui_list),1):
    cui = cui_list[x]
    dc_code = dc_code_list[x]
    content_endpoint = f"/rest/content/current/CUI/{cui}/atoms?"
    full_url = base_uri + content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'apiKey': apikey, 'sabs': 'LNC', 'ttys': 'LC', 'pageNumber': page}
            query['sabs'] = "LNC"
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            results = r.json()

            for item in np.arange(0, len(results['result']), 1):
                LOINC_DC_Code.append(dc_code)
                LOINC_code.append(extract_code(results['result'][item]['code']))
                LOINC_name.append(results['result'][item]['name'])
                LOINC_root.append(results['result'][item]['rootSource'])
                
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

loinc_trans_df = pd.DataFrame({"VASRD Code": LOINC_DC_Code, "CFR Criteria": "N/A", "Code Set": LOINC_root, "Code": LOINC_code, "Code Description": LOINC_name})

loinc_trans_df = loinc_trans_df.drop_duplicates(subset=["Code"])

# Combine CPT and LOINC Transformed DataFrames 
CPT_LOINC_full = pd.concat([loinc_trans_df, CPT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Combine ICD10, CPT and LOINC Transformed DataFrames 
ICD10_CPT_LOINC_full = pd.concat([ICD10_full, CPT_LOINC_full.loc[:]]).drop_duplicates().reset_index(drop=True)

# Find the parent folder "GitHub Saved Progress"
parent_folder_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# Define the output folder path
output_folder_path = os.path.join(parent_folder_path, "output")

# Check if the output folder exists, if not, create it
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)
    print(f"output folder created successfully.")

# Define the path for the output Excel file
excel_path = os.path.join(output_folder_path, f'{Excel_Sheet_Name}.xlsx')

# Write DataFrame to the Excel file
ICD10_CPT_LOINC_full.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")