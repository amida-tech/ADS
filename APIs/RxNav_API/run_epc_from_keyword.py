"""
This script processes a string of medication names and returns the code's
Established Pharmacologic Class (EPC).
The required input is an excel file with a column titled: "Keyword"
The output is a structured excel file titled 'drug_epc_results' with two columns:
"Drug Name" and "RxNorm API EPC"
"""
import time
import requests
import pandas as pd


# INPUTS
INPUT_FILE_NAME = "Test Subset RxNorm Keywords"
OUTPUT_FILE_NAME = "drug_epc_results"
# END OF INPUTS

# Function to query the RxNorm API for a drug's EPC class


def get_epc_for_drug(drug_name):
    """Returns EPC for a drug keyword"""
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json?"
    params = {
        "drugName": drug_name,
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)

        # If the response status code is not 200, raise an HTTPError
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Extract EPC class information and drop duplicates using a set
        epc_classes = set()  # Using a set to ensure no duplicates
        if 'rxclassDrugInfoList' in data:
            drug_info_list = data['rxclassDrugInfoList']['rxclassDrugInfo']
            for info in drug_info_list:
                if info['rxclassMinConceptItem']['classType'] == 'EPC':
                    epc_classes.add(
                        info['rxclassMinConceptItem']['className'])  # Add EPC to set

        # Return the EPCs joined by a semicolon, or "No EPC found" if empty
        return "; ".join(epc_classes) if epc_classes else "No EPC found"

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for {drug_name}: {http_err}")
        return f"Error: {http_err}"
    except requests.exceptions.Timeout:
        return f"Error: Timeout occurred while processing {drug_name}"
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for {drug_name}: {req_err}")
        return f"Error: {req_err}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"An unexpected error occurred for {drug_name}: {e}")
        return f"Error: {e}"
    # pylint: disable=broad-exception-caught

# Function to process a list of drugs and return EPC results in a pandas
# DataFrame


def process_drugs(drug_list):
    """Processes the list of drug keywords"""
    results = []
    for drug in drug_list:
        epc = get_epc_for_drug(drug)
        results.append({"Drug Name": drug, "RxNorm API EPC": epc})
        time.sleep(1)  # Pause between requests to avoid overloading the API
    return pd.DataFrame(results)


if __name__ == "__main__":
    # Load medication keywords from Excel file
    EXCEL_FILE = f"input/{INPUT_FILE_NAME}.xlsx"
    # Assuming the drug names are in the first column
    df_keywords = pd.read_excel(EXCEL_FILE)

    # Extract drug names as a list from the first column
    keywords = df_keywords["Keyword"].to_list()

    # Process the medications and save results to Excel
    df = process_drugs(keywords)
    df.to_excel(f"output/{OUTPUT_FILE_NAME}.xlsx", index=False)
