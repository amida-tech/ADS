# 1. Check for Medical Codes in CDW Dataset

## Overview
The script `CDW_code_checker.py` validates the presence of medical codes in the CDW by ingesting an original file where medical codes were identified. The script should adjust code formats for accurate matching and populate the original file with a "Yes" or "No" in the "In CDW" column to indicate whether each code is present in the CDW.

## Usage
1) Navigate inside the `utils` folder & download the `CDW_code_checker.py` file.
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
- Abstain from running code in Jupyter Notebooks. There is a bug causing some CPT codes to not be identified. VSCode is highly preferred.
- Run this script before adding additional CDW codes, and double check results. It's possible that additional codes pulled when running `Additional_NDC_Keyword_Search.sql` will appears as "No" in the output file. However, these codes should be marked "Yes" if they were the results of our SQL query.
- Code labeled 786.50 in the CDW, but in the arrythmias dataset it was 786.5. Value is not identified by the script but is in the CDW

# 2. Parse Inputs for SQL Queries

## Overview
The scripts `parse_all_codes.py` and `parse_codes_for_SQL.py` process and format medical code sets from Excel files into structured text outputs. They extract, filter, and categorize different code types (ICD-10, CPT, NDC, etc.) based on CFR criteria and save the results in a formatted text file.

## Usage
### Script 1: `parse_all_codes.py`
This script processes medical codes and categorizes them by their associated CFR criteria. The output is a structured text file containing different sets of codes (ICD-10, CPT, NDC, etc.).

#### Steps
1. Set `Name_of_Code_Set` to the name of the condition (e.g., "Arrhythmias")
2. Set `file_name` to the name of the Excel file (without extension) in the `codeset/input/` folder
3. Run the script to generate a formatted output file in `codeset/output/`

#### Processing Details

- Reads the Excel file and filters out entries where `In CDW` is marked "No"
- Splits CFR criteria if multiple values exist, creating separate entries
- Groups codes by CFR criteria and code type (e.g., ICD-10, CPT, NDC, etc.)
- Writes the results into a text file in `codeset/output/`

### Script 2: `parse_codes_for_SQL.py`
This script is a modified version of the first but includes:

- Conversion of CFR criteria names into camelCase for consistency
- Removal of special characters from CFR criteria keys
- Formatting output variables as SQL `DECLARE` statements

#### Steps:
1. Set `Name_of_Code_Set` and `file_name` as described above.
2. Run the script to generate a structured text file containing SQL variable declarations for each code category.

#### Processing Details:
- Converts CFR criteria keys into camelCase
- Cleans special characters from key names
- Writes output in SQL-friendly format and defines `VARCHAR(MAX)` variables for each category of codes

## Output
Each script generates a text file with structured data. The first script produces readable grouped codes, while the second script structures output as SQL variables.

## Notes
- Ensure the input Excel file follows the expected format
- CFR criteria must be consistently named to avoid duplicate keys
- Special characters in CFR criteria are removed in the second script for SQL compatibility