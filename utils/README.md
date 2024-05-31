# Medical Code Presence in Dataset

## Script Purpose
This script validates the presence of medical codes in the CDW by ingesting an original file where medical codes were identified. The script should adjust code formats for accurate matching and populate the original file with a "Yes" or "No" in the "In CDW" column to indicate whether each code is present in the CDW.


## How to Use:
1) Navigate inside the `utils` folder & download the CDW_code_checker.py file.
2) Make sure you have a `med_codes` Excel file (which represents CDW codes) as well as another Excel file that contains the specific medical data to be checked. Place path name for `med_codes` in `file_path` and the other file path in `file_path_1`.
3) At the bottom of the script, place output path name in `output_file_path`.
4) Run script. A new file titled `confirmed_codes` will be generated in the output file path.

## Understanding Results
A new Excel file titled `confirmed codes` will be created where the presence of each code in the CDW will be represented with "Yes" or "No". 

## Inputs
- Any dataset that contains the following columns at minimum: 'Code Set', 'Code', 'Code Description' and 'In CDW'. Ideally, the 'In CDW' column will be blank. If not, the script will overwrite anything in that column. 

## Outputs
- Excel file containing the following columns:'Code Set', 'Code', 'Code Description' and 'In CDW' + any other columns. 

## Warnings/Discrepancies 
- Run this script before adding additional CDW codes, and double check results. It's possible that additional codes pulled when running `Additional_NDC_Keyword_Search.sql` will appears as "No" in the output file. However, these codes should be marked "Yes" if they were the results of our SQL query.
- Code labeled 786.50 in the CDW, but in the arrythmias dataset it was 786.5. Value is not identified by the script but is in the CDW
