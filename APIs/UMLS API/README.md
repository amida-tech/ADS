# UMLS API Folder
Before being able to use these scripts, you must create an account with UMLS. The website can be found [here](https://uts.nlm.nih.gov/uts/profile). After your account has been approved, navigate to your [profile](https://uts.nlm.nih.gov/uts/profile) and find your APIKey. This is required for this script to run.

## File Descriptions
- UMLS SNOMED, ICD10, CPT, and LOINC Decendant and Children Pull
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Checks children of the inputted list of strings
- UMLS SNOMED, ICD10, CPT, and LOINC Quick Pull
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Does **not** check children of the inputted list of strings

## File Notes
- UMLS SNOMED, ICD10, CPT, and LOINC Quick Pull
    - This document will pull all the SNOMEDCT_US, ICD10, CPT, and LOINC code of the given concept(s) and export them as an excel file. Note that this **does not** pull descendants or children of the concepts given.  This will run more efficiently, but it may not have all calls that you are looking for.  Use UMLS Decendant and Children Pull even more detailed data pull (it just takes a while to compile).
- UMLS SNOMED, ICD10, CPT, and LOINC Decendant and Children Pull
    - This document will pull all the SNOMEDCT_US, ICD10, CPT, and LOINC code of the given parent concept(s), the parent concept(s) children, and export them as an excel file.
    - This script is very thorough and will frequently return more codes than required. Some codes returned may not be directly relevant to the diagnosis. It is recommended that the analyst reviews the data returned for accuracy concerning their specific diagnosis.

## Folder Description
- Single Pulls
    - Contains script to pull only one type of coding standard at a time
        - CPT
        - ICD10
        - LOINC
        - SNOMEDCT_US
        - RxNorm
