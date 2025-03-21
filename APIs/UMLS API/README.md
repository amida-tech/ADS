# UMLS API Folder
## Script Purpose
These scripts query the UMLS API using a list of keywords and returns medical codes related to the ingested keywords. 

## How to Use:
1) Create an [Unified Medical Language System (UMLS)](https://uts.nlm.nih.gov/uts/umls/home) and obtain your [UMLS API Key](https://uts.nlm.nih.gov/uts/profile) before running these scripts.
2) Navigate inside of the `Single Pulls` folder & download the python file that matches the medical code you are trying to pull (ex: CPT, ICD10, LOINC, RxNorm, SNOMED-CT) 
3) Navigate to your Condition's keyword file in Google Sheets and download the file as a CSV file. This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.
Note: Conditions that contain commas in their description(i.e "Esophagus, stricture of") will not be affected by this conversion to CSV.  When Google Sheets converts a file to a CSV, cell values with commas are encased in double quotations when saved as a CSV to prevent the comma inside the value frm being interpreted as a delimiter. The quotes will typically be removed automatically, and the value will be displayed correctly if you open the file in Excel as a CSV file. 
4) Place your condition's downloaded CSV file in the `inputs` folder.  
5) Update the API_KEY, CONDITION, and CSV_FILE_INPUT_NAME variables at the top of the script with the requested information. 
6) Run the script.  A new file will be generated in the `output` folder with the medical code type appended to the condition (i.e "arrythmia" + "_icd10_codes")

## Understanding Results
- A new Excel file will be created titled based on the CONDITION variable and the medical code script you are running.  For example, the `run_umls_cpt.py` file will output a file titled varicose_veins_cpt_codes if CONDITION = 'varicose_veins'.
- The outputted file will have a list of your chosen medical codes, their code description, the keyword prompting that result.  The outputted file will also have the corresponding VASRD Code, CFR criteria, and Data Concept related to the returned medical code.   

## Inputs
- Your Condition's keyword CSV file in the `inputs` folder.  This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.

## Outputs
- Excel file containing the following columns: 'VASRD Code', 'CFR Criteria', 'Code', 'Code Description', 'Keyword', and 'Data Concept'
- Note: SNOMED-CT outputs two additional columns: 'Semantic Group' and 'Semantic Type'

## Warnings/Discrepancies 
- Read `Python Script Troubleshooting` documentation located in this folder for more information on commonly returned errors and troubleshooting steps. 