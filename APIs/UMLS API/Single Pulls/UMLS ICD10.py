## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Condition = "Condition"

#Input Excel Sheet with Keywords Name
csv_file_input_name = 'Condition Keywords'


## End of Requested Inputs ##
# Imports
import requests 
import pandas as pd
from json.decoder import JSONDecodeError
version = 'current'
base_uri = "https://uts-ws.nlm.nih.gov"

# Keyword Column Name
column_name = 'Keyword'

# Read the Excel file
df = pd.read_csv('input/' + csv_file_input_name + '.csv')
df = df[(df["Data Concept"] == "Diagnosis") | (df["Data Concept"] == "Symptom")]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
df = df.groupby('Keyword').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first'  # Retain 'Code Set' as it doesn't need concatenation
}).reset_index()

# Extract the column as a Pandas Series
column_series = df[column_name]

# Convert the Pandas Series to a list
string_list = column_series.tolist()
# print(string_list)

# Clinical Tables Supplemental ICD-10 API Call
clin_table_ICD10_code = []
clin_table_ICD10_name = []
dc_code_ICD_10 = []
keyword_ICD_10 = []
data_concept_ICD_10 = []
cfr_criteria_ICD_10 = []
names = [item.replace(" ", "_") for item in string_list]

# Additional API to supplement UMLS ICD10 API call
for x in range(len(names)):
    value = names[x]
    string = string_list[x]
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concpet = df['Data Concept'][df['Keyword'] == string].to_list()[0]

    URL = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={value}&maxList=500"
    response = requests.get(URL)

    if response.status_code == 200:
        try:
            variable = response.json()
            # Ensure the expected structure is present in the response
            if len(variable) > 3 and variable[3]:
                count = len(variable[3])
                clin_table_ICD10_code.extend([item[0] for item in variable[3]])
                clin_table_ICD10_name.extend([item[1] for item in variable[3]])
                dc_code_ICD_10.extend([DC_code] * count)
                keyword_ICD_10.extend([string] * count)
                cfr_criteria_ICD_10.extend([CFR_criteria] * count)
                data_concept_ICD_10.extend([data_concpet] * count)
        except requests.exceptions.JSONDecodeError:
            print(f"Error parsing JSON for {value}")
    else:
        print(f"Error: Received status code {response.status_code} for keyword: {value}")

# Create DataFrame and drop duplicates
clin_table_test_pd = pd.DataFrame({
    "VASRD Code": dc_code_ICD_10, 
    "Data Concept": data_concept_ICD_10, 
    "CFR Criteria": cfr_criteria_ICD_10, 
    "Code Set": "ICD-10", 
    "Code": clin_table_ICD10_code, 
    "Code Description": clin_table_ICD10_name, 
    "Keyword": keyword_ICD_10
}).drop_duplicates().reset_index(drop=True)

# Start of UMLS API call
# Pulls UMLS CUI codes from the UMLS API using the keyword input

code_2 = []
name_2 = [] 
vocab_type_2 = []
dc_code_2 = []
cfr_criteria_2 = []
data_concept_2 = []
keyword_value_2 = []

for x in range(len(string_list)):
    string = str(string_list[x])
    # Precompute metadata for this keyword to avoid repeated DataFrame filtering.
    DC_code = df["VASRD Code"][df['Keyword'] == string].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == string].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == string].to_list()[0]
    content_endpoint = "/rest/search/" + version
    full_url = base_uri + content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {
                'string': string,
                'apiKey': apikey,
                'pageNumber': page,
                'includeObsolete': 'true',
                'sabs': "ICD10"
            }
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs = r.json()

            # Safely extract the results list.
            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                break
            count = len(items)

            # Use list comprehension to extend constant lists:
            keyword_value_2.extend([string] * count)
            dc_code_2.extend([DC_code] * count)
            cfr_criteria_2.extend([CFR_criteria] * count)
            data_concept_2.extend([data_concept] * count)

            # Use list comprehensions to extract values from each item.
            code_2.extend([item['ui'] for item in items])
            name_2.extend([item['name'] for item in items])
            vocab_type_2.extend([item['rootSource'] for item in items])
    except Exception as e:
        print(f"Error processing keyword {string}: {e}")
        continue  # Skip this CUI and continue with the next one
        
icd_df = pd.DataFrame({"VASRD Code": dc_code_2, 
                       "Data Concept": data_concept_2,
                       "CFR Criteria": cfr_criteria_2, 
                       "Code Set": vocab_type_2, 
                       "Code": code_2, 
                       "Code Description": name_2, 
                       "Keyword": keyword_value_2})

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR Criteria', and 'Keyword' by a semicolon if there are multiple entries for the same keyword
icd_df = icd_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
}).reset_index()

