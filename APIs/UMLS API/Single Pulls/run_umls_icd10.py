"""
This script ingests a CSV file of condition diagnosis and symptom keywords and 
returns and Excel file of ICD-10 codes that are associated with the inputted keywords
Resources: 
- [Keywords template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) # pylint: disable=line-too-long
"""

# Imports
from json.decoder import JSONDecodeError
import requests # pylint: disable=import-error
import pandas as pd # pylint: disable=import-error

## CHANGE INPUTS HERE ##
API_KEY = 'YOUR API KEY HERE'

# Output Excel Sheet Name
CONDITION = 'CONDITION NAME'

# Input Excel Sheet with Keywords Name
CSV_FILE_INPUT_NAME = 'CONDITION KEYWORDS FILE NAME'

## END OF REQUESTED INPUTS ##
VERSION = 'current'
BASE_URI = "https://uts-ws.nlm.nih.gov"

# Keyword Column Name
COLUMN_NAME = 'Keyword'

# Read the Excel file
df = pd.read_csv('input/' + CSV_FILE_INPUT_NAME + '.csv')
df = df[(df["Data Concept"] == "Diagnosis")
        | (df["Data Concept"] == "Symptom")]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
df = df.groupby('Keyword').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first'  # Retain 'Code Set' as it doesn't need concatenation
}).reset_index()

# Extract the column as a Pandas Series
column_series = df[COLUMN_NAME]

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
for x in range(len(names)): # pylint: disable=consider-using-enumerate
    value = names[x]
    STRING = string_list[x]
    DC_code = df["VASRD Code"][df['Keyword'] == STRING].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == STRING].to_list()[0]
    data_concpet = df['Data Concept'][df['Keyword'] == STRING].to_list()[0]

    URL = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={value}&maxList=500" # pylint: disable=line-too-long
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
                keyword_ICD_10.extend([STRING] * count)
                cfr_criteria_ICD_10.extend([CFR_criteria] * count)
                data_concept_ICD_10.extend([data_concpet] * count)
        except requests.exceptions.JSONDecodeError:
            print(f"Error parsing JSON for {value}")
    else:
        print(
            f"Error: Received status code {response.status_code} for keyword: {value}")

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

