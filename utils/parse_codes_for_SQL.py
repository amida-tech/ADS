"""
This script is a modified version of parse_all_codes.py but includes:

- Conversion of CFR criteria names into camelCase for consistency
- Removal of special characters from CFR criteria keys
- Formatting output variables as SQL `DECLARE` statements
"""

import pandas as pd

NAME_OF_CODE_SET = ""  # Enter name of condition(Arrythmias, GI Cancer etc.)
FILE_NAME = ""  # Enter file name stored in input folder

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

# Code below sourced from a website to convert CFR Criteria to camelCase
main = {
    ''.join(
        word.title() if i else word for i,
        word in enumerate(
            k.split(' '))): v for k,
    v in main.items()}

for key in list(main.keys()):
    new_key = key.replace(
        ",",
        "").replace(
        "(",
        "").replace(
            ")",
            "").replace(
                "'",
                "").replace(
                    "-",
                    "").replace(
                        "/",
                        "").replace(
                            ":",
        "")

    if new_key != key:
        main[new_key] = main.pop(key)


# creating tuples of Code Set and Code(Keyword)
df['Tuple_part_2'] = list(zip(df['Code Set'], df["Code Description"]))

keyword_dict = (df.groupby('CFR Criteria')['Tuple_part_2'].apply(list).to_dict())
# Code below sourced from a website to convert CFR Criteria to camelCase
keyword_dict = {
    ''.join(
        word.title() if i else word for i,
        word in enumerate(
            k.split(' '))): v for k,
    v in keyword_dict.items()}

for key in list(keyword_dict.keys()):
    new_key = key.replace(
        ",",
        "").replace(
        "(",
        "").replace(
            ")",
            "").replace(
                "'",
                "").replace(
                    "-",
                    "").replace(
                        "/",
                        "").replace(
                            ":",
        "")

    if new_key != key:
        keyword_dict[new_key] = keyword_dict.pop(key)

with open(OUTPUT_DIRECTORY, "w", encoding="utf-8") as f:

    f.write(f"{NAME_OF_CODE_SET} \n\n")

    # Compiles all LOINC Codes
    # for k,v in main.items():
    #    loinc_appender = []
    #    for code_type, code in v:
    #        if code_type == "LOINC":
    #            loinc_appender.append(str(code))
    #    loincs = f"{k} LOINC codeset:\n '{','.join(loinc_appender)}'\n"

    #    if len(loinc_appender) > 0:
    #        f.write(f"{loincs} \n")
    # f.write("\n\n\n")

    # Compiles all ICD-10 Codes
    f.write("/*ICD-10 Codes*/\n\n")
    for k, v in main.items():
        icd_10_appender = []
        for code_type, code in v:
            if code_type == "ICD-10":
                icd_10_appender.append(str(code))
        icd_10 = f"Declare @{k}_ICD10 AS VARCHAR(MAX) = ('{','.join(icd_10_appender)}')" # pylint: disable=invalid-name

        if len(icd_10_appender) > 0:
            f.write(f"{icd_10} \n")
    f.write("\n\n\n")

    # Compiles all CPT Codes
    f.write("/*CPT Codes*/\n\n")
    for k, v in main.items():
        cpt_appender = []
        for code_type, code in v:
            if code_type == "CPT":
                cpt_appender.append(str(code))
        cpt = f"Declare @{k}_cptcodes AS VARCHAR(MAX) = ('{','.join(cpt_appender)}')" # pylint: disable=invalid-name

        if len(cpt_appender) > 0:
            f.write(f"{cpt} \n")
    f.write("\n\n\n")

    # Compiles all ICD-9 Codes
    f.write("/*ICD-9 Codes*/\n\n")
    for k, v in main.items():
        icd_9_appender = []
        for code_type, code in v:
            if code_type == "ICD-9":
                icd_9_appender.append(str(code))
        icd_9 = f"Declare @{k}_ICD9 AS VARCHAR(MAX) = ('{','.join(icd_9_appender)}')" # pylint: disable=invalid-name

        if len(icd_9_appender) > 0:
            f.write(f"{icd_9} \n")
    f.write("\n\n\n")

    # Compiles NDC Codes
    # for k,v in main.items():
    #    ndc_appender = []
    #    for code_type, code in v:
    #        if code_type == "NDC":
    #          ndc_appender.append(f"{str(code)}%")
    #    ndc = f"{k} NDC codeset:\n '{','.join(ndc_appender)}'\n"

    #    if len(ndc_appender) > 0:
    #        f.write(f"{ndc} \n")
    # f.write("\n\n\n")

    # Compiles all SNOMED-CT Codes
    f.write("/*SNOMED_CT Codes*/\n\n")
    for k, v in main.items():
        snomed_appender = []
        for code_type, code in v:
            if code_type == "SNOMED-CT":
                snomed_appender.append(str(code))
        snomed = f"Declare @{k}_SNOMEDCodes AS VARCHAR(MAX) = ('{','.join(snomed_appender)}')" # pylint: disable=invalid-name

        if len(snomed_appender) > 0:
            f.write(f"{snomed} \n")
    f.write("\n\n\n")

    # Compiles Keyword Codes
    f.write("/*Drug Keywords*/\n\n")
    for k, v in keyword_dict.items():
        keyword_appender = []
        for code_type, code in v:
            if code_type == "Keyword":
                keyword_appender.append(f"%{str(code)}%")
        keyword = f"Declare @{k}_keywords = ('{','.join(keyword_appender)}')" # pylint: disable=invalid-name

        if len(keyword_appender) > 0:
            f.write(f"{keyword} \n")
    f.write("\n\n\n")


f.close()
