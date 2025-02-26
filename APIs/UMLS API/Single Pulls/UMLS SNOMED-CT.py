## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Condition = "Condition Name"

#Input Excel Sheet with Keywords Name
csv_file_input_name = 'Condition Keywords'

## End of requested inputs ##

# Imports
import requests 
import argparse
import numpy as np
import pandas as pd
import json
import os
from json.decoder import JSONDecodeError
version = 'current'
base_uri = "https://uts-ws.nlm.nih.gov"

# Keyword Column Name
column_name = 'Keyword'

# Read the Excel file
df = pd.read_csv('input/' + csv_file_input_name + '.csv')
df = df[df["Data Concept"] != "Medication"]

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

# Convert the Pandas Series to a list
column_list = column_series.tolist()
string_list = column_list

# Uncomment below to see the list of inputted keywords
# print(string_list)

# This pulls the CUI code for UMLS

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
    content_endpoint = "/rest/search/"+version
    full_url = base_uri+content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {'string':string,'apiKey':apikey, 'pageNumber':page}
            query['includeObsolete'] = 'true'
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
        
            keyword_value_3.extend([string for _ in items])
            dc_code_3.extend([DC_code for _ in items])
            cfr_criteria_3.extend([CFR_criteria for _ in items])
            data_concept_3.extend([data_concept for _ in items])
            code_3.extend([result['ui'] for result in items])
            name_3.extend([result['name'] for result in items])
            vocab_type_3.extend([result['rootSource'] for result in items])

    except Exception as e:
        print(f"Error processing keyword {string}: {e}")
        continue  # Skip this CUI and continue with the next one
        
SNOMED_CT_df = pd.DataFrame({"VASRD Code": dc_code_3, "Data Concept": data_concept_3, "CFR Criteria": cfr_criteria_3, "Code Set": vocab_type_3, "Code": code_3, "Code Description": name_3, "Keyword": keyword_value_3})

# Uncomment below if you want to see the CUI dataframe
# SNOMED_CT_df

# Pull Semantic Types and Semantic Group URI 
# Read the list of CUI codes from the input file (one per line)
cui_list = SNOMED_CT_df["Code"]
results_list = []

# Loop through each CUI code and query the UMLS API
for cui in cui_list:
    # Build the endpoint URL for this CUI
    endpoint = f"/rest/content/{version}/CUI/{cui}"
    url = base_uri + endpoint
    params = {"apiKey": apikey}
    
    try:
        response = requests.get(url, params=params)
        response.encoding = "utf-8"
        response.raise_for_status()  # raise an error for non-200 responses
        json_data = response.json()
    except Exception as e:
        print(f"Error processing Semantic Type for CUI {cui}: {e}")
        continue  # Skip this CUI and continue with the next one
    
    # Extract the semantic type from the response
    result = json_data.get("result", {})
    semantic_types = result.get("semanticTypes", [])
    semantic_group_uri = result.get("semanticTypes", [])
    if semantic_types and len(semantic_types) > 0:
        semantic_type = semantic_types[0].get("name", "Not Found")
        semantic_uri = semantic_group_uri[0].get("uri", "Not Found")
    else:
        semantic_type = "Not Found"
        semantic_uri = "Not Found"
    
    results_list.append({
        "Code": cui,
        "Semantic Type": semantic_type,
        "Semantic Group URI": semantic_uri
    })

# Create a DataFrame from the results
semantic_types_df = pd.DataFrame(results_list)

# Uncomment below if you want to see the dataframe for the CUI codes, Semantic types, and Semantic Group URI
# semantic_types_df

# Find Semantic Group
semantic_group_list = []

for idx, row in semantic_types_df.iterrows():
    sem_uri = row["Semantic Group URI"]
    if sem_uri == "Not Found" or sem_uri.strip() == "":
        semantic_group_list.append("Not Found")
        continue

    # Build the full URL for the semantic group query.
    url = sem_uri
        
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        response.raise_for_status()
        json_data = response.json()
        
        stg = json_data.get("result", {}).get("semanticTypeGroup", {})
        class_type = stg.get("classType", "")
        if class_type == "SemanticGroup":
            expanded_form = stg.get("expandedForm", "Not Provided")
        else:
            expanded_form = "Not Provided"  # or "Flag for review"
        semantic_group_list.append(expanded_form)
    except requests.exceptions.JSONDecodeError:
        print(f"JSONDecodeError for Semantic Group (URI: {sem_uri}). Skipping this entry.")
        semantic_group_list.append("Error")
    except Exception as e:
        print(f"Error processing Semantic Group URI for {sem_uri}: {e}")
        semantic_group_list.append("Error")

# Add the new column to the DataFrame
semantic_types_df["Semantic Group"] = semantic_group_list

semantic_types_group_df = semantic_types_df.drop("Semantic Group URI", axis='columns').reindex(["Code", "Semantic Group", "Semantic Type"], axis=1)

# Uncomment below if you want to see a dataframe of the CUI code and it's corresponding Semantic Group and Semantic Type 
# semantic_types_group_df

