# General Equivalence Mappings (GEMs): ICD-10 to ICD-9 

## GEMs Backward Mapping
This script uses General Equivalence Mappings (GEMs) to do backward mappings from ICD-10 codes to ICD-9 codes. 

Steps: 
1. Add your Code Set file into the "Input" folder. Make sure the "Code Set Details" sheet is present
2. Update the CODE_SET_NAME variable in the `icd10_to_icd9_backward_mapping.py` script to match the name of your code set file
3. Run script within the GEMs folder
4. Review output file before adding ICD-9 codes to Code Set File, specifically codes with the "Approximate" or "Requires combination" flags

## Understanding Results
This script output is formatted to be copy and pasted into the code set details tab of the code set file, once the user reviews the "Approximate" and "Requires combination" flagged rows. 

Duplicate rows of ICD-9 codes have been concatenated on the `VASRD Code`, `CFR Criteria`, `ICD10` and `ICD10 Name` columns. These rows are marked in the `Flag` column as either "Approximate" or "Requires combination" and must be reviewed by the user. Upon review, the user must determine if the concatenated VASRD Code and CFR Criteria need correction. Rows that are flagged as "Accurate" provide a one to one match between ICD-10 and ICD-9 codes, these rows do not need further review.

"Approximate" indicates that the match is probable, but is not a direct 1-to-1 match. For example, ICD-10 code C18.1 (Malignant neoplasm of appendix) is a direct match to ICD-9 code 153.5 (Malignant neoplasm of appendix vermiformis). ICD-10 code C22.2 (Hepatoblastoma) is an approximate match to ICD-9 155.0 (Malignant neoplasm of liver, primary).

When a mapped ICD-9 code requires a combination, this indicates that two or more ICD-9 codes are needed to map correctly to the ICD-10 code. Please review ICD-9 code and remove if needed. For example, ICD-10 code E10.36 (Type 1 diabetes mellitus with diabetic cataract) will need both ICD-9 codes 250.51 (Diabetes with ophthalmic manifestations, type I [juvenile type], not stated as uncontrolled) and 366.41 (Diabetic cataract) to be a more accurate match. 

This script will remove all codes from output where an ICD-10 code was not matched to an ICD-9 code, or if the code was flagged as not having a corresponding code.

After review of ICD-9 output, the `VASRD Code`, `CFR Criteria`, `Code Set`, `ICD9` and `ICD9 Name` columns can be copy and pasted into the final code set.

## Inputs
- `2018_I10gems.csv` : 2018 General Equivalnce Mappings from [CMS](https://www.cms.gov/medicare/coding-billing/icd-10-codes/2018-icd-10-cm-gem)
- `ICD9_CMS32_DESC_LONG_SHORT_DX.xlsx` : ICD-9 Full and Abbreviated Code Titles from [CMS](https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-9-cm-diagnosis-procedure-codes-abbreviated-and-full-code-titles)
- `icd10_to_icd9_backward_mapping.py` : Mapping file to go from ICD-10 codes to find equivalent ICD-9 codes
- Code Set file with Code Set Details sheet

## Outputs
- Excel file containing the following columns: 
    - `VASRD Code` (VASRD Codes pulled from the ICD-10 equivalent/s)
    - `CFR Criteria` (CFR Criteria pulled from the ICD-10 equivalent/s)
    - `Code Set` (Identifier of Code Set type)
    - `ICD9` (ICD-9 Code)
    - `ICD9 Name` (ICD-9 Description)
    - `Flag` (Readable format of flag from GEMs file)
    - `ICD10` (ICD-10 Code - only present if ICD-9 code requires review)
    - `ICD10 Name` (ICD-10 Description - only present if ICD-9 code requires review)
