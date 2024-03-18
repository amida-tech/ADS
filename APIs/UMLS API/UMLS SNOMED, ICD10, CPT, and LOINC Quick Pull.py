#!/usr/bin/env python
# coding: utf-8


## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'
string_list = ["Asthma", "with Asthma"]
Excel_Sheet_Name = "Asthma Sheet"


# Code Structure Outline 
# SNOMED-CT UMLS CUI 
# SNOMED-CT UMLS CUI:SNOMEDCT Code Transformation

# ICD10 UMLS CUI 
# ICD10 UMLS CUI:SNOMEDCT Code Transformation

# CPT UMLS CUI 
# CPT UMLS CUI:SNOMEDCT Code Transformation

# LNC UMLS CUI 
# LNC UMLS CUI:SNOMEDCT Code Transformation


## DO NOT CHANGE BELOW THIS LINE ##
import requests 
import argparse
import numpy as np
import pandas as pd
version = 'current'

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


# Combine the ICD10 pull from a different API and merge it with the UMLS pull 
ICD10_full = pd.concat([clin_table_test_pd, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)


# Combine the SNOMEDCT_US and ICD10 Transformed and Decendents DataFrames
SNOMEDCT_ICD10_trans_decend = pd.concat([snomed_trans_df, ICD10_full.loc[:]]).drop_duplicates().reset_index(drop=True)

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

# Combine the CPT and LOINC Transformed and Decendents DataFrames
CPT_LOINC_trans_decend = pd.concat([loinc_trans_df, CPT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Combine SNOMEDCT, ICD10, CPT, and LOINC Transformed and Decendents DataFrames Together 
SNOMEDCT_ICD10_CPT_LOINC_trans_df = pd.concat([CPT_LOINC_trans_decend, SNOMEDCT_ICD10_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)


excel_name = f'{Excel_Sheet_Name}' + ".xlsx"

SNOMEDCT_ICD10_CPT_LOINC_trans_df.to_excel(excel_name)


