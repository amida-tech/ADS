## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Condition = "Test Condition SNOMED"

#Input Excel Sheet with Keywords Name
excel_file_input_name = 'Test Keywords'

## End of requested inputs ##

# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
version = 'current'

# Keyword Column Name
column_name = 'Keyword'

# Read the Excel file
df = pd.read_excel('input/' + excel_file_input_name + '.xlsx')

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
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, SNOMED_CT, etc codes

code_3 = []
name_3 = [] 
vocab_type_3 = []
dc_code_3 = []
cfr_criteria_3 = []
data_concept_3 = []
keyword_value_3 = []

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
                keyword_value_3.append(string)
                dc_code_3.append(DC_code)
                cfr_criteria_3.append(CFR_criteria)
                data_concept_3.append(data_concept)
                code_3.append(result['ui'])
                name_3.append(result['name'])
                vocab_type_3.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
SNOMED_CT_df = pd.DataFrame({"VASRD Code": dc_code_3, "Data Concept": data_concept_3, "CFR Criteria": cfr_criteria_3, "Code Set": vocab_type_3, "Code": code_3, "Code Description": name_3, "Keyword": keyword_value_3})

# Converts the SNOMED_CT CUI Codes from the chunk above into SNOMED_CT Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = SNOMED_CT_df["Code"]
dc_code_list = SNOMED_CT_df["VASRD Code"]
cfr_criteria_list = SNOMED_CT_df["CFR Criteria"]
data_concept_list = SNOMED_CT_df["Data Concept"]
keyword_value_list = SNOMED_CT_df["Keyword"]

sabs = 'SNOMEDCT_US'
SNOMED_CT_name = []
SNOMED_CT_code = []
SNOMED_CT_root = []
SNOMED_CT_DC_Code = []
SNOMED_CT_CFR_criteria = []
SNOMED_CT_data_concept = []
SNOMED_CT_keyword = []

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
                SNOMED_CT_keyword.append(keyword_value)
                SNOMED_CT_DC_Code.append(dc_code)
                SNOMED_CT_CFR_criteria.append(cfr_criteria)
                SNOMED_CT_data_concept.append(data_concept)
                SNOMED_CT_code.append(item['ui'])
                SNOMED_CT_name.append(item['name'])
                SNOMED_CT_root.append(item['rootSource'])

SNOMED_CT_trans_df = pd.DataFrame({"VASRD Code": SNOMED_CT_DC_Code, "Data Concept": SNOMED_CT_data_concept, "CFR Criteria": SNOMED_CT_CFR_criteria, "Code Set": SNOMED_CT_root, "Code": SNOMED_CT_code, "Code Description": SNOMED_CT_name, "Keyword": SNOMED_CT_keyword})

# Get Children of SNOMED_CT
decend_SNOMED_CT_names = []
decend_SNOMED_CT_values = []
decend_SNOMED_CT_root = []
decend_SNOMED_CT_DC_Code = []
decend_SNOMED_CT_CFR_criteria = []
decend_SNOMED_CT_data_concept = []
decend_SNOMED_CT_keyword_value = []

for x in np.arange(0,len(SNOMED_CT_code),1):
    source = 'SNOMED_CT'
    string = SNOMED_CT_keyword[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
    identifier = str(SNOMED_CT_code[x])
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
                decend_SNOMED_CT_keyword_value.append(string)
                decend_SNOMED_CT_DC_Code.append(dc_code)
                decend_SNOMED_CT_CFR_criteria.append(cfr_criteria)
                decend_SNOMED_CT_data_concept.append(data_concept)
                decend_SNOMED_CT_values.append(result["ui"])
                decend_SNOMED_CT_names.append(result["name"])
                decend_SNOMED_CT_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
SNOMED_CT_decend = pd.DataFrame({"VASRD Code": decend_SNOMED_CT_DC_Code, "Data Concept": decend_SNOMED_CT_data_concept, "CFR Criteria": decend_SNOMED_CT_CFR_criteria, "Code Set": decend_SNOMED_CT_root, "Code": decend_SNOMED_CT_values, "Code Description": decend_SNOMED_CT_names, "Keyword": decend_SNOMED_CT_keyword_value})

SNOMED_CT_trans_decend = pd.concat([SNOMED_CT_decend, SNOMED_CT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
SNOMED_CT_full_grouped = SNOMED_CT_trans_decend.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

## Save file
outpath = 'output/'
file_name = f"{Condition}_SNOMED_CT_codes.xlsx"
SNOMED_CT_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")