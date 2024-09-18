## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Condition = "Finger"

#Input Excel Sheet with Keywords Name
excel_file_input_name = 'Finger Keywords'

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
df = df[df["Code Set"] == "CPT"]

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
                keyword_value_3.append(string)
                dc_code_3.append(DC_code)
                cfr_criteria_3.append(CFR_criteria)
                data_concept_3.append(data_concept)
                code_3.append(result['ui'])
                name_3.append(result['name'])
                vocab_type_3.append(result['rootSource'])

    except Exception as except_error:
        print(except_error)
        
cpt_df = pd.DataFrame({"VASRD Code": dc_code_3, "Data Concept": data_concept_3, "CFR Criteria": cfr_criteria_3, "Code Set": vocab_type_3, "Code": code_3, "Code Description": name_3, "Keyword": keyword_value_3})

# Converts the CPT CUI Codes from the chunk above into CPT Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = cpt_df["Code"]
dc_code_list = cpt_df["VASRD Code"]
cfr_criteria_list = cpt_df["CFR Criteria"]
data_concept_list = cpt_df["Data Concept"]
keyword_value_list = cpt_df["Keyword"]

sabs = 'CPT'
CPT_name = []
CPT_code = []
CPT_root = []
CPT_DC_Code = []
CPT_CFR_criteria = []
CPT_data_concept = []
CPT_keyword = []

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
                CPT_keyword.append(keyword_value)
                CPT_DC_Code.append(dc_code)
                CPT_CFR_criteria.append(cfr_criteria)
                CPT_data_concept.append(data_concept)
                CPT_code.append(item['ui'])
                CPT_name.append(item['name'])
                CPT_root.append(item['rootSource'])

CPT_trans_df = pd.DataFrame({"VASRD Code": CPT_DC_Code, "Data Concept": CPT_data_concept, "CFR Criteria": CPT_CFR_criteria, "Code Set": CPT_root, "Code": CPT_code, "Code Description": CPT_name, "Keyword": CPT_keyword})

# Get Children of CPT
decend_CPT_names = []
decend_CPT_values = []
decend_CPT_root = []
decend_CPT_DC_Code = []
decend_CPT_CFR_criteria = []
decend_CPT_data_concept = []
decend_CPT_keyword_value = []

for x in np.arange(0,len(CPT_code),1):
    source = 'CPT'
    string = CPT_keyword[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
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
                decend_CPT_keyword_value.append(string)
                decend_CPT_DC_Code.append(dc_code)
                decend_CPT_CFR_criteria.append(cfr_criteria)
                decend_CPT_data_concept.append(data_concept)
                decend_CPT_values.append(result["ui"])
                decend_CPT_names.append(result["name"])
                decend_CPT_root.append(result["rootSource"])

    except Exception as except_error:
        print(except_error)
        
CPT_decend = pd.DataFrame({"VASRD Code": decend_CPT_DC_Code, "Data Concept": decend_CPT_data_concept, "CFR Criteria": decend_CPT_CFR_criteria, "Code Set": decend_CPT_root, "Code": decend_CPT_values, "Code Description": decend_CPT_names, "Keyword": decend_CPT_keyword_value})

CPT_trans_decend = pd.concat([CPT_decend, CPT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
CPT_full_grouped = CPT_trans_decend.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

## Save file
outpath = 'output/'
file_name = f"{Condition}_cpt_codes.xlsx"
CPT_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")