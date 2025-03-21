# openFDA API Folder
## Script Purpose
These scripts query the openFDA API using a list of keywords and returns NDC codes related to the ingested keywords. 

## How to Use:
1) [Go here to get an openFDA apiKey](https://open.fda.gov/apis/authentication/).
- Note: The API_KEY confirmation email is commonly blocked by Amida's email firewall.  If you don't receive your API_KEY within a couple minutes of requesting it, either reach out to IT or request an API_KEY with your personal email. 
2) Put your Condition's keyword CSV file in the `inputs` folder.  This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.
3) Update the API_KEY, CONDITION, and CSV_FILE_INPUT_NAME variables at the top of the script with the requested information. 
4) Run the script.  A new file will be generated in the `output` folder with title of the file built on the CONDITION variable + _NDC_codes.

## Understanding Results
- A new Excel file will be created titled based on the CONDITION variable and the medical code script you are running.
- The outputted file will have a list of your chosen medication keywords, their code description, the keyword prompting that result.  The outputted file will also have the corresponding VASRD Code, CFR criteria, and Data Concept related to the returned NDC code.   

## Inputs
- Your Condition's keyword CSV file in the `inputs` folder.  This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.

## Outputs
- Excel file containing the following columns: 'VASRD Code', 'CFR Criteria', 'Code', 'Code Description', 'Keyword', and 'Data Concept'

## Warnings/Discrepancies 
- openFDA has a limited call per keyword of 1000 items returned.  While this limit should not cause an issue with our calls, the possibility is factored into this code.  If you receive a "Warning: Total results for {keyword} exceed the specified limit" message after running this script, please contact me at alyssa.warnock@amida.com or over slack and I will do my best to help troubleshoot this issue. 
- The API_KEY confirmation email is commonly blocked by Amida's email firewall.  If you don't receive your API_KEY within a couple minutes of requesting it, either reach out to IT or request an API_KEY with your personal email. 
- If you do not change the Excel_Sheet_Name variable and attempt to run the code again with a different string_list keywords list, the code will overwrite your existing file with the new string_list variables. 