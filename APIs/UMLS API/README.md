# 1. Unified Medical Language System (UMLS) medical code python scripts 

## Script Purpose
These scripts query the UMLS API using a list of keywords and returns medical codes related to the ingested keywords.  These scripts include: 
- `run_umls_cpt.py`
- `run_umls_icd10.py`
- `run_umls_loinc.py`
- `run_umls_rxnorm.py`
- `run_umls_snomed.py`

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

# 2. LOINC backwards medical mapping script

## Overview
The script `loinc_backwards_mapping.py` will ingest a list of LOINC codes and output relational information and data using the UMLS API.

## Usage
1) Create an [Unified Medical Language System (UMLS)](https://uts.nlm.nih.gov/uts/umls/home) and obtain your [UMLS API Key](https://uts.nlm.nih.gov/uts/profile) before running these scripts.
2) Navigate inside of the `Single Pulls` folder & download the `loinc_backwards_mapping.py` file 
3) Navigate or create an Excel file with a list of LOINC codes. Ensure that the column title of the LOINC codes is "LOINC_CODE".
Note: This script ingests and Excel file while the other UMLS scripts ingest a CSV file.  
4) Place your Excel file with a list of LOINC codes in the `inputs` folder.    
5) Update the API_KEY, INPUT_FILE_NAME, and OUTPUT_FILE_NAME variables at the top of the script with the requested information. 
6) Run the script.  A new file will be generated in the `output` folder with the default name `test_loinc_results` or a file name matching the variable `OUTPUT_FILE_NAME`'s assigned string value.

## Understanding Results
A new Excel file with the deafult name `test_loinc_results` will be created. The file name will vary depending on the name inputted to the  `OUTPUT_FILE_NAME` variable. 

## Inputs
- An Excel file that contains a column titled "LOINC_CODE", with a list of at least 1 LOINC code in the list.   

## Outputs
- Excel file that contains the following columns: 
    - "LOINC_CODE": The LOINC code ingested
    - "LOINC Description": The UMLS name of the LOINC code
    - "answer_to":  Indicates that the LOINC code is an answer to a question or part of a question-answer relationship. Typically LOINC codes are either "answer_to" or not "answer_to" codes 
    - "has_class": Specifies the classification or category the LOINC code belongs to
    - "has_system": Identifies the system or specimen involved (e.g., blood, urine)
    - "has_component": Refers to the main analyte, element, or part being measured or assessed
    - "analyzes": Represents the concept being analyzed or examined
    - "measures": Specifies the entity or concept being measured (e.g., vital signs, lab values)
    - "evaluation_of_relation_1": Custom attribute representing the first evaluation-related relationship
    - "evaluation_of_relation_2": Custom attribute representing the second evaluation-related relationship
    - "Official LOINC Name": The official LOINC code name, this name is often longer and not as human-readable 

## Warnings/Discrepancies 
- LOINC codes that fall under the "answer_to" category may report "Not Found" for the majority of the other relational categories.  If you would like more information on these LOINC codes, it is recommended that you use UMLS to find the associated LOINC code and query that code for more information. 
