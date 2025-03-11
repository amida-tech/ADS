"""
This script processes RxNorm codes and returns the code's Veteran Administration Class.
The required input is an excel file with two columns: "Code Value" and "Code Description"
The output is a structured excel file titled 'va_class_results' with three columns: "Code Value",  "Code Description", "VA Class". # pylint: disable=line-too-long
"""

import time
import requests  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error


def get_va_class_for_cui(cui):  # pylint: disable=missing-function-docstring
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": cui}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "rxclassDrugInfoList" in data:  # pylint: disable=no-else-return
            va_classes = {
                item["rxclassMinConceptItem"]["className"]
                for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]
                if item["rxclassMinConceptItem"]["classType"] == "VA"
            }
            return "; ".join(va_classes) if va_classes else "No VA Class Found"
        else:
            return "No VA Class Found"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def process_cui_list(file_path, output_file):  # pylint: disable=missing-function-docstring
    df = pd.read_excel(file_path)
    results = []

    for _, row in df.iterrows():
        cui = str(row[0])  # Code Value (CUI)
        description = str(row[1])  # Code Description
        va_class = get_va_class_for_cui(cui)
        results.append({"Code Value": cui,
                        "Code Description": description,
                        "VA Class": va_class})
        time.sleep(1)  # To prevent overloading the API

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")


# UPDATE INPUTS HERE
if __name__ == "__main__":
    INPUT_FILE = "input/" + "RxNorm Codes to Map.xlsx"  # Update with actual file name
    # Update as needed for additional calls
    OUTPUT_FILE = "output/" + "va_class_results.xlsx"
    process_cui_list(INPUT_FILE, OUTPUT_FILE)
