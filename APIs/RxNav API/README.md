# 1. Pull the Established Pharmacologic Class (EPC) from a Medication String

## Overview
The script `run_epc_from_keyword_call.py` returns the Established Pharmacologic Class (EPC) of a medication name by ingesting an original file where medication names were identified.

## Usage
1) Naviagte inside the `RxNav API` folder & download the `run_epc_from_keyword_call.py` file. 
2) Make sure you have an Excel file with the medication keywords located in the `input` folder. 
3) At the bottom of the script, update the `EXCEL_FILE` input variable with the name of the input excel file. 
- Optional: Update the output file name if desired.  Otherwise, the outputted file name will be `drug_epc_result`.
4) Run script.  A new file will be generated titled `drug_epc_result` in the output file path.
- Note: The default output file path is the `output` folder

## Understanding Results
A new Excel file titled `drug_epc_result` will be created.  The file will have two columns: "Drug Name" and "RxNorm API EPC".  "Drug Name" relates to the inputted keyword, while the "RxNorm API EPC" reflects the gathered EPC.

## Inputs
The required input is an Excel file with the first column labled "Keywords", with a list of medication strings in that column. 

## Outputs
The output is a structured Excel file titled 'drug_epc_results' with two columns: "Drug Name" and "RxNorm API EPC".

## Warnings/Discrepancies 
- If you run the script again for a different set of keywords, consider changing the output file name in the last line of the code to avoid overwriting your previous file. 

# 2. Pull Medication RxNav Relations (ATC1-4, EPC, may_treat, and VA Class) from a RxNorm Code

## Overview
The scripts `run_atc1_4_class_call.py`, `run_epc_from_rxnorm_codes_call.py`, `run_may_treat_class_call.py`, and `run_va_class_call.py` process RxNorm codes from Excel files and outputs different RxNav relations (ATC1-4, EPC, may_treat, and VA Class) associated with the inputted RxNorm codes. 

## Usage
### Script 1: `run_atc1_4_class_call.py`
This script processes RxNorm codes and returns the code's Anatomical Therapeutic Chemical (ATC) Classification. The required input is an excel file with two columns: "Code Value" and "Code Description". The output is a structured excel file titled 'atc1_4_class_results' with three columns: "Code Value",  "Code Description", "ATC1-4".

### Script 2: `run_epc_from_rxnorm_codes_call.py`
This script processes RxNorm codes and returns the code's Established Pharmacologic Class (EPC). The required input is an excel file with two columns: "Code Value" and "Code Description". The output is a structured excel file titled 'epc_class_results' with three columns: "Code Value",  "Code Description", "EPC".

### Script 3: `run_may_treat_class_call.py`
This script processes RxNorm codes and returns the code's [may_treat](https://lhncbc.nlm.nih.gov/RxNav/applications/RxClassIntro.html) relation. The required input is an excel file with two columns: "Code Value" and "Code Description". The output is a structured excel file titled 'may_treat_results' with three columns: "Code Value",  "Code Description", "May Treat".

### Script 4: `run_va_class_call.py`
This script processes RxNorm codes and returns the code's Veteran Administration Class. The required input is an excel file with two columns: "Code Value" and "Code Description". The output is a structured excel file titled 'va_class_results' with three columns: "Code Value",  "Code Description", "VA Class".

### Steps (For All Scripts)
1. Set `INPUT_FILE` to the name of the input Excel file located in the `input` folder. 
- Optional: Update the `OUTPUT_FILE` variable name, if desired
2. Run the script to generate a formatted output file in the `output/` folder

### Processing Details (For All Scripts)
- Reads the Excel file with RxNorm codes and cycle through each of them, querying the RxNav API for each
- If the query returns no ATC1-4/EPC/may_treat/VA Class variables, the script will return "No ATC1-4/EPC/may_treat/VA Class Found"
- If the query returns 1 ATC1-4/EPC/may_treat/VA Class variable, the script will return each variable in associated column ("ATC1-4", "EPC", "may_treat", or "VA Class") on the outputted Excel sheet by the corresponding Code Value and Code Description row. 
- For RxNorm calls with multiple ATC1-4/EPC/may_treat/VA Class variables, each unique entry will apepar separated by a semicolon and one space.

## Output
Each script generates an excel file with structured data. The `run_atc1_4_class_call.py`, `run_epc_from_rxnorm_codes_call.py`, `run_may_treat_class_call.py`, and `run_va_class_call.py` outputs an excel file with three columns: "Code Value",  "Code Description", and "ATC1-4/. The last column name depends on the information pulled. The `run_epc_from_keyword_call.py` outputs an excel file with two columns: "Drug Name" and "RxNorm API EPC".

## Notes
- Ensure the input Excel file follows the expected format outlined in each python file