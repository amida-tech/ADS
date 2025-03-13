"""
This script ingests a CSV file of condition procedure keywords and 
returns and Excel file of CPT codes that are associated with the inputted keywords
Resources: 
- [Keywords template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) # pylint: disable=line-too-long
"""

# Imports
from json.decoder import JSONDecodeError
import requests
import pandas as pd

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
df = df[df["Data Concept"] == "Procedure"]

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
string_list = df[COLUMN_NAME].tolist()
# print(string_list)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their
# associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_3 = []
name_3 = []
vocab_type_3 = []
dc_code_3 = []
cfr_criteria_3 = []
data_concept_3 = []
keyword_value_3 = []

for x in range(len(string_list)): # pylint: disable=consider-using-enumerate
    STRING = str(string_list[x])
    DC_code = df["VASRD Code"][df['Keyword'] == STRING].to_list()[0]
    CFR_criteria = df['CFR Criteria'][df['Keyword'] == STRING].to_list()[0]
    data_concept = df['Data Concept'][df['Keyword'] == STRING].to_list()[0]
    CONTENT_ENDPOINT = "/rest/search/" + VERSION
    FULL_URL = BASE_URI + CONTENT_ENDPOINT
    PAGE = 0

    try:
        while True:
            PAGE += 1
            query = {'string': STRING, 'apiKey': API_KEY, 'pageNumber': PAGE}
            query['includeObsolete'] = 'true'
            query['sabs'] = "CPT"
            r = requests.get(FULL_URL, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs = r.json()

            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                break

            # Using list comprehension to append data
            keyword_value_3.extend([STRING] * len(items))
            dc_code_3.extend([DC_code] * len(items))
            cfr_criteria_3.extend([CFR_criteria] * len(items))
            data_concept_3.extend([data_concept] * len(items))
            code_3.extend([result['ui'] for result in items])
            name_3.extend([result['name'] for result in items])
            vocab_type_3.extend([result['rootSource'] for result in items])

    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error processing keyword {STRING}: {e}")
        continue  # Skip this CUI and continue with the next one

cpt_df = pd.DataFrame({"VASRD Code": dc_code_3,
                       "Data Concept": data_concept_3,
                       "CFR Criteria": cfr_criteria_3,
                       "Code Set": vocab_type_3,
                       "Code": code_3,
                       "Code Description": name_3,
                       "Keyword": keyword_value_3})

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR
# Criteria', and 'Keyword' by a semicolon if there are multiple entries
# for the same keyword
cpt_df = cpt_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
}).reset_index()

# Converts the CPT CUI Codes from the chunk above into CPT Codes
cui_list = cpt_df["Code"]
dc_code_list = cpt_df["VASRD Code"]
cfr_criteria_list = cpt_df["CFR Criteria"]
data_concept_list = cpt_df["Data Concept"]
keyword_value_list = cpt_df["Keyword"]

SABS = 'CPT'
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
            results = (([outputJson['result']])[0])['results']

            if len(results) == 0:
                break

            CPT_keyword.extend([keyword_value] * len(results))
            CPT_DC_Code.extend([dc_code] * len(results))
            CPT_CFR_criteria.extend([cfr_criteria] * len(results))
            CPT_data_concept.extend([data_concept] * len(results))
            CPT_code.extend([item['ui'] for item in results])
            CPT_name.extend([item['name'] for item in results])
            CPT_root.extend([item['rootSource'] for item in results])
        except JSONDecodeError:
            print(
                f"JSONDecodeError encountered for CUI: {cui}. Skipping this entry.")
            break  # Exit the while loop for this `cui` and proceed to the next one

CPT_trans_df = pd.DataFrame({"VASRD Code": CPT_DC_Code,
                             "Data Concept": CPT_data_concept,
                             "CFR Criteria": CPT_CFR_criteria,
                             "Code Set": CPT_root,
                             "Code": CPT_code,
                             "Code Description": CPT_name,
                             "Keyword": CPT_keyword})

# Get Decendents of CPT
decend_CPT_names = []
decend_CPT_values = []
decend_CPT_root = []
decend_CPT_VASRD_Code = []
decend_CPT_CFR_criteria = []
decend_CPT_data_concept = []
decend_CPT_keyword_value = []

for x in range(len(CPT_code)): # pylint: disable=consider-using-enumerate
    SOURCE = 'CPT'
    STRING = CPT_trans_df["Keyword"].to_list()[x]
    DC_code = CPT_trans_df["VASRD Code"][CPT_trans_df['Keyword'] == STRING].to_list()[
        0]
    CFR_criteria = CPT_trans_df['CFR Criteria'][CPT_trans_df['Keyword'] == STRING].to_list()[
        0]
    data_concept = CPT_trans_df['Data Concept'][CPT_trans_df['Keyword'] == STRING].to_list()[
        0]
    IDENTIFIER = str(CPT_code[x])
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
            decend_CPT_keyword_value.extend([STRING] * len(items["result"]))
            decend_CPT_VASRD_Code.extend([DC_code] * len(items["result"]))
            decend_CPT_CFR_criteria.extend(
                [CFR_criteria] * len(items["result"]))
            decend_CPT_data_concept.extend(
                [data_concept] * len(items["result"]))
            decend_CPT_values.extend([result["ui"]
                                     for result in items["result"]])
            decend_CPT_names.extend([result["name"]
                                    for result in items["result"]])
            decend_CPT_root.extend([result["rootSource"]
                                   for result in items["result"]])
    except Exception as except_error: # pylint: disable=broad-exception-caught
        print(except_error)

CPT_decend = pd.DataFrame({"VASRD Code": decend_CPT_VASRD_Code,
                           "Data Concept": decend_CPT_data_concept,
                           "CFR Criteria": decend_CPT_CFR_criteria,
                           "Code Set": decend_CPT_root,
                           "Code": decend_CPT_values,
                           "Code Description": decend_CPT_names,
                           "Keyword": decend_CPT_keyword_value})

CPT_trans_decend = pd.concat(
    [CPT_decend, CPT_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
CPT_full_grouped = CPT_trans_decend.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

CPT_full_grouped = CPT_full_grouped.reindex(
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
FILE_NAME = f"{CONDITION}_cpt_codes.xlsx"
CPT_full_grouped.to_excel(OUTPATH + FILE_NAME)

# Print a message indicating where the file is saved
print(f"Excel file '{FILE_NAME}' saved in the output folder.")
