# General Equivalnce Mappings (GEMs): ICD-10 to ICD-9 

## GEMs Backward Mapping
This script uses General Equivalnce Mappings (GEMs) to do backward mappings from ICD-10 codes to ICD-9 codes. 

Steps: 
1. Create an excel file with only ICD-10 codes and corresponding names/descriptions for running this script. 
2. Add your ICD-10 code file into the "Input" folder.
3. Update the following variables in the `ICD10toICD9_backward_mapping.py` script:
    - Update `Condition` to the diagnosis code sets you are using
    - Update `ICD10List` to your ICD-10 file location
    - Update `ICD10CodeColumn` to the column name of where your ICD-10 codes are in your ICD-10 sheet 
    - Update `ICD10Name` to the column name of where your ICD-10 descriptions/names are in your ICD-10 sheet  
4. Run script with in the GEMs folder

## Understanding Results
Not all ICD-10 codes will have ICD-9 codes.  

There are three columns (Match, Corresponding Code, Requires Combination) that interprets the flag column to help with any analysis. 

Type of match can be "Accurate" or "Approximate." When "Accurate", this indicates a 1-to-1 match. "Approximate" indicates that the match is probable, but is not a direct 1-to-1 match. For example, ICD-10 code C18.1 (Malignant neoplasm of appendix) is a direct match to ICD-9 code 153.5 (Malignant neoplasm of appendix vermiformis). ICD-10 code C22.2 (Hepatoblastoma) is an approximate match to ICD-9 155.0 (Malignant neoplasm of liver, primary).

If there is no corresponding code, this means that the ICD-10 code is in the GEMs file, but does not have a corresponding ICD-9 code. 

When a mapped ICD-9 code requires a combination, this indicates that two or more ICD-9 codes are needed to map correctly to the ICD-10 code. Please review ICD-9 code and remove if needed. For example, ICD-10 code E10.36 (Type 1 diabetes mellitus with diabetic cataract) will need both ICD-9 codes 250.51 (Diabetes with ophthalmic manifestations, type I [juvenile type], not stated as uncontrolled) and 366.41 (Diabetic cataract) to be a more accurate match. 

"No Match" in any of the flag columns indicates that the GEMs file does not have that ICD-10 code included. 

For cases where there is no match, no corresponding code, or requires a combination, further reasearch into that code may be required. 

Note. There may be duplicate ICD-9 codes in the file. Please remove any duplicates for final code set file. 

## Inputs
- `2018_I10gems.csv` : 2018 General Equivalnce Mappings from [CMS](https://www.cms.gov/medicare/coding-billing/icd-10-codes/2018-icd-10-cm-gem)
- `ICD9_CMS32_DESC_LONG_SHORT_DX.xlsx` : ICD-9 Full and Abbreviated Code Titles from [CMS](https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-9-cm-diagnosis-procedure-codes-abbreviated-and-full-code-titles)
- `ICD10toICD9_backward_mapping.py` : Mapping file to go from ICD-10 codes to find equivalent ICD-9 codes
- ICD-10 code list with names/descriptions

## Outputs
- Excel file containing the following columns: 
    - `ICD10` (ICD-10 codes)
    - `ICD10 Name` (ICD-10 Names/Description)
    - `ICD9` (ICD-9 codes)
    - `ICD9 Name` (ICD-9 Names/Description)
    - `Match` (Type of Match)
    - `Corresponding Code` (If there is a corresponding code)
    - `Requires Combination` (If two or more ICD-9 codes are needed for mapping)
