# UMLS API Folder

## File Descriptions
- UMLS RxNorm Codes Pull 
    - Returns the RxNorm codes associated with an inputted generic or name brand medication
- UMLS SNOMED, ICD10, CPT, and LOINC Pull
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Checks children of the inputted list of strings
- UMLS SNOMED, ICD10, CPT, and LOINC Pull-Refactor (Runs faster than original, less data returned)
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Does **not** check children of the inputted list of strings

## Folder Description
- Single Pulls
    - Contains script to pull only one type of coding standard at a time
        - CPT
        - ICD10
        - LOINC
        - SNOMEDCT_US
