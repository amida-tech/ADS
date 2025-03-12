"""
This script ingests a CSV file of condition lab keywords and 
returns and Excel file of LOINC codes that are associated with the inputted keywords
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
BASE_URI = 'https://uts-ws.nlm.nih.gov'

# Keyword Column Name
COLUMN_NAME = 'Keyword'
## End of Requested Inputs ##

# Read the Excel file
df = pd.read_csv('input/' + CSV_FILE_INPUT_NAME + '.csv')
df = df[df["Data Concept"] == "Lab"]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
df = df.groupby('Keyword').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first'  # Retain 'Code Set' as it doesn't need concatenation
}).reset_index()

# Extract the column as a Pandas Series then list
string_list = df[COLUMN_NAME].tolist()

# Now column_list contains the column data with the column name as the first element
# int(string_list)

# Keep in mind this pulls the CUI code for UMLS
# You will need to convert these CUI codes from UMLS codes into their
# associated SNOMEDCT, ICD10, LNC, CPT, etc codes

code_4 = []
name_4 = []
vocab_type_4 = []
dc_code_4 = []
cfr_criteria_4 = []
data_concept_4 = []
keyword_value_4 = []

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
            query['sabs'] = "LNC"
            r = requests.get(FULL_URL, params=query)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs = r.json()

            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                break

            # Using list comprehension to append data
            keyword_value_4.extend([STRING] * len(items))
            dc_code_4.extend([DC_code] * len(items))
            cfr_criteria_4.extend([CFR_criteria] * len(items))
            data_concept_4.extend([data_concept] * len(items))
            code_4.extend([result['ui'] for result in items])
            name_4.extend([result['name'] for result in items])
            vocab_type_4.extend([result['rootSource'] for result in items])

    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error processing keyword {STRING}: {e}")
        continue  # Skip this CUI and continue with the next one

loinc_df = pd.DataFrame({"VASRD Code": dc_code_4,
                         "Data Concept": data_concept_4,
                         "CFR Criteria": cfr_criteria_4,
                         "Code Set": vocab_type_4,
                         "Code": code_4,
                         "Code Description": name_4,
                         "Keyword": keyword_value_4})

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR
# Criteria', and 'Keyword' by a semicolon if there are multiple entries
# for the same keyword
loinc_df = loinc_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
}).reset_index()

cui_list = loinc_df["Code"]
dc_code_list = loinc_df["VASRD Code"]
cfr_criteria_list = loinc_df["CFR Criteria"]
data_concept_list = loinc_df["Data Concept"]
keyword_value_list = loinc_df["Keyword"]

SABS = 'LNC'
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

            LOINC_keyword.extend([keyword_value] * len(results))
            LOINC_DC_Code.extend([dc_code] * len(results))
            LOINC_CFR_criteria.extend([cfr_criteria] * len(results))
            LOINC_data_concept.extend([data_concept] * len(results))
            LOINC_code.extend([item['ui'] for item in results])
            LOINC_name.extend([item['name'] for item in results])
            LOINC_root.extend([item['rootSource'] for item in results])
        except JSONDecodeError:
            print(
                f"JSONDecodeError encountered for CUI: {cui}. Skipping this entry.")
            break  # Exit the while loop for this `cui` and proceed to the next one

LOINC_trans_df = pd.DataFrame({"VASRD Code": LOINC_DC_Code,
                               "Data Concept": LOINC_data_concept,
                               "CFR Criteria": LOINC_CFR_criteria,
                               "Code Set": LOINC_root,
                               "Code": LOINC_code,
                               "Code Description": LOINC_name,
                               "Keyword": LOINC_keyword})

# Get Children of LOINC
decend_LOINC_names = []
decend_LOINC_values = []
decend_LOINC_root = []
decend_LOINC_DC_Code = []
decend_LOINC_CFR_criteria = []
decend_LOINC_data_concept = []
decend_LOINC_keyword_value = []

for x in range(len(LOINC_code)): # pylint: disable=consider-using-enumerate
    SOURCE = 'LNC'
    STRING = LOINC_trans_df["Keyword"].to_list()[x]
    DC_code = LOINC_trans_df["VASRD Code"][LOINC_trans_df['Keyword'] == STRING].to_list()[
        0]
    CFR_criteria = LOINC_trans_df['CFR Criteria'][LOINC_trans_df['Keyword'] == STRING].to_list()[
        0]
    data_concept = LOINC_trans_df['Data Concept'][LOINC_trans_df['Keyword'] == STRING].to_list()[
        0]
    IDENTIFIER = str(LOINC_code[x])
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
            decend_LOINC_keyword_value.extend([STRING] * len(items["result"]))
            decend_LOINC_DC_Code.extend([DC_code] * len(items["result"]))
            decend_LOINC_CFR_criteria.extend(
                [CFR_criteria] * len(items["result"]))
            decend_LOINC_data_concept.extend(
                [data_concept] * len(items["result"]))
            decend_LOINC_values.extend([result["ui"]
                                       for result in items["result"]])
            decend_LOINC_names.extend([result["name"]
                                      for result in items["result"]])
            decend_LOINC_root.extend([result["rootSource"]
                                     for result in items["result"]])
    except Exception as except_error: # pylint: disable=broad-exception-caught
        print(except_error)


LOINC_decend = pd.DataFrame({"VASRD Code": decend_LOINC_DC_Code,
                             "Data Concept": decend_LOINC_data_concept,
                             "CFR Criteria": decend_LOINC_CFR_criteria,
                             "Code Set": decend_LOINC_root,
                             "Code": decend_LOINC_values,
                             "Code Description": decend_LOINC_names,
                             "Keyword": decend_LOINC_keyword_value})

LOINC_trans_decend = pd.concat(
    [LOINC_decend, LOINC_trans_df.loc[:]]).drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
LOINC_full_grouped = LOINC_trans_decend.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

# Replace 'LNC' with 'LOINC' in the 'Code Set' column
LOINC_full_grouped['Code Set'] = LOINC_full_grouped['Code Set'].replace(
    'LNC', 'LOINC')

# Filter out codes containing non-numeric values (allow hyphen)
LOINC_full_grouped = LOINC_full_grouped[LOINC_full_grouped['Code'].str.match(
    r'^[\d-]+$')]

LOINC_full_grouped = LOINC_full_grouped.reindex(
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
FILE_NAME = f"{CONDITION}_LOINC_codes.xlsx"
LOINC_full_grouped.to_excel(OUTPATH + FILE_NAME)

# Print a message indicating where the file is saved
print(f"Excel file '{FILE_NAME}' saved in the output folder.")
