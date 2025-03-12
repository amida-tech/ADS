# 1. Pull the Established Pharmacologic Class (EPC) from a Medication String

## Overview
The script `run_epc_from_keyword.py` returns the Established Pharmacologic Class (EPC) of a medication name by ingesting an original file where medication names were identified.

## Usage
1) Naviagte inside the `RxNav API` folder & download the `run_epc_from_keyword.py` file. 
2) Make sure you have an Excel file with the medication keywords located in the `input` folder.  This file will need a column titled "Keyword". 
3) Update the `INPUT_FILE_NAME` input variable with the name of the input excel file. 
- Optional: Update the `OUTPUT_FILE_NAME` variable if desired.  Otherwise, the outputted file name will be `drug_epc_results`.
4) Run script.  A new file will be generated titled `drug_epc_results` in the output file path.
- Note: The default output file path is the `output` folder

## Understanding Results
A new Excel file titled `drug_epc_results` will be created.  The file will have two columns: "Drug Name" and "RxNorm API EPC".  "Drug Name" relates to the inputted keyword, while the "RxNorm API EPC" reflects the gathered EPC.

## Inputs
The required input is an Excel file with a column labled "Keyword", with a list of medication strings in that column. 

## Outputs
The output is a structured Excel file titled `drug_epc_results` with two columns: "Drug Name" and "RxNorm API EPC".

## Warnings/Discrepancies 
- If you run the script again for a different set of keywords, consider changing the output file name in the last line of the code to avoid overwriting your previous file. 
- Ensure the input Excel file follows the expected format outlined in each python file

# 2. Pull Medication RxNav Relations (ATC1-4, EPC, may_treat, and VA Class) from a RxNorm Code

## Overview
The script `run_rxnorm_classes.py` processes RxNorm codes from an Excel file and outputs different RxNav relations (ATC1-4, EPC, may_treat, and VA Class) associated with the inputted RxNorm codes. 

## Usage
1) Naviagte inside the `RxNav API` folder & download the `run_rxnorm_classes.py` file. 
2) Make sure you have an Excel file with the first column titled "Code Value" with RxNorm codes and the second column titled "Code Description" with the RxNorm names, located in the `input` folder. 
3) Update the `INPUT_FILE_NAME` input variable with the name of the input excel file. 
- Optional: Update the `OUTPUT_FILE_NAME` variable if desired.  Otherwise, the outputted file name will be `drug_epc_results`.
4) Run script.  A new file will be generated titled `drug_epc_results` in the output file path.
- Note: The default output file path is the `output` folder

## Understanding Results
A new Excel file titled `complete_rxnorm_classes` will be created. The file will have six columns: "Code Value", "Code Description", "VA Class", "EPC", "ATC1-4", and "May Treat".  
- "Code Value" relates to the inputted RxNorm code
- "Code Description" relates to the RxNorm medication name 
- "VA Class" relates to the VA Class associated with the RxNorm code and Code Description 
- "EPC" relates to the Established Pharmacologic Class associated with the RxNorm code and Code Description 
- "ATC1-4" relates to the Anatomical Therapeutic Chemical Classification associated with the RxNorm code and Code Description
- "May Treat" relates to the possible diagnoses that are associated with the RxNorm code and Code Description

## Inputs
The required input is an Excel file with the first column titled "Code Value" with a list of RxNorm codes in that column and a second column titled "Code Description" with the name of the medications. 

## Processing Details
- Reads the input Excel file with RxNorm codes and cycle through each of them, querying the RxNav API for each
- If the query returns no ATC1-4/EPC/may_treat/VA Class variables, the script will return "No ATC1-4/EPC/may_treat/VA Class Found"
- If the query returns 1 ATC1-4/EPC/may_treat/VA Class variable, the script will return each variable in associated column ("ATC1-4", "EPC", "may_treat", or "VA Class") on the outputted Excel sheet by the corresponding Code Value and Code Description row. 
- For RxNorm calls with multiple ATC1-4/EPC/may_treat/VA Class variables, each unique entry will apepar separated by a semicolon and one space.

## Outputs
The output is a structured Excel file titled `complete_rxnorm_classes` with six columns: "Code Value", "Code Description", "VA Class", "EPC", "ATC1-4", and "May Treat".

## Warnings/Discrepancies 
- If you run the script again for a different set of keywords, consider changing the output file name in the last line of the code to avoid overwriting your previous file. 
- Ensure the input Excel file follows the expected format outlined in each python file