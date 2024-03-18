#!/usr/bin/env python
# coding: utf-8

## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'
string_list = ["Asthma"]
Excel_Sheet_Name = "Asthma ICD10 Sheet"


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

excel_name = f'{Excel_Sheet_Name}' + ".xlsx"

ICD10_full.to_excel(excel_name)

