"""
This script will reverse map ICD-10 codes to ICD-9 codes using the GEMs files
and clean the results for user review.

Script assumes that the input file includes a "Code Set Details" sheet that includes ICD-10 codes
and is formatted appropriately.
Script also assumes that 2018_I10gem.csv and ICD9_CMS32_DESC_LONG_SHORT_DX.xlsx files are
located in the GEMS folder.
"""


# Import Libraries
import pandas as pd


# Codes to Check- Enter any medical codes file here.
CODE_SET_NAME = ""  # Enter name of Code Set as it is stored in the input folder

# Full code set file with named sheets. Make sure an updated version is in the input
# folder and the sheets are accurately named.
FILE_PATH_1 = f"input/{CODE_SET_NAME}.xlsx"
SHEET_NAME = "Code Set Details"
CodeSet = pd.read_excel(FILE_PATH_1, sheet_name=SHEET_NAME)
ICD10List = CodeSet[CodeSet['Code Set'] == 'ICD-10']

# Do not change these variables
GEMS = pd.read_csv('2018_I10gem.csv', dtype=str)
ICD9desc = pd.read_excel('ICD9_CMS32_DESC_LONG_SHORT_DX.xlsx')

# Format ICD10 file for use
ICD10List = ICD10List.rename({'Code': 'ICD10'}, axis=1)
ICD10List = ICD10List.rename({'Code Description': 'ICD10 Name'}, axis=1)
ICD10List['ICD10'] = ICD10List['ICD10'].str.replace('.', '')

# Join ICD10 code list and GEMs file
AddICD9 = pd.merge(ICD10List, GEMS, on=['ICD10'], how='left')

# Add descriptions
AddICD9 = pd.merge(AddICD9, ICD9desc, on=['ICD9'], how='left')

# Reformat ICD9 and ICD10 codes, names
AddICD9['ICD9'] = AddICD9['ICD9'].str[:3] + '.' + AddICD9['ICD9'].str[3:]
AddICD9['ICD10'] = AddICD9['ICD10'].str[:3] + '.' + AddICD9['ICD10'].str[3:]
ICD9codes = AddICD9
ICD9codes = ICD9codes.rename({'LONG DESCRIPTION': 'ICD9 Name'}, axis=1)
ICD9codes['Code Set'] = "ICD-9"  # Set 'Code Set' column to "ICD-9"
# Filter and sort columns to keep
ICD9codes = ICD9codes.loc[:, ['VASRD Code', 'CFR Criteria', 'Code Set',
                              'ICD9', 'ICD9 Name', 'Flag', 'ICD10', 'ICD10 Name']]


# Remove rows where ICD9 or Flag columns are blank
ICD9codes = ICD9codes[ICD9codes['ICD9'].notna()]
ICD9codes = ICD9codes[ICD9codes['Flag'].notna()]


def flag_review(i):
    """Converting flag to readable format"""
    if isinstance(i, str):
        flag = str(i[0:3])
        if flag == '000':
            return "Accurate"
        if flag == '100':
            return "Approximate"
        if flag == '101':
            return "Requires combination"
    return None


ICD9codes['Flag'] = ICD9codes['Flag'].apply(flag_review)


# Creating dataframe for codes with flags starting with 000, 100 or 101
# Codes flagged as approximate or requiring combination need further review

FinalICD9 = ICD9codes[ICD9codes['Flag'].isin(
    ['Accurate', 'Approximate', 'Requires combination'])]

# For the dataframe that needs manual review, concatenate the VASRD, CFR Criteria, ICD-10 codes
# and ICD-10 descriptions if there are duplicate rows
FinalICD9 = FinalICD9.groupby('ICD9', as_index=False).agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(sorted(set(x))),
    'Code Set': 'first',
    'ICD9': 'first',
    'ICD9 Name': 'first',
    'Flag': 'first',
    'ICD10': lambda x: '; '.join(sorted(set(x))),
    'ICD10 Name': lambda x: '; '.join(sorted(set(x)))
})


# A new file of mapped ICD-9 codes will be generated. Manual review of codes with
# an "Approximate" or "Requires Combination" Flag is necessary.

OUTPUT_FILE_PATH = f"output/{CODE_SET_NAME}_confirmed.xlsx"
FinalICD9.to_excel(OUTPUT_FILE_PATH, index=False)

# Print a message indicating where the file is saved
print(
    f"Excel file '{CODE_SET_NAME}_confirmed.xlsx' saved in the output folder.")
