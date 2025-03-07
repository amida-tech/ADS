"""This code will cross check whether codes are present in the CDW and label the 'In CDW' column
with either 'Yes' or 'No'.

Script assumes that there are sheets labeled as icd10-cpt-loinc and ndc-snomed-icd9. Script also
assumes that in sheet name icd10-cpt-loinc, there are column names labeled as CodeSet, Code and
Description. Sheet name ndc-snomed-icd9 should also have columns CodeSet, Code and Description.
"""

import re  # pylint: disable=unused-import
import warnings
import pandas as pd

warnings.filterwarnings("ignore")

# Codes to Check- Enter any medical codes file here.
CODE_SET_NAME = "example_codes"

# medical codes file
# This is the CDW. Make sure an updated version is inside the input folder
# or change the file path to where it is stored.
FILE_PATH = r"codeset/input/med_codes.xlsx"

SHEET_NAME_ICD10_LOINC_CPT = "icd10-cpt-loinc"
SHEET_NAME_NDC_SNOMED_ICD9 = "ndc-snomed-icd9"
med_codes_icd10_loinc_cpt = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_ICD10_LOINC_CPT)
med_codes_ndc_snomed_icd9 = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_NDC_SNOMED_ICD9)


# File with codes to check. Make sure an updated version is in the input
# folder. There should be a column labeled as 'In CDW' which should be
# blank.
FILE_PATH_1 = f"codeset/input/{CODE_SET_NAME}.xlsx"
SHEET_NAME = "Code Set Details"
confirmed_codes = pd.read_excel(FILE_PATH_1, sheet_name=SHEET_NAME)
confirmed_codes["Code"] = confirmed_codes["Code"].astype(str)


# NDC values format adjustment. Uses boolean mask to check if values have the CodeSet of "NDC".
# Then performs format adjustment using regex.
# Convert to string if not already str
med_codes_ndc_snomed_icd9["Code"] = med_codes_ndc_snomed_icd9["Code"].astype(str)
# Boolean mask for NDC codes
is_ndc = med_codes_ndc_snomed_icd9["CodeSet"] == "NDC"
# Extract only the first 9 digits (keeping dashes)
med_codes_ndc_snomed_icd9.loc[is_ndc, "Code"] = med_codes_ndc_snomed_icd9.loc[
    is_ndc, "Code"
].str.extract(r"^(\d{5}-\d{4})")[0]
# Remove possible whitespace
med_codes_ndc_snomed_icd9["Code"] = med_codes_ndc_snomed_icd9["Code"].str.strip()


# ICD-10 values format adjustment. Uses boolean mask to check if values
# have the CodeSet of "ICD-10". Then performs format adjustment using
# regex.
is_ICD_10 = med_codes_icd10_loinc_cpt["CodeSet"] == "ICD-10"
med_codes_icd10_loinc_cpt.loc[is_ICD_10, "Code"] = med_codes_icd10_loinc_cpt.loc[
    is_ICD_10, "Code"
].str.replace(r"^([A-Za-z0-9]+)$", r"\1.", regex=True)

# ICD-9 values format adjustment. Uses boolean mask to check if values
# have the CodeSet of "NDC". Then performs format adjustment using regex.
is_ICD_9 = med_codes_ndc_snomed_icd9["CodeSet"] == "ICD-9"
med_codes_ndc_snomed_icd9.loc[is_ICD_9, "Code"] = med_codes_ndc_snomed_icd9.loc[
    is_ICD_9, "Code"
].str.replace(r"^(\d+)$", r"\1.0", regex=True)

# ICD-9 values format adjustment in codes to check file(ex. changes 150 to
# 150.0)
for index, row in confirmed_codes.iterrows():
    if row["Code Set"] == "ICD-9" and "." not in row["Code"]:
        confirmed_codes.at[index, "Code"] = f"{row['Code']}.0"


# Remove trailing zeros from decimal values-small but important test case
# med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'] =
# med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'].str.replace(r'(\.\d*[1-9])0+$', r'\1', regex=True)


# First if statement in for loop covers keyword checks. Else statement
# covers NDC, ICD-10, CPT etc., and labels 'Yes' or 'No' in the 'in_cdw'
# column.

for index_cs, code_set_val in confirmed_codes["Code Set"].items():
    if code_set_val == "Keyword":
        temp_desc = confirmed_codes.at[index_cs, "Code Description"]
        in_cdw = med_codes_ndc_snomed_icd9["Description"].str.contains(temp_desc, case=False).any()
        confirmed_codes.at[index_cs, "In CDW"] = "Yes" if in_cdw else "No"

    elif code_set_val in ("RxNorm", "RXNORM"):
        confirmed_codes.at[index_cs, "In CDW"] = "No"

    else:
        temp = confirmed_codes.at[index_cs, "Code"]
        in_cdw = (
            med_codes_icd10_loinc_cpt["Code"].eq(temp).any()
            or med_codes_ndc_snomed_icd9["Code"].eq(temp).any()
        )
        confirmed_codes.at[index_cs, "In CDW"] = "Yes" if in_cdw else "No"


# Update output file path to desired output file path. A new file
# 'confirmed_codes' will be generated with values representing if codes
# are found in CDW.

OUTPUT_FILE_PATH = f"codeset/output/{CODE_SET_NAME}_confirmed.xlsx"
confirmed_codes.to_excel(OUTPUT_FILE_PATH, index=False)

# Print a message indicating where the file is saved
print(f"Excel file '{CODE_SET_NAME}.xlsx' saved in the output folder.")
