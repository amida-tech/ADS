## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "EXCEL SHEET NAME HERE"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'EXCEL SHEET NAME HERE.xlsx'


## End of Requested Inputs ##

# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
version = 'current'

# Keyword Column Name
column_name = 'Keywords'

# Read the Excel file
excel_file_path = excel_file_keywords
df = pd.read_excel(excel_file_path)
df = df[df["Code Set"] == "ICD-10"]

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

clin_table_ICD10_code = []
clin_table_ICD10_name = []
dc_code_ICD_10 = []
keyword_ICD_10 = []
data_concept_ICD_10 = []
cfr_criteria_ICD_10 = []
names = []

names = []

for x in np.arange(0, len(string_list),1):
    list_item = string_list[x]
    names.append(list_item.replace(" ", "_"))

# Get ICD10 Codes from another API source
# This is because UMLS is lacking alone in their ICD10 call

for x in np.arange(0, len(names),1):
    value = names[x]
    string = string_list[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concpet = df['Data Concept'][df['Keyword'] == string].to_list()[0]
    URL = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={value}&maxList=500"
    response = requests.get(URL)
    variable = response.json()
    
    for y in np.arange(0, len(variable[3]),1):
        clin_table_ICD10_code.append(variable[3][y][0])
        clin_table_ICD10_name.append(variable[3][y][1])
        dc_code_ICD_10.append(DC_code)
        keyword_ICD_10.append(string)
        cfr_criteria_ICD_10.append(CFR_criteria)
        data_concept_ICD_10.append(data_concpet)
        
clin_table_test_pd = pd.DataFrame({"VASRD Code": dc_code_ICD_10, "Data Concept": data_concept_ICD_10,"CFR Criteria": cfr_criteria_ICD_10, "Code Set": "ICD-10", "Code": clin_table_ICD10_code, "Code Description": clin_table_ICD10_name, "Keyword": keyword_ICD_10}).drop_duplicates().reset_index(drop=True)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_2 = []
name_2 = [] 
vocab_type_2 = []
dc_code_2 = []
cfr_criteria_2 = []
data_concept_2 = []
keyword_value_2 = []

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
                keyword_value_2.append(string)
                dc_code_2.append(DC_code)
                cfr_criteria_2.append(CFR_criteria)
                data_concept_2.append(data_concept)
                code_2.append(result['ui'])
                name_2.append(result['name'])
                vocab_type_2.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
icd_df = pd.DataFrame({"VASRD Code": dc_code_2, "Data Concept": data_concept_2,"CFR Criteria": cfr_criteria_2, "Code Set": "ICD-10", "Code": code_2, "Code Description": name_2, "Keyword": keyword_value_2})

# Converts the ICD10 CUI Codes from the chunk above into ICD10 Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = icd_df["Code"]
dc_code_list = icd_df["VASRD Code"]
cfr_criteria_list = icd_df["CFR Criteria"]
data_concept_list = icd_df["Data Concept"]
keyword_value_list = icd_df["Keyword"]

sabs = 'ICD10'
ICD10_name = []
ICD10_code = []
ICD10_root = []
ICD_10_VASRD_Code = []
ICD_10_CFR_criteria = []
ICD_10_data_concept = []
ICD_10_keyword = []

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
                ICD_10_keyword.append(keyword_value)
                ICD_10_VASRD_Code.append(dc_code)
                ICD_10_CFR_criteria.append(cfr_criteria)
                ICD_10_data_concept.append(data_concept)
                ICD10_code.append(item['ui'])
                ICD10_name.append(item['name'])
                ICD10_root.append(item['rootSource'])

icd10_trans_df = pd.DataFrame({"VASRD Code": ICD_10_VASRD_Code, "Data Concept": ICD_10_data_concept,"CFR Criteria": ICD_10_CFR_criteria, "Code Set": "ICD-10", "Code": ICD10_code, "Code Description": ICD10_name, "Keyword": ICD_10_keyword})

# Get Decendents of ICD10
decend_ICD10_names = []
decend_ICD10_values = []
decend_ICD10_root = []
decend_ICD_10_VASRD_Code = []
decend_ICD_10_CFR_criteria = []
decend_ICD_10_data_concept = []
decend_ICD_10_keyword_value = []

for x in np.arange(0,len(ICD10_code),1):
    source = 'ICD10'
    string = ICD_10_keyword[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
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
                decend_ICD_10_keyword_value.append(string)
                decend_ICD_10_VASRD_Code.append(DC_code)
                decend_ICD_10_CFR_criteria.append(CFR_criteria)
                decend_ICD_10_data_concept.append(data_concept)
                decend_ICD10_values.append(result["ui"])
                decend_ICD10_names.append(result["name"])
                decend_ICD10_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
ICD10_decend = pd.DataFrame({"VASRD Code": decend_ICD_10_VASRD_Code, "Data Concept": decend_ICD_10_data_concept,"CFR Criteria": decend_ICD_10_CFR_criteria, "Code Set": "ICD-10", "Code": decend_ICD10_values, "Code Description": decend_ICD10_names, "Keyword": decend_ICD_10_keyword_value})
ICD10_trans_decend = pd.concat([ICD10_decend, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Combine the ICD10 pull from a different API and merge it with the UMLS pull 
ICD10_full = pd.concat([clin_table_test_pd, ICD10_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)

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
ICD10_full.to_excel(excel_path, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the output folder.")

