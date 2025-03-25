# UMLS API Folder
## Script Purpose
These scripts query the UMLS API using a list of keywords and returns medical codes related to the ingested keywords. 

## How to Use:
1) Create an [Unified Medical Language System (UMLS)](https://uts.nlm.nih.gov/uts/umls/home) and obtain your [UMLS API Key](https://uts.nlm.nih.gov/uts/profile) before running these scripts.
2) Navigate inside of the `single_pulls` folder & download the python file that matches the medical code you are trying to pull (ex: CPT, ICD10, LOINC, RxNorm, SNOMED-CT) 
3) Navigate to your Condition's keyword file in Google Sheets and download the file as a CSV file. This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.
Note: Conditions that contain commas in their description(i.e "Esophagus, stricture of") will not be affected by this conversion to CSV.  When Google Sheets converts a file to a CSV, cell values with commas are encased in double quotations when saved as a CSV to prevent the comma inside the value frm being interpreted as a delimiter. The quotes will typically be removed automatically, and the value will be displayed correctly if you open the file in Excel as a CSV file. 
4) Place your condition's downloaded CSV file in the `inputs` folder.  
5) Update the API_KEY, CONDITION, and CSV_FILE_INPUT_NAME variables at the top of the script with the requested information. 
6) Run the script.  A new file will be generated in the `output` folder with the medical code type appended to the condition (i.e "arrythmia" + "_icd10_codes")

## Understanding Results
- A new Excel file will be created titled based on the CONDITION variable and the medical code script you are running.  For example, the `run_umls_cpt.py` file will output a file titled varicose_veins_cpt_codes if CONDITION = 'varicose_veins'. The output file will have seven columns (nine if SNOMED-CT): "VASRD Code", "CFR Criteria", "Code Set", "Code", "Code Description", "Keyword", "Data Concept", and (for SNOMED-CT scripts only) "Semantic Group" and "Semantic Type". 
- "VASRD Code": The Veterans Affairs Schedule for Rating Disabilities (VASRD) code extracted from the federal eCFR (Electronic Code of Federal Regulations). It represents the diagnostic code used for evaluating disability claims.
- "CFR Criteria": The regulatory criteria sourced from the keywords mapping file. This column contains the specific CFR (Code of Federal Regulations) language or conditions related to the medication keyword.
- "Code Set": The reference or classification system associated with the medication keyword, obtained from the keywords mapping file (ex: NDC)
- "Code": The National Drug Code (NDC) or equivalent identifier returned by the openFDA API. This unique code identifies the drug product, including the labeler, product, but excludes the package segments for VA formatting standards (see "Warnings/Discrepancies" for more information).
- "Code Description": A detailed description of the drug product associated with the NDC code, retrieved from the openFDA API. This typically includes the generic name, brand name, and strength.
- "Keyword": The medication keyword from the keywords mapping file, used as the search term for querying the openFDA API. It may represent a generic or brand name.
- "Data Concept": The classification label from the keywords mapping file, indicating the category of the keyword (e.g., Diagnosis, Symptoms, Procedure, Lab, etc.).
- "Semantic Group" (SNOMED-CT): The broad UMLS classification category assigned to the concept in SNOMED-CT dataset calls. Semantic groups categorize medical concepts into high-level groups (e.g., Disorders, Chemicals & Drugs, Anatomy, Procedures) to simplify concept organization.  This column is only available in the `run_umls_snomed.py` file.
- "Semantic Type" (SNOMED-CT): The more granular UMLS classification that describes the specific type of concept within the semantic group. Semantic types provide detailed categorization (e.g., Clinical Drug, Antibiotic, Finding, Disease or Syndrome), offering more precise medical context. This column is only available in the `run_umls_snomed.py` file.

## Inputs
- Your Condition's keyword CSV file in the `inputs` folder.  This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.

## Outputs
- Excel file containing the following columns: 'VASRD Code', 'CFR Criteria', 'Code', 'Code Description', 'Keyword', and 'Data Concept'
- Note: SNOMED-CT outputs two additional columns: 'Semantic Group' and 'Semantic Type'

## Warnings/Discrepancies 
- Read `Python Script Troubleshooting` documentation located in this folder for more information on commonly returned errors and troubleshooting steps. 