for x in range(len(string_list)): # pylint: disable=consider-using-enumerate
    STRING = str(string_list[x])
    # Precompute metadata for this keyword to avoid repeated DataFrame
    # filtering.
    DC_code = df["VASRD Code"][df['Keyword'] == STRING].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == STRING].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == STRING].to_list()[0]
    CONTENT_ENDPOINT = "/rest/search/" + VERSION
    FULL_URL = BASE_URI + CONTENT_ENDPOINT
    PAGE = 0

    try:
        while True:
            PAGE += 1
            query = {
                'string': STRING,
                'apiKey': API_KEY,
                'pageNumber': PAGE,
                'includeObsolete': 'true',
                'sabs': "ICD10"
            }
            r = requests.get(FULL_URL, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs = r.json()

            # Safely extract the results list.
            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                break
            count = len(items)

            # Use list comprehension to extend constant lists:
            keyword_value_2.extend([STRING] * count)
            dc_code_2.extend([DC_code] * count)
            cfr_criteria_2.extend([CFR_criteria] * count)
            data_concept_2.extend([data_concept] * count)

            # Use list comprehensions to extract values from each item.
            code_2.extend([item['ui'] for item in items])
            name_2.extend([item['name'] for item in items])
            vocab_type_2.extend([item['rootSource'] for item in items])
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error processing keyword {STRING}: {e}")
        continue  # Skip this CUI and continue with the next one

icd_df = pd.DataFrame({"VASRD Code": dc_code_2,
                       "Data Concept": data_concept_2,
                       "CFR Criteria": cfr_criteria_2,
                       "Code Set": vocab_type_2,
                       "Code": code_2,
                       "Code Description": name_2,
                       "Keyword": keyword_value_2})

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR
# Criteria', and 'Keyword' by a semicolon if there are multiple entries
# for the same keyword
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

SABS = 'ICD10'
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

    PAGE = 0

    while True:
        PAGE += 1
        PATH = '/search/' + VERSION
        query = {
            'apiKey': API_KEY,
            'string': cui,
            'sabs': SABS,
            'returnIdType': 'code',
            'pageNumber': PAGE}
        try:
            output = requests.get(BASE_URI + PATH, params=query)
            output.encoding = 'utf-8'
            outputJson = output.json()

            # Safely extract the "results" list:
            results = (([outputJson['result']])[0])['results']

            if len(results) == 0:
                break

            count = len(results)
            # Use list comprehensions to extend the lists with constant values
            # repeated for each item in results.
            ICD_10_keyword.extend([keyword_value] * count)
            ICD_10_VASRD_Code.extend([dc_code] * count)
            ICD_10_CFR_criteria.extend([cfr_criteria] * count)
            ICD_10_data_concept.extend([data_concept] * count)

            # For values coming from each item, use list comprehensions:
            ICD10_code.extend([item['ui'] for item in results])
            ICD10_name.extend([item['name'] for item in results])
            ICD10_root.extend([item['rootSource'] for item in results])

        except JSONDecodeError:
            print(
                f"JSONDecodeError encountered in ICD-10 pull for CUI: {cui}. Skipping this entry.")
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

for x in range(len(ICD10_code)): # pylint: disable=consider-using-enumerate
    SOURCE = 'ICD10'
    STRING = icd10_trans_df["Keyword"].to_list()[x]
    DC_code = icd10_trans_df["VASRD Code"][icd10_trans_df['Keyword'] == STRING].to_list()[
        0]
    CFR_criteria = icd10_trans_df['CFR Criteria'][icd10_trans_df['Keyword'] == STRING].to_list()[
        0]
    data_concept = icd10_trans_df['Data Concept'][icd10_trans_df['Keyword'] == STRING].to_list()[
        0]
    IDENTIFIER = str(ICD10_code[x])
    OPERATION = 'children'
    CONTENT_ENDPOINT = "/rest/content/" + VERSION + \
        "/source/" + SOURCE + "/" + IDENTIFIER + "/" + OPERATION

    PAGE_NUMBER = 0

    try:
        while True:
            PAGE_NUMBER += 1
            query = {'apiKey': API_KEY, 'pageNumber': PAGE_NUMBER}
            r = requests.get(BASE_URI + CONTENT_ENDPOINT, params=query)
            r.encoding = 'utf-8'
            items = r.json()
            if r.status_code != 200:
                break
            decend_ICD_10_keyword_value.extend([STRING] * len(items["result"]))
            decend_ICD_10_VASRD_Code.extend([DC_code] * len(items["result"]))
            decend_ICD_10_CFR_criteria.extend(
                [CFR_criteria] * len(items["result"]))
            decend_ICD_10_data_concept.extend(
                [data_concept] * len(items["result"]))
            decend_ICD10_values.extend([result["ui"]
                                       for result in items["result"]])
            decend_ICD10_names.extend([result["name"]
                                      for result in items["result"]])
            decend_ICD10_root.extend([result["rootSource"]
                                     for result in items["result"]])
    except Exception as except_error: # pylint: disable=broad-exception-caught
        print(f"Error processing CUI code {IDENTIFIER}: {e}")

ICD10_decend = pd.DataFrame({"VASRD Code": decend_ICD_10_VASRD_Code,
                             "Data Concept": decend_ICD_10_data_concept,
                             "CFR Criteria": decend_ICD_10_CFR_criteria,
                             "Code Set": decend_ICD10_root,
                             "Code": decend_ICD10_values,
                             "Code Description": decend_ICD10_names,
                             "Keyword": decend_ICD_10_keyword_value})

ICD10_trans_decend = pd.concat(
    [ICD10_decend, icd10_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Combine the ICD10 pull from a different API and merge it with the UMLS pull
ICD10_full = pd.concat([clin_table_test_pd, ICD10_trans_decend.loc[:]]
                       ).drop_duplicates().reset_index(drop=True)

# Filter rows where 'Code' contains a decimal point
ICD10_full_filtered = ICD10_full[ICD10_full['Code'].str.contains(r'\.')]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
ICD10_full_grouped = ICD10_full_filtered.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

# Replace 'ICD10' with 'ICD-10' in the 'Code Set' column
ICD10_full_grouped['Code Set'] = ICD10_full_grouped['Code Set'].replace(
    'ICD10', 'ICD-10')
ICD10_full_grouped = ICD10_full_grouped.reindex(
    [
        "VASRD Code",
        "CFR Criteria",
        "Code Set",
        "Code",
        "Code Description",
        "Keyword",
        "Data Concept"],
    axis=1)

# Save file
OUTPATH = 'output/'
FILE_NAME = f"{CONDITION}_icd10_codes.xlsx"
ICD10_full_grouped.to_excel(OUTPATH + FILE_NAME)

# Print a message indicating where the file is saved
print(f"Excel file '{FILE_NAME}' saved in the output folder.")
