"""
This script processes RxNorm codes and returns the code's
Veteran Administration Class,
Anatomical Therapeutic Chemical (ATC) Classification,
Established Pharmacologic Class (EPC)
and
RxNav's may_treat relation
The required input is an excel file with two columns: "Code Value" and "Code Description"
The output is a structured excel file titled 'complete_rxnorm_classes' with three columns:
"Code Value",  "Code Description", "VA Class".
"""

import time
import requests  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error

# INPUTS
INPUT_FILE_NAME = "Test Subset RxNorm"
OUTPUT_FILE_NAME = "complete_rxnorm_classes"
# END OF INPUTS


def get_va_class_for_cui(cui): # pylint: disable=inconsistent-return-statements
    """Returns VA Class for an RxNorm code"""
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": cui}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "rxclassDrugInfoList" in data:
            va_classes = {
                item["rxclassMinConceptItem"]["className"]
                for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]
                if item["rxclassMinConceptItem"]["classType"] == "VA"
            }
            return "; ".join(va_classes) if va_classes else "No VA Class Found"

    except requests.exceptions.RequestException as e:
        return f"Error processing {cui} for VA Class: {e}"


def get_atc1_4_class_for_cui(cui): # pylint: disable=inconsistent-return-statements
    """Returns ATC1-4 for an RxNorm code"""
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": cui}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "rxclassDrugInfoList" in data:
            atc1_4_classes = {
                item["rxclassMinConceptItem"]["className"]
                for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]
                if item["rxclassMinConceptItem"]["classType"] == "ATC1-4"
            }
            return "; ".join(
                atc1_4_classes) if atc1_4_classes else "No ATC1-4 Class Found"

    except requests.exceptions.RequestException as e:
        return f"Error processing {cui} for ATC1-4: {e}"


def get_epc_class_for_cui(cui): # pylint: disable=inconsistent-return-statements
    """Returns EPC for an RxNorm code"""
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": cui}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "rxclassDrugInfoList" in data:
            epc_classes = {
                item["rxclassMinConceptItem"]["className"]
                for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]
                if item["rxclassMinConceptItem"]["classType"] == "EPC"
            }
            return "; ".join(epc_classes) if epc_classes else "No EPC Found"

    except requests.exceptions.RequestException as e:
        return f"Error processing {cui} for EPC: {e}"


def get_may_treat_class_for_cui(cui): # pylint: disable=inconsistent-return-statements
    """Returns possible associated diagnoses associated with an RxNorm code"""
    base_url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": cui}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "rxclassDrugInfoList" in data:
            may_treat_classes = {
                item["rxclassMinConceptItem"]["className"]
                for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]
                if item.get("rela") == "may_treat"
            }
            return "; ".join(
                may_treat_classes) if may_treat_classes else "No May Treat Class Found"

    except requests.exceptions.RequestException as e:
        return f"Error processing {cui} for may_treat relation: {e}"


def process_cui_list(file_path, output_file):
    """Processes CUI codes and builds output Excel file"""
    df = pd.read_excel(file_path)
    results = []

    for _, row in df.iterrows():
        cui = str(row[0])  # Code Value (CUI)
        description = str(row[1])  # Code Description
        va_class = get_va_class_for_cui(cui)
        epc_class = get_epc_class_for_cui(cui)
        atc1_4_class = get_atc1_4_class_for_cui(cui)
        may_treat = get_may_treat_class_for_cui(cui)
        results.append({"Code Value": cui,
                        "Code Description": description,
                        "VA Class": va_class,
                        "EPC": epc_class,
                        "ATC1-4": atc1_4_class,
                        "May Treat": may_treat})
        time.sleep(1)  # To prevent overloading the API

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    INPUT_FILE = f"input/{INPUT_FILE_NAME}.xlsx"
    OUTPUT_FILE = f"output/{OUTPUT_FILE_NAME}.xlsx"
    process_cui_list(INPUT_FILE, OUTPUT_FILE)