#Merge above DF with original DF and update all below chunks accordingly
SNOMED_CT_df = pd.merge(SNOMED_CT_df, semantic_types_group_df[['Code', 'Semantic Group', 'Semantic Type']], on='Code', how='left')

# Uncomment below if you want to see the merged CUI dataframe with associated semantic types and groups attached
# SNOMED_CT_df

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR Criteria', and 'Keyword' by a semicolon if there are multiple entries for the same keyword
SNOMED_CT_df = SNOMED_CT_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
    'Semantic Group': 'first',
    'Semantic Type': 'first'
}).reset_index()

# Converts the SNOMED_CT CUI Codes from the chunk above into SNOMED_CT Codes
cui_list = SNOMED_CT_df["Code"]
dc_code_list = SNOMED_CT_df["VASRD Code"]
cfr_criteria_list = SNOMED_CT_df["CFR Criteria"]
data_concept_list = SNOMED_CT_df["Data Concept"]
keyword_value_list = SNOMED_CT_df["Keyword"]
semantic_type_list = SNOMED_CT_df["Semantic Type"]
semantic_group_list = SNOMED_CT_df["Semantic Group"]

sabs = 'SNOMEDCT_US'
SNOMED_CT_name = []
SNOMED_CT_code = []
SNOMED_CT_root = []
SNOMED_CT_DC_Code = []
SNOMED_CT_CFR_criteria = []
SNOMED_CT_data_concept = []
SNOMED_CT_keyword = []
SNOMED_CT_semantic_type = []
SNOMED_CT_semantic_group = []

for idx, cui in enumerate(cui_list):
    dc_code = dc_code_list[idx]
    cfr_criteria = cfr_criteria_list[idx]
    data_concept = data_concept_list[idx]
    keyword_value = keyword_value_list[idx]
    semantic_type = semantic_type_list[idx]
    semantic_group = semantic_group_list[idx]

    page = 0

    while True:
        page += 1
        path = '/search/' + version
        query = {'apiKey': apikey, 'string': cui, 'sabs': sabs, 'returnIdType': 'code', 'pageNumber': page}
        try:
            output = requests.get(base_uri + path, params=query)
            output.encoding = 'utf-8'
            # Parse the JSON output
            outputJson = output.json()

            results = (([outputJson['result']])[0])['results']

            if len(results) == 0:
                if page == 1:
                    break
                else:
                    break

            # Extend the lists with constant values repeated for each item in results
            count = len(results)
            SNOMED_CT_keyword.extend([keyword_value] * count)
            SNOMED_CT_DC_Code.extend([dc_code] * count)
            SNOMED_CT_CFR_criteria.extend([cfr_criteria] * count)
            SNOMED_CT_data_concept.extend([data_concept] * count)
            SNOMED_CT_semantic_type.extend([semantic_type] * count)
            SNOMED_CT_semantic_group.extend([semantic_group] * count)

            # For values coming from each item in results, use list comprehensions:
            SNOMED_CT_code.extend([item['ui'] for item in results])
            SNOMED_CT_name.extend([item['name'] for item in results])
            SNOMED_CT_root.extend([item['rootSource'] for item in results])

        except JSONDecodeError:
            print(f"JSONDecodeError encountered in SNOMED-CT pull for CUI: {cui}. Skipping this entry.")
            break  # Exit the while loop for this `cui` and proceed to the next one

SNOMED_CT_trans_df = pd.DataFrame({
    "VASRD Code": SNOMED_CT_DC_Code,
    "Data Concept": SNOMED_CT_data_concept,
    "CFR Criteria": SNOMED_CT_CFR_criteria,
    "Code Set": SNOMED_CT_root,
    "Code": SNOMED_CT_code,
    "Code Description": SNOMED_CT_name,
    "Keyword": SNOMED_CT_keyword, 
    "Semantic Group": SNOMED_CT_semantic_group, 
    "Semantic Type": SNOMED_CT_semantic_type
})

# Uncomment out below if you want to see the transformed CUI to SNOMED-CT dataframe 
# SNOMED_CT_trans_df

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR Criteria', and 'Keyword' by a semicolon if there are multiple entries for the same keyword
SNOMED_CT_full_grouped = SNOMED_CT_trans_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
    'Semantic Group': 'first',
    'Semantic Type': 'first'
}).reset_index()

# Replace 'SNOMEDCT_US' with 'SNOMED-CT' in the 'Code Set' column
SNOMED_CT_full_grouped['Code Set'] = SNOMED_CT_full_grouped['Code Set'].replace('SNOMEDCT_US', 'SNOMED-CT')
# Reorder columns 
SNOMED_CT_full_grouped = SNOMED_CT_full_grouped.reindex(["VASRD Code", "CFR Criteria", "Code Set", "Code", "Code Description", "Keyword", "Data Concept", "Semantic Group", "Semantic Type"], axis=1)

# Uncomment below if you want to see the expected output file before it is exported to excel
# SNOMED_CT_full_grouped

## Save file
outpath = 'output/'
file_name = f"{Condition}_SNOMED_CT_codes.xlsx"
SNOMED_CT_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")