# Converts the CUI Codes from the chunk above into ICD10 Codes
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
    
    while True:
        page += 1
        path = '/search/' + version
        query = {'apiKey': apikey, 'string': cui, 'sabs': sabs, 'returnIdType': 'code', 'pageNumber': page}
        try:
            output = requests.get(base_uri + path, params=query)
            output.encoding = 'utf-8'
            outputJson = output.json()

            # Safely extract the "results" list:
            results = (([outputJson['result']])[0])['results']

            if len(results) == 0:
                break

            count = len(results)
            # Use list comprehensions to extend the lists with constant values repeated for each item in results.
            ICD_10_keyword.extend([keyword_value] * count)
            ICD_10_VASRD_Code.extend([dc_code] * count)
            ICD_10_CFR_criteria.extend([cfr_criteria] * count)
            ICD_10_data_concept.extend([data_concept] * count)

            # For values coming from each item, use list comprehensions:
            ICD10_code.extend([item['ui'] for item in results])
            ICD10_name.extend([item['name'] for item in results])
            ICD10_root.extend([item['rootSource'] for item in results])
        
        except JSONDecodeError:
            print(f"JSONDecodeError encountered in ICD-10 pull for CUI: {cui}. Skipping this entry.")
            break  # Exit the while loop for this `cui` and proceed to the next one

icd10_trans_df = pd.DataFrame({
    "VASRD Code": ICD_10_VASRD_Code, 
    "Data Concept": ICD_10_data_concept,
    "CFR Criteria": ICD_10_CFR_criteria,
    "Code Set": ICD10_root, 
    "Code": ICD10_code, 
    "Code Description": ICD10_name, 
    "Keyword": ICD_10_keyword
})

# Get Decendents of ICD10
decend_ICD10_names = []
decend_ICD10_values = []
decend_ICD10_root = []
decend_ICD_10_VASRD_Code = []
decend_ICD_10_CFR_criteria = []
decend_ICD_10_data_concept = []
decend_ICD_10_keyword_value = []

for x in range(len(ICD10_code)):
    source = 'ICD10'
    string = icd10_trans_df["Keyword"].to_list()[x]
    DC_code = icd10_trans_df["VASRD Code"][icd10_trans_df['Keyword'] == string].to_list()[0]
    CFR_criteria = icd10_trans_df['CFR Criteria'][icd10_trans_df['Keyword'] == string].to_list()[0]
    data_concept = icd10_trans_df['Data Concept'][icd10_trans_df['Keyword'] == string].to_list()[0]
    identifier = str(ICD10_code[x])
    operation = 'children'
    content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/"+operation

    pageNumber=0

    try:
        while True:
            pageNumber += 1
            query = {'apiKey':apikey,'pageNumber':pageNumber}
            r = requests.get(base_uri+content_endpoint,params=query)
            r.encoding = 'utf-8'
            items  = r.json()
            if r.status_code != 200:
                if pageNumber == 1:
                    break
                else:
                    break
            decend_ICD_10_keyword_value.extend([string] * len(items["result"]))
            decend_ICD_10_VASRD_Code.extend([DC_code] * len(items["result"]))
            decend_ICD_10_CFR_criteria.extend([CFR_criteria] * len(items["result"]))
            decend_ICD_10_data_concept.extend([data_concept] * len(items["result"]))
            decend_ICD10_values.extend([result["ui"] for result in items["result"]])
            decend_ICD10_names.extend([result["name"] for result in items["result"]])
            decend_ICD10_root.extend([result["rootSource"] for result in items["result"]])
    except Exception as except_error:
        print(except_error)
        
ICD10_decend = pd.DataFrame({"VASRD Code": decend_ICD_10_VASRD_Code, 
                             "Data Concept": decend_ICD_10_data_concept,
                             "CFR Criteria": decend_ICD_10_CFR_criteria, 
                             "Code Set": decend_ICD10_root, 
                             "Code": decend_ICD10_values, 
                             "Code Description": decend_ICD10_names, 
                             "Keyword": decend_ICD_10_keyword_value})

ICD10_trans_decend = pd.concat([ICD10_decend, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Combine the ICD10 pull from a different API and merge it with the UMLS pull 
ICD10_full = pd.concat([clin_table_test_pd, ICD10_trans_decend.loc[:]]).drop_duplicates().reset_index(drop=True)

# Filter rows where 'Code' contains a decimal point
ICD10_full_filtered = ICD10_full[ICD10_full['Code'].str.contains(r'\.')]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and 'CFR Criteria' by a semicolon if there are multiple entries for the same keyword
ICD10_full_grouped = ICD10_full_filtered.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

# Replace 'ICD10' with 'ICD-10' in the 'Code Set' column
ICD10_full_grouped['Code Set'] = ICD10_full_grouped['Code Set'].replace('ICD10', 'ICD-10')
ICD10_full_grouped = ICD10_full_grouped.reindex(["VASRD Code", "CFR Criteria", "Code Set", "Code", "Code Description", "Keyword", "Data Concept"], axis=1)

## Save file
outpath = 'output/'
file_name = f"{Condition}_icd10_codes.xlsx"
ICD10_full_grouped.to_excel(outpath + file_name)

# Print a message indicating where the file is saved
print(f"Excel file '{file_name}' saved in the output folder.")