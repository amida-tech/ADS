"""
This script processes a string of medication names and returns the code's Established Pharmacologic Class (EPC).
The required input is an excel file with the first column: "Keywords"
The output is a structured excel file titled 'drug_epc_results' with two columns: "Drug Name" and "RxNorm API EPC"
"""
import time
import requests  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error

# Function to query the RxNorm API for a drug's EPC class


def get_epc_for_drug(drug_name): # pylint: disable=missing-function-docstring
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json?"
    params = {  # pylint: disable=missing-function-docstring
        "drugName": drug_name,
    }
    try:
        response = requests.get(base_url, params=params)

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
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for {drug_name}: {req_err}")
        return f"Error: {req_err}"
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"An unexpected error occurred for {drug_name}: {e}")
        return f"Error: {e}"
    # pylint: disable=broad-exception-caught

# Function to process a list of drugs and return EPC results in a pandas
# DataFrame


def process_drugs(drug_list): # pylint: disable=missing-function-docstring
    results = []
    for drug in drug_list:
        epc = get_epc_for_drug(drug)
        results.append({"Drug Name": drug, "RxNorm API EPC": epc})
        time.sleep(1)  # Pause between requests to avoid overloading the API
    return pd.DataFrame(results)


# UPDATE INPUTS HERE
if __name__ == "__main__":
    # Load medication keywords from Excel file
    EXCEL_FILE = "input/" + "RxNorm Codes to Map.xlsx"  # Update with actual file name
    # Assuming the drug names are in the first column
    df_keywords = pd.read_excel(EXCEL_FILE)

    # Extract drug names as a list from the first column
    keywords = df_keywords.iloc[:, 0].tolist()

    # Process the medications and save results to Excel
    df = process_drugs(keywords)  # pylint: disable=
    # Update as needed to account for multiple calls
    df.to_excel("output/drug_epc_results.xlsx", index=False)
