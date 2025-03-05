"""
This script processes medical codes and categorizes them by their associated CFR criteria.
The output is a structured text file containing different sets of codes (ICD-10, CPT, NDC, etc.).
"""

import pandas as pd

NAME_OF_CODE_SET = "example"  # Enter name of condition(Arrythmias, GI Cancer etc.)
FILE_NAME = "example_codes"  # Enter file name stored in input folder

INPUT_DIRECTORY = f"codeset/input/{FILE_NAME}.xlsx"
OUTPUT_DIRECTORY = f"codeset/output/{NAME_OF_CODE_SET}.txt"

default = pd.read_excel(INPUT_DIRECTORY, sheet_name="Code Set Details")

df = default.drop(default[default['In CDW'] == 'No'].index)

# splitting phrases if they have a semicolon
df['Code Set'] = df['Code Set'].str.split().str.join("")

df['CFR Criteria'] = df['CFR Criteria'].str.split('; ')
df = df.explode('CFR Criteria')

top_dicts = df['CFR Criteria'].unique()

nested_dict = {}

for unique_val in top_dicts:
    nested_dict[unique_val] = {"Tuple Code Set": ()}

# Code works by utilizing dictionary data structure. Keys are the CFR
# criteria and the values are tuples(Code Set, Code). A different for loop
# runs for every Code Set(NDC, ICD-10 etc.) and consolidates codes by both
# CFR criteria as well as code set. Output is a text file.


# creating tuples of Code Set and Code(NDC, CPT, ICD-9, IDC-10)
df['Tuple'] = list(zip(df['Code Set'], df["Code"]))

# Making dictionary: Key = CFR Criteria and Value = tuple of Code Set + Code combo
main = (df.groupby('CFR Criteria')['Tuple'].apply(list).to_dict())


# creating tuples of Code Set and Code(Keyword)
df['Tuple_part_2'] = list(zip(df['Code Set'], df["Code Description"]))

keyword_dict = (df.groupby('CFR Criteria')['Tuple_part_2'].apply(list).to_dict())


with open(OUTPUT_DIRECTORY, "w", encoding="utf-8") as f:

    f.write(f"{NAME_OF_CODE_SET} \n\n")

    # Compiles all LOINC Codes
    for k, v in main.items():
        loinc_appender = []
        for code_type, code in v:
            if code_type == "LOINC":
                loinc_appender.append(str(code))
        loincs = f"{k} LOINC codeset:\n '{','.join(loinc_appender)}'\n" # pylint: disable=invalid-name

        if len(loinc_appender) > 0:
            f.write(f"{loincs} \n")
    f.write("\n\n\n")

    # Compiles all ICD-10 Codes
    for k, v in main.items():
        icd_10_appender = []
        for code_type, code in v:
            if code_type == "ICD-10":
                icd_10_appender.append(str(code))
        icd_10 = f"{k} ICD-10 codeset:\n '{','.join(icd_10_appender)}'\n" # pylint: disable=invalid-name

        if len(icd_10_appender) > 0:
            f.write(f"{icd_10} \n")
    f.write("\n\n\n")

    # Compiles all CPT Codes
    for k, v in main.items():
        cpt_appender = []
        for code_type, code in v:
            if code_type == "CPT":
                cpt_appender.append(str(code))
        cpt = f"{k} CPT codeset:\n '{','.join(cpt_appender)}'\n" # pylint: disable=invalid-name

        if len(cpt_appender) > 0:
            f.write(f"{cpt} \n")
    f.write("\n\n\n")

    # Compiles all ICD -9 Codes
    for k, v in main.items():
        icd_9_appender = []
        for code_type, code in v:
            if code_type == "ICD-9":
                icd_9_appender.append(str(code))
        icd_9 = f"{k} ICD-9 codeset:\n '{','.join(icd_9_appender)}'\n" # pylint: disable=invalid-name

        if len(icd_9_appender) > 0:
            f.write(f"{icd_9} \n")
    f.write("\n\n\n")

    # Compiles NDC Codes
    for k, v in main.items():
        ndc_appender = []
        for code_type, code in v:
            if code_type == "NDC":
                ndc_appender.append(f"{str(code)}%")
        ndc = f"{k} NDC codeset:\n '{','.join(ndc_appender)}'\n" # pylint: disable=invalid-name

        if len(ndc_appender) > 0:
            f.write(f"{ndc} \n")
    f.write("\n\n\n")

    # Compiles all SNOMED-CT Codes
    for k, v in main.items():
        snomed_appender = []
        for code_type, code in v:
            if code_type == "SNOMED-CT":
                snomed_appender.append(str(code))
        snomed = f"{k} SNOMED-CT codeset:\n '{','.join(snomed_appender)}'\n" # pylint: disable=invalid-name

        if len(snomed_appender) > 0:
            f.write(f"{snomed} \n")
    f.write("\n\n\n")

    # Compiles Keyword Codes
    for k, v in keyword_dict.items():
        keyword_appender = []
        for code_type, code in v:
            if code_type == "Keyword":
                keyword_appender.append(f"%{str(code)}%")
        keyword = f"{k} Keyword codeset:\n '{','.join(keyword_appender)}'\n" # pylint: disable=invalid-name

        if len(keyword_appender) > 0:
            f.write(f"{keyword} \n")
    f.write("\n\n\n")


f.close()
