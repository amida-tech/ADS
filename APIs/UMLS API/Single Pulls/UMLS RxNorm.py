## CHANGE INPUTS HERE ##
apikey = 'Your API Key Here'

#Output Excel Sheet Name
Condition = "Test Condition"

#Input Excel Sheet with Keywords Name
excel_file_input_name = 'Test Keywords'

## End of Requested Inputs ##

# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import os
version = 'current'

# Keyword Column Name
column_name = 'Keyword'

## End of Requested Inputs ##

# Read the Excel file
df = pd.read_excel('input/' + excel_file_input_name + '.xlsx')
df = df[df["Data Concept"] == "Medication"]

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
# You will need to convert these CUI codes from UMLS codes into their associated SNOMEDCT, ICD10, LNC, RxNorm, etc codes

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
            query['sabs'] = "RXNORM"
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
        
RxNorm_df = pd.DataFrame({"VASRD Code": dc_code_4, "Data Concept": data_concept_4, "CFR Criteria": cfr_criteria_4, "Code Set": vocab_type_4, "Code": code_4, "Code Description": name_4, "Keyword": keyword_value_4})

# Converts the RxNorm CUI Codes from the chunk above into RxNorm Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = RxNorm_df["Code"]
dc_code_list = RxNorm_df["VASRD Code"]
cfr_criteria_list = RxNorm_df["CFR Criteria"]
data_concept_list = RxNorm_df["Data Concept"]
keyword_value_list = RxNorm_df["Keyword"]

sabs = 'RXNORM'
RxNorm_name = []
RxNorm_code = []
RxNorm_root = []
RxNorm_DC_Code = []
RxNorm_CFR_criteria = []
RxNorm_data_concept = []
RxNorm_keyword = []

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
                RxNorm_keyword.append(keyword_value)
                RxNorm_DC_Code.append(dc_code)
                RxNorm_CFR_criteria.append(cfr_criteria)
                RxNorm_data_concept.append(data_concept)
                RxNorm_code.append(item['ui'])
                RxNorm_name.append(item['name'])
                RxNorm_root.append(item['rootSource'])

RxNorm_trans_df = pd.DataFrame({"VASRD Code": RxNorm_DC_Code, "Data Concept": RxNorm_data_concept, "CFR Criteria": RxNorm_CFR_criteria, "Code Set": RxNorm_root, "Code": RxNorm_code, "Code Description": RxNorm_name, "Keyword": RxNorm_keyword})

RxNorm_trans_df_clean = RxNorm_trans_df.drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
RxNorm_full_grouped = RxNorm_trans_df_clean.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

## Save file
outpath = 'output/'
file_name = f"{Condition}_RxNorm_codes.xlsx"
RxNorm_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")