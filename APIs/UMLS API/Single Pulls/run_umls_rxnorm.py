"""
This script ingests a CSV file of condition medication keywords and 
returns and Excel file of RxNorm codes that are associated with the inputted keywords
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
df = df[df["Data Concept"] == "Medication"]

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
            query['sabs'] = "RXNORM"
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

RxNorm_df = pd.DataFrame({"VASRD Code": dc_code_4,
                          "Data Concept": data_concept_4,
                          "CFR Criteria": cfr_criteria_4,
                          "Code Set": vocab_type_4,
                          "Code": code_4,
                          "Code Description": name_4,
                          "Keyword": keyword_value_4})

# Group by 'Code' and concatenate 'VASRD Code', 'Data Concept', 'CFR
# Criteria', and 'Keyword' by a semicolon if there are multiple entries
# for the same keyword
RxNorm_df = RxNorm_df.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique()),
}).reset_index()

# Initial setup
cui_list = RxNorm_df["Code"]
dc_code_list = RxNorm_df["VASRD Code"]
cfr_criteria_list = RxNorm_df["CFR Criteria"]
data_concept_list = RxNorm_df["Data Concept"]
keyword_value_list = RxNorm_df["Keyword"]

SABS = 'RXNORM'
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

            RxNorm_keyword.extend([keyword_value] * len(results))
            RxNorm_DC_Code.extend([dc_code] * len(results))
            RxNorm_CFR_criteria.extend([cfr_criteria] * len(results))
            RxNorm_data_concept.extend([data_concept] * len(results))
            RxNorm_code.extend([item['ui'] for item in results])
            RxNorm_name.extend([item['name'] for item in results])
            RxNorm_root.extend([item['rootSource'] for item in results])
        except JSONDecodeError:
            print(
                f"JSONDecodeError encountered for CUI: {cui}. Skipping this entry.")
            break  # Exit the while loop for this `cui` and proceed to the next one

# Create the resulting DataFrame
RxNorm_trans_df = pd.DataFrame({
    "VASRD Code": RxNorm_DC_Code,
    "Data Concept": RxNorm_data_concept,
    "CFR Criteria": RxNorm_CFR_criteria,
    "Code Set": RxNorm_root,
    "Code": RxNorm_code,
    "Code Description": RxNorm_name,
    "Keyword": RxNorm_keyword
})

RxNorm_trans_df_clean = RxNorm_trans_df.drop_duplicates().reset_index(drop=True)

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
RxNorm_full_grouped = RxNorm_trans_df_clean.groupby('Code').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
    'Code Description': 'first',
    'Keyword': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

RxNorm_full_grouped = RxNorm_full_grouped[RxNorm_full_grouped["Code"].str.len(
) >= 5]

# Reorder columns
RxNorm_full_grouped = RxNorm_full_grouped.reindex(
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
FILE_NAME = f"{CONDITION}_RxNorm_codes.xlsx"
RxNorm_full_grouped.to_excel(OUTPATH + FILE_NAME)

# Print a message indicating where the file is saved
print(f"Excel file '{FILE_NAME}' saved in the output folder.")
