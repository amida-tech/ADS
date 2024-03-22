# UMLS API Folder
Make sure you have an account active with [UMLS](https://uts.nlm.nih.gov/uts/umls/home) and a [UMLS API Key](https://uts.nlm.nih.gov/uts/profile) before running these scripts. 

Many of these scripts are very thorough and will frequently return more codes than required. Some codes returned may not be directly relevant to the diagnosis. It is recommended that the analyst reviews the data returned for accuracy concerning their specific diagnosis.

All scripts output can be found in the "output" folder, located in the API folder. 

## File Descriptions
- UMLS SNOMED, ICD10, CPT, and LOINC Decendant and Children Pull
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Checks children of the inputted list of strings
- UMLS SNOMED, ICD10, CPT, and LOINC Quick Pull
    - Returns the SNOMEDCT_US, ICD10, CPT, and LOINC codes associated with an inputted list of strings
    - Does **not** check children of the inputted list of strings

## Single Pulls File Descriptions, Notes and Limitations
### UMLS CPT
- This document will pull all the CPT given parent concept(s), the parent concept(s) children, and export them as an excel file.
- In order to ensure that all desired CPT codes are returned, the type of procedure associated with the diagnosis must be included in the string_list variable search. 
### UMLS ICD10
- This document will pull all the SNOMEDCT_US given parent concept(s), the parent concept(s) children, and export them as an excel file.
### UMLS LOINC
- This document will pull all the LOINC given parent concept(s), the parent concept(s) children, and export them as an excel file.
- The variable "string_list" should contain relevant lab tests (like PFTs), as opposed to the diagnosis of the associated concept.
- LOINC is abbreviated as LNC in UMLS
### UMLS RxNorm
- This document will pull all RxNorm codes of the given generic or name brand medication that are available to UMLS and export them as an excel file. 
- It is recommended that the generic brand of drugs are included in the search to increase the quality of the data returned
- Depending on the length of the string_list variable, this script can take up to 20 minutes to run.  This is normal.  Leave the script running and come back to it later.  If the script's run time exceeds 30 minutes, try running two or more smaller queries (remember to change the Excel_Sheet_Name variable to avoid overwriting your previous output). 
- The RxNorm code for some name brands may not be returned, but their medications will be returned. 
    - Example Returns: 14 ACTUAT Arnuity 0.2 MG/ACTUAT Dry Powder Inhaler, but won't return the RxNorm code for just Arnuity
- It is recommended to include variations of the medication.
    - Ex: if you want to search for Advair, include "Advair", "Advair Diskus", "Advair HFA"
### UMLS SNOMED-CT
- This document will pull all the SNOMEDCT_US given parent concept(s), the parent concept(s) children, and export them as an excel file.
