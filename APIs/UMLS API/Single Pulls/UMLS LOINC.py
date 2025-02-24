## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Condition = "Finger LOINC Test"

#Input Excel Sheet with Keywords Name
excel_file_input_name = 'Finger Keywords'

## End of Requested Inputs ##

# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
from json.decoder import JSONDecodeError
version = 'current'

# Keyword Column Name
column_name = 'Keyword'
## End of Requested Inputs ##

# Read the Excel file
df = pd.read_excel('input/' + excel_file_input_name + '.xlsx')
df = df[df["Code Set"] == "LOINC"]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
df_combined = df.groupby('Keyword').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first'  # Retain 'Code Set' as it doesn't need concatenation
}).reset_index()

# Display the resulting DataFrame
df = df_combined

# Extract the column as a Pandas Series
column_series = df[column_name]

# Convert the Pandas Series to a list and exclude the column name as the first element
column_list = column_series.tolist()

string_list = column_list

# Now column_list contains the column data with the column name as the first element
print(string_list)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_4 = []
name_4 = [] 
vocab_type_4 = []
dc_code_4 = []
cfr_criteria_4 = []
data_concept_4 = []
keyword_value_4 = []

for x in np.arange(0, len(string_list),1):
    string = str(string_list[x])
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
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
                keyword_value_4.append(string)
                dc_code_4.append(DC_code)
                cfr_criteria_4.append(CFR_criteria)
                data_concept_4.append(data_concept)
                code_4.append(result['ui'])
                name_4.append(result['name'])
                vocab_type_4.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
loinc_df = pd.DataFrame({"VASRD Code": dc_code_4, "Data Concept": data_concept_4, "CFR Criteria": cfr_criteria_4, "Code Set": vocab_type_4, "Code": code_4, "Code Description": name_4, "Keyword": keyword_value_4})

# Converts the CPT CUI Codes from the chunk above into CPT Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = loinc_df["Code"]
dc_code_list = loinc_df["VASRD Code"]
cfr_criteria_list = loinc_df["CFR Criteria"]
data_concept_list = loinc_df["Data Concept"]
keyword_value_list = loinc_df["Keyword"]

sabs = 'LNC'
LOINC_name = []
LOINC_code = []
LOINC_root = []
LOINC_DC_Code = []
LOINC_CFR_criteria = []
LOINC_data_concept = []
LOINC_keyword = []

for idx, cui in enumerate(cui_list):
        dc_code = dc_code_list[idx]
        cfr_criteria = cfr_criteria_list[idx]
        data_concept = data_concept_list[idx]
        keyword_value = keyword_value_list[idx]
        
        page = 0
        
        # o.write('SEARCH CUI: ' + cui + '\n' + '\n')
        
        while True:
            page += 1
            path = '/search/'+version
            query = {'apiKey':apikey, 'string':cui, 'sabs':sabs, 'ttys': 'LN,LC', 'returnIdType':'code', 'pageNumber':page}
            try:
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
                    LOINC_keyword.append(keyword_value)
                    LOINC_DC_Code.append(dc_code)
                    LOINC_CFR_criteria.append(cfr_criteria)
                    LOINC_data_concept.append(data_concept)
                    LOINC_code.append(item['ui'])
                    LOINC_name.append(item['name'])
                    LOINC_root.append(item['rootSource'])
            except JSONDecodeError:
                print(f"JSONDecodeError encountered for CUI: {cui}. Skipping this entry.")
                break  # Exit the while loop for this `cui` and proceed to the next one
LOINC_trans_df = pd.DataFrame({"VASRD Code": LOINC_DC_Code, "Data Concept": LOINC_data_concept, "CFR Criteria": LOINC_CFR_criteria, "Code Set": LOINC_root, "Code": LOINC_code, "Code Description": LOINC_name, "Keyword": LOINC_keyword})

# Get Children of CPT
decend_LOINC_names = []
decend_LOINC_values = []
decend_LOINC_root = []
decend_LOINC_DC_Code = []
decend_LOINC_CFR_criteria = []
decend_LOINC_data_concept = []
decend_LOINC_keyword_value = []

for x in np.arange(0,len(LOINC_code),1):
    source = 'LNC'
    string = LOINC_keyword[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
    identifier = str(LOINC_code[x])
    operation = 'children'
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/"+operation

    pageNumber=0

    try:
        while True:
            pageNumber += 1
            query = {'apiKey':apikey,'ttys': 'LN,LC','pageNumber':pageNumber}
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
                decend_LOINC_keyword_value.append(string)
                decend_LOINC_DC_Code.append(dc_code)
                decend_LOINC_CFR_criteria.append(cfr_criteria)
                decend_LOINC_data_concept.append(data_concept)
                decend_LOINC_values.append(result["ui"])
                decend_LOINC_names.append(result["name"])
                decend_LOINC_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
LOINC_decend = pd.DataFrame({"VASRD Code": decend_LOINC_DC_Code, "Data Concept": decend_LOINC_data_concept, "CFR Criteria": decend_LOINC_CFR_criteria, "Code Set": decend_LOINC_root, "Code": decend_LOINC_values, "Code Description": decend_LOINC_names, "Keyword": decend_LOINC_keyword_value})

LOINC_trans_decend = pd.concat([LOINC_decend, LOINC_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
LOINC_full_grouped = LOINC_trans_decend.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

# Replace 'LNC' with 'LOINC' in the 'Code Set' column
LOINC_full_grouped['Code Set'] = LOINC_full_grouped['Code Set'].replace('LNC', 'LOINC')
LOINC_full_grouped = LOINC_full_grouped.reindex(["VASRD Code", "CFR Criteria", "Code Set", "Code", "Code Description", "Keyword", "Data Concept"], axis=1)

# Filter out codes containing non-numeric values (allow hyphen)
LOINC_full_grouped = LOINC_full_grouped[LOINC_full_grouped['Code'].str.match(r'^[\d-]+$')]

## Save file
outpath = 'output/'
file_name = f"{Condition}_LOINC_codes.xlsx"
LOINC_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")