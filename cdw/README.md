# CDW: Retrieve codesets from CDW

## Purpose:
This script retrieve codesets by connecting to CDW-CDWWork and allows the user to input a list of codes (.txt) format to search on and outputs as a .csv file. It will be built out to support various functionalities such as other codesets (ICD, LOINC, NDC, etc.) or other functionality as well to pull data from CDW.

## Important notes:
- This script is only to successfully connect if you have access to CDW-CDWWork database and the VA network
- Ensure your python libraries are installed prior to running the script if it's your first time running
- Each input file is formatted as a list of codes where each code is a new line
- Currently the query only pulls CPT codes from the CPT table


## Steps to execute:
1. Ensure you're successfully connected to the VA network
2. Add an input file
Update variables: 
    - `cpt_input`: input file name
    - `output_file`: output file name

## Input:
- text files containing list of CPT codes to pull from CDW
    - `cpt_input`: input file name
    - `output_file`: output file name

## Output:
- CSV file containing data from CDW mentioned in the query parameter (str)
    - CPTCode: CPT type code
    - CPTName: Formal name of the CPT code
    - CPTDescription: Additional details of the CPT code
