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
excel_file_keywords = 'GI Cancer SNOMED Keywords.xlsx'

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

names = []

for x in np.arange(0, len(string_list),1):
    list_item = string_list[x]
    names.append(list_item.replace(" ", "_"))


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
# If it's taking too long, change the operation = 'descendants' to 'children'; this will return less, but run faster

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

# Get ICD10 Codes from another API source
# This is because UMLS is lacking alone in their ICD10 call

clin_table_ICD10_code = []
clin_table_ICD10_name = []

for x in np.arange(0, len(names),1):
    value = names[x]
    URL = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={value}&maxList=500"
    response = requests.get(URL)
    variable = response.json()
    
    for y in np.arange(0, len(variable[3]),1):
        clin_table_ICD10_code.append(variable[3][y][0])
    
    for y in np.arange(0, len(variable[3]),1):
        clin_table_ICD10_name.append(variable[3][y][1])
        
clin_table_test_pd = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": "ICD10", "Code Value": clin_table_ICD10_code, "Code Description": clin_table_ICD10_name}).drop_duplicates().reset_index(drop=True)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_2 = []
name_2 = [] 
vocab_type_2 = []

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
            query['sabs'] = "ICD10"
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
                code_2.append(result['ui'])
                name_2.append(result['name'])
                vocab_type_2.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
icd_df = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": vocab_type_2, "Code Value": code_2, "Code Description": name_2})


# Converts the ICD10 CUI Codes from the chunk above into ICD10 Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = icd_df["Code Value"]

sabs = 'ICD10'
ICD10_name = []
ICD10_code = []
ICD10_root = []

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
                ICD10_code.append(item['ui'])
                ICD10_name.append(item['name'])
                ICD10_root.append(item['rootSource'])

icd10_trans_df = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": ICD10_root, "Code Value": ICD10_code, "Code Description": ICD10_name})


# Get Decendents of ICD10
decend_ICD10_names = []
decend_ICD10_values = []
decend_ICD10_root = []

for x in np.arange(0,len(ICD10_code),1):
    source = 'ICD10'
    identifier = str(ICD10_code[x])
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
                decend_ICD10_values.append(result["ui"])
                decend_ICD10_names.append(result["name"])
                decend_ICD10_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
ICD10_decend = pd.DataFrame({"Data Concept": "Diagnosis Code", "Data Sub-Concept": "N/A", "Coding Standard": decend_ICD10_root, "Code Value": decend_ICD10_values, "Code Description": decend_ICD10_names})
ICD10_trans_decend = pd.concat([ICD10_decend, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)


# Combine the ICD10 pull from a different API and merge it with the UMLS pull 
ICD10_full = pd.concat([clin_table_test_pd, ICD10_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)
ICD10_full


# Combine the SNOMEDCT_US and ICD10 Transformed and Decendents DataFrames
SNOMEDCT_ICD10_trans_decend = pd.concat([SNOMED_trans_decend, ICD10_full.loc[:]]).drop_duplicates().reset_index(drop=True)


# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_3 = []
name_3 = [] 
vocab_type_3 = []

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
            query['sabs'] = "CPT"
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
                code_3.append(result['ui'])
                name_3.append(result['name'])
                vocab_type_3.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
cpt_df = pd.DataFrame({"Data Concept": "Procedure Code", "Data Sub-Concept": "N/A", "Coding Standard": vocab_type_3, "Code Value": code_3, "Code Description": name_3})


# Converts the CPT CUI Codes from the chunk above into CPT Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = cpt_df["Code Value"]

sabs = 'CPT'
CPT_name = []
CPT_code = []
CPT_root = []

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
                CPT_code.append(item['ui'])
                CPT_name.append(item['name'])
                CPT_root.append(item['rootSource'])

CPT_trans_df = pd.DataFrame({"Data Concept": "Procedure Code", "Data Sub-Concept": "N/A", "Coding Standard": CPT_root, "Code Value": CPT_code, "Code Description": CPT_name})


# Get Decendents of CPT
decend_CPT_names = []
decend_CPT_values = []
decend_CPT_root = []

for x in np.arange(0,len(CPT_code),1):
    source = 'CPT'
    identifier = str(CPT_code[x])
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
                decend_CPT_values.append(result["ui"])
                decend_CPT_names.append(result["name"])
                decend_CPT_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
CPT_decend = pd.DataFrame({"Data Concept": "Procedure Code", "Data Sub-Concept": "N/A", "Coding Standard": decend_CPT_root, "Code Value": decend_CPT_values, "Code Description": decend_CPT_names})
CPT_trans_decend = pd.concat([CPT_decend, CPT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# This pulls the CUI code for UMLS
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
        
loinc_df = pd.DataFrame({"Data Concept": "Procedure Code", "Data Sub-Concept": "N/A", "Coding Standard": vocab_type_4, "Code Value": code_4, "Code Description": name_4})

# Drop any codes that may have been picked up that are not LNC codes
loinc_df = loinc_df[loinc_df['Coding Standard'] == "LNC"]

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

loinc_trans_df = pd.DataFrame({"Data Concept": "Observation Code", "Data Sub-Concept": LOINC_term_type, "Coding Standard": LOINC_root, "Code Value": LOINC_code, "Code Description": LOINC_name})

# Combine the CPT and LOINC Transformed and Decendents DataFrames
CPT_LOINC_trans_decend = pd.concat([loinc_trans_df, CPT_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)


# Combine SNOMEDCT, ICD10, CPT, and LOINC Transformed and Decendents DataFrames Together 
SNOMEDCT_ICD10_CPT_LOINC_trans_decend = pd.concat([CPT_LOINC_trans_decend, SNOMEDCT_ICD10_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)


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
SNOMEDCT_ICD10_CPT_LOINC_trans_decend.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")


