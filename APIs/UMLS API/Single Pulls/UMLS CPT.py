#!/usr/bin/env python
# coding: utf-8

## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'
string_list = ["Spirometry"]
Excel_Sheet_Name = "Asthma CPT Sheet"


## DO NOT CHANGE BELOW THIS LINE ##
import requests 
import argparse
import numpy as np
import pandas as pd
version = 'current'

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



# Get Children of CPT
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

excel_name = f'{Excel_Sheet_Name}' + ".xlsx"

CPT_trans_decend.to_excel(excel_name)

