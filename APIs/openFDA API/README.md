# openFDA Folder
Before being able to use these scripts, you must create an account with UMLS. The website can be found [here](https://uts.nlm.nih.gov/uts/profile). After your account has been approved, navigate to your [profile](https://uts.nlm.nih.gov/uts/profile) and find your APIKey. This is required for this script to run.

## openFDA API NDC Code Pull-No API Key
This Python code retrieves drug information from the openFDA API based on provided keywords, processes the data, and writes it to an Excel file.

If "No data found for keyword: KEYWORD" is returned, check to ensure that either a name_brand or generic_name of that is included in the keyword list.  If the generic_name or the name_brand are included, it is confidently covered.  Otherwise, if neither the name_brand or generic_name are found, it is recommended to add that name to the keywords list and run the script again. 

Before using this script, you must have an APIKey with openFDA.  [Go here to get an openFDA apiKey](https://open.fda.gov/apis/authentication/)

## Notes and Limitations
- openFDA has a limited call per keyword of 1000 items returned.  While this limit should not cause an issue with our calls, the possibility is factored into this code.  If you receive a "Warning: Total results for {keyword} exceed the specified limit" message after running this script, please contact me at alyssa.warnock@amida.com or over slack and I will do my best to help troubleshoot this issue. 
- If you do not change the Excel_Sheet_Name variable and attempt to run the code again with a different string_list keywords list, the code will overwrite your existing file with the new string_list variables. 

## Required Inputs
- apikey
- Excel_Sheet_Name
    - This is the title of the outputted excel sheet. 
    - Outputs each code into two columns: "NDC" and "DrugNameWithDose"
- excel_file_keywords 
    - This is the title of the inputted excel sheet with the list of keywords
- column_name 
    - This is the title of the keywords column in the excel_file_keywords 