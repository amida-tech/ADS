"""
This script processes an Excel sheet with LOINC medical codes in a column titled "LOINC_CODES" 
and returns relational data related to the inputted LOINC code.
The output is a structured Excel file containing the following columns:
- LOINC_CODE
- LOINC Description
- answer_to
- has_class
- has_system
- has_component
- analyzes
- measures
- evaluation_of_relation_1
- evaluation_of_relation_2
- Official LOINC Name
"""
import pandas as pd
import requests

## CHANGE INPUTS HERE ##
API_KEY = '903c7d74-6a9e-4d12-a3eb-6f7d41a21c2d'

# Input Excel Sheet with LOINC Codes
INPUT_FILE_NAME = "Test LOINC"

# Output Excel sheet name
OUTPUT_FILE_NAME = "test_loinc_results"

## END OF REQUESTED INPUTS ##

BASE_URL = "https://uts-ws.nlm.nih.gov/rest/content/current/source/LNC/"
# Load the Excel file containing LOINC codes
# Update with the correct file path
FILE_PATH = f"input/{INPUT_FILE_NAME}.xlsx"
loinc_df = pd.read_excel(FILE_PATH)

# Ensure there's a column named 'LOINC_CODE' in the Excel file
if 'LOINC_CODE' not in loinc_df.columns:
    raise ValueError("The Excel file must contain a 'LOINC_CODE' column.")

results = []

# Iterate over each LOINC code and query the API
for loinc_code in loinc_df['LOINC_CODE']:
    URL = f"{BASE_URL}{loinc_code}/relations?apiKey={API_KEY}"
    PAGE = 1  # Start with page 1

    while True:
        try:
            # Add page parameter to the URL for pagination
            PAGINATED_URL = f"{URL}&page={PAGE}"
            response = requests.get(PAGINATED_URL, timeout=10)
            response.raise_for_status()
            json_data = response.json()
        except Exception as e: # pylint: disable=broad-exception-caught
            print(
                f"Error retrieving data for LOINC {loinc_code} on page {PAGE}: {e}")
            break

        # Extract relevant information from JSON
        official_name, human_readable_name = None, None
        has_class_values = set()
        answer_to_values = set()
        has_system_values = set()
        has_comp_values = set()
        has_analyzes_values = set()
        has_measures_values = set()

        # Process the current page of results
        for item in json_data.get("result", []):
            if item.get("additionalRelationLabel") == "answer_to":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    answer_to_values.add(related_id_name)

            if item.get("additionalRelationLabel") == "expanded_form_of" or item.get(
                    "additionalRelationLabel") == "mth_expanded_form_of":
                official_name = item.get("relatedFromIdName", "Not Found")
                human_readable_name = item.get("relatedIdName", "Not Found")

            if item.get("additionalRelationLabel") == "has_class":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    has_class_values.add(related_id_name)

            if item.get("additionalRelationLabel") == "has_system":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    has_system_values.add(related_id_name)

            if item.get("additionalRelationLabel") == "has_component":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    has_comp_values.add(related_id_name)

            if item.get("additionalRelationLabel") == "analyzes":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    has_analyzes_values.add(related_id_name)

            if item.get("additionalRelationLabel") == "measures":
                related_id_name = item.get("relatedIdName")
                if related_id_name:
                    has_measures_values.add(related_id_name)

        # Append the results for the current page
        results.append({
            "LOINC_CODE": loinc_code,
            "Human Readable LOINC Name": human_readable_name 
                if human_readable_name else "Not Found",
            "answer_to": "; ".join(sorted(answer_to_values)) 
                if answer_to_values else "Not Found",
            "has_class": "; ".join(sorted(has_class_values)) 
                if has_class_values else "Not Found",
            "has_system": "; ".join(sorted(has_system_values)) 
                if has_system_values else "Not Found",
            "has_component": "; ".join(sorted(has_comp_values)) 
                if has_comp_values else "Not Found",
            "analyzes": "; ".join(sorted(has_analyzes_values)) 
                if has_analyzes_values else "Not Found",
            "measures": "; ".join(sorted(has_measures_values)) 
                if has_measures_values else "Not Found",
            "Official LOINC Name": official_name 
                if official_name else "Not Found"
        })

        # Check if there is a next page, if not, break the loop
        if "next" not in json_data or not json_data["next"]:
            break

        # Move to the next page
        PAGE += 1

semi_complete_df = pd.DataFrame(results)


# Keep in mind this pulls the CUI code for UMLS
string_list = [item for item in semi_complete_df["Official LOINC Name"].to_list(
) if item != "Not Found"]
code_4 = []
name_4 = []
loinc_code_4 = []
VERSION = 'current'
BASE_URI = 'https://uts-ws.nlm.nih.gov'

for x in range(len(string_list)): # pylint: disable=consider-using-enumerate
    STRING = str(string_list[x])
    CONTENT_ENDPOINT = "/rest/search/" + VERSION
    FULL_URL = BASE_URI + CONTENT_ENDPOINT
    LOINC_CODE = semi_complete_df['LOINC_CODE'][semi_complete_df['Official LOINC Name'] == STRING].to_list()[0] # pylint: disable=line-too-long
    PAGE = 0

    try:
        while True:
            PAGE += 1
            query = {
                'string': STRING,
                'apiKey': API_KEY,
                'searchType': 'exact',
                'pageNumber': PAGE,
                'sabs': 'LNC'}
            r = requests.get(FULL_URL, params=query, timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            outputs = r.json()

            items = (([outputs['result']])[0])['results']

            if len(items) == 0:
                break

            # Using list comprehension to append data
            loinc_code_4.extend([LOINC_CODE for _ in items])
            code_4.extend([result['ui'] for result in items])
            name_4.extend([result['name'] for result in items])

    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error processing keyword {STRING}: {e}")
        continue  # Skip this CUI and continue with the next one

loinc_df = pd.DataFrame({"CUI Code": code_4,
                         "LOINC_CODE": loinc_code_4,
                         "Code Description": name_4})

# Read the list of CUI codes from the input file (one per line)
cui_list = loinc_df["CUI Code"]
results_list = []

# Loop through each CUI code and query the UMLS API
for cui in cui_list:
    # Build the ENDPOINT URL for this CUI
    ENDPOINT = f"/rest/content/{VERSION}/CUI/{cui}"
    URL = BASE_URI + ENDPOINT
    params = {"apiKey": API_KEY}

    try:
        response = requests.get(URL, params=params, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()  # raise an error for non-200 responses
        json_data = response.json()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error processing Semantic Type for CUI {cui}: {e}")
        continue  # Skip this CUI and continue with the next one

    # Extract the semantic type from the response
    result = json_data.get("result", {})
    semantic_types = result.get("semanticTypes", [])
    semantic_group_uri = result.get("semanticTypes", [])
    if semantic_types and len(semantic_types) > 0:
        SEMANTIC_URI = semantic_group_uri[0].get("uri", "Not Found")
    else:
        SEMANTIC_URI = "Not Found"

    results_list.append({
        "CUI Code": cui,
        "Semantic Group URI": SEMANTIC_URI
    })

# Create a DataFrame from the results
semantic_uri_df = pd.DataFrame(results_list)

# Initialize a list to hold the results
data = []

json_urls = semantic_uri_df["Semantic Group URI"].to_list()
code_values = semantic_uri_df["CUI Code"].to_list()

# Loop through each JSON source
for idx, URL in enumerate(json_urls):
    code_value = semantic_uri_df["CUI Code"].to_list()[idx]

    try:
        # Fetch the JSON data
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # Extract 'evaluation_of' relations
        filtered_relations = [
            relation for relation in json_data.get("result", {}).get("inverseInheritedRelations", []) # pylint: disable=line-too-long
            if relation.get("relationType") == "evaluation_of"
        ]

        # Extract and deduplicate 'relation1' and 'relation2' values
        relation1_values = list(
            dict.fromkeys(
                rel['relation1'] for rel in filtered_relations))
        relation2_values = list(
            dict.fromkeys(
                rel['relation2'] for rel in filtered_relations))

        # Concatenate unique values with semicolons
        RELATION1_CONCAT = "; ".join(
            relation1_values) if relation1_values else "None"
        RELATION2_CONCAT = "; ".join(
            relation2_values) if relation2_values else "None"

        # Append the row data
        data.append({
            "CUI Code": code_value,
            "source_url": URL,
            "evaluation_of_relation_1": RELATION1_CONCAT,
            "evaluation_of_relation_2": RELATION2_CONCAT
        })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {URL}: {e}")
        data.append({
            "CUI Code": code_value,
            "source_url": URL,
            "evaluation_of_relation_1": "Error",
            "evaluation_of_relation_2": "Error"
        })

# Create the final DataFrame
evaluation_of_df = pd.DataFrame(data)

# Merge above DF with original DF and update all below chunks accordingly
evaluation_of_df_complete = pd.merge(loinc_df, evaluation_of_df[[
    'CUI Code', 
    'evaluation_of_relation_1', 
    'evaluation_of_relation_2']], on='CUI Code', how='left')

# Merge the two dataframes on "LOINC_CODE", keeping all rows from
# semi_complete_df
merged_df = pd.merge(semi_complete_df, evaluation_of_df_complete[['LOINC_CODE',
                                                                  'evaluation_of_relation_1', 
                                                                  'evaluation_of_relation_2']],
                     on='LOINC_CODE', how='left')

# Replace NaN values with 'N/A'
merged_df.fillna('N/A', inplace=True)

# Rename "Human Readable LOINC Name" to "LOINC Description"
merged_df.rename(
    columns={
        'Human Readable LOINC Name': 'LOINC Description'},
    inplace=True)

# Reorder columns as specified
final_columns = ['LOINC_CODE',
                 'LOINC Description', 
                 'answer_to', 
                 'has_class', 
                 'has_system', 
                 'has_component', 
                 'analyzes',
                 'measures', 
                 'evaluation_of_relation_1', 
                 'evaluation_of_relation_2', 
                 'Official LOINC Name']
merged_df = merged_df[final_columns]

# Display the final merged dataframe
# merged_df

# Convert results to DataFrame and save to Excel
output_df = merged_df
OUTPUT_FILE = f"output/{OUTPUT_FILE_NAME}.xlsx"
output_df.to_excel(OUTPUT_FILE, index=False)
print(f"Results saved to {OUTPUT_FILE}")
