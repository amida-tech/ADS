# Medical Code Presence in Dataset

## Script Purpose
This script validates the presence of medical codes in the CDW by ingesting an original file where medical codes were identified. The script should adjust code formats for accurate matching and populate the original file with a "Yes" or "No" in the "In CDW" column to indicate whether each code is present in the CDW.


## How to Use:
1) Navigate inside the Utils folder & download the CDW_code_checker.py file.
2) Make sure you have a med_codes excel file(CDW) as well as another excel file containing the data to be checked. Place med_codes path name in file_path and the other file path in file_path_1 in the script.
3) At the bottom of the script, place output path name in "output_file_path" variable.
4) Run script. A new file with "confirmed_codes" will be generated in the output file path that was set on your local machine.

## Understanding Results
A new spreadsheet 'confirmed codes' will be created where the presence of each code in the CDW will be represented as Yes or No. 

## Inputs
- any dataset with columns containing at LEAST 'Code Set', 'Code', 'Code Description' and 'In CDW'. Ideally the 'In CDW' column will be blank. If not, the script will overwrite anything in that column. 

## Outputs
- Excel file containing the following columns:'Code Set', 'Code', 'Code Description' and 'In CDW' + any other columns. 

## Warnings/Discrepancies 
- code labeled 786.50 in the CDW, but in the arrythmias dataset it was 786.5. Value is not identified by the script but is in the CDW
