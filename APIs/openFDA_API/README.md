# openFDA API Folder
## Script Purpose
This script queries the openFDA API using a list of keywords and returns NDC codes related to the ingested keywords. 

## How to Use:
1) [Go here to get an openFDA apiKey](https://open.fda.gov/apis/authentication/).
- Note: The API_KEY confirmation email is commonly blocked by Amida's email firewall.  If you don't receive your API_KEY within a couple minutes of requesting it, either reach out to IT or check your spam folder. 
2) Navigate inside of the `openFDA_API` folder & download `query_openfda.py` file
3) Navigate to your condition's keyword file in Google Sheets and downlod the file as a CSV file. This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.
4) Put your Condition's keyword CSV file in the `inputs` folder.
5) Update the API_KEY, CONDITION, and CSV_FILE_INPUT_NAME variables at the top of the script with the requested information. 
6) Run the script.  A new file will be generated in the `output` folder with title of the file built on the CONDITION variable + _NDC_codes.

## Understanding Results
- A new Excel file will be created titled based on the CONDITION variable + _NDC_codes suffix.The outputted file will have the following columns: 
- "VASRD Code": The Veterans Affairs Schedule for Rating Disabilities (VASRD) code extracted from the federal eCFR (Electronic Code of Federal Regulations). It represents the diagnostic code used for evaluating disability claims.
- "CFR Criteria": The regulatory criteria sourced from the keywords mapping file. This column contains the specific CFR (Code of Federal Regulations) language or conditions related to the medication keyword.
- "Code Set": The reference or classification system associated with the medication keyword, obtained from the keywords mapping file (ex: NDC)
- "Code": The National Drug Code (NDC) or equivalent identifier returned by the openFDA API. This unique code identifies the drug product, including the labeler, product, but excludes the package segments for VA formatting standards (see "Warnings/Discrepancies" for more information).
- "Code Description": A detailed description of the drug product associated with the NDC code, retrieved from the openFDA API. This typically includes the generic name, brand name, and strength.
- "Keyword": The medication keyword from the keywords mapping file, used as the search term for querying the openFDA API. It may represent a generic or brand name.
- "Data Concept": The classification label from the keywords mapping file, indicating the category of the keyword (e.g., Medication).
- "MarketingCategory": The regulatory classification of the drug, obtained from the openFDA API. It specifies whether the product is prescription, over-the-counter, or other marketing categories.

## Inputs
- Your Condition's keyword CSV file in the `inputs` folder.  This file should follow the [Keyword Template](https://docs.google.com/spreadsheets/d/1_RapZeT2gHfZQERkFxnjQZEbvCiMd5hNdy9sqATFvNw/edit?gid=0#gid=0) structure.

## Outputs
- Excel file containing the following columns: "Code", "Code Description", "VASRD Code", "Data Concept", "CFR Criteria", "Code Set", "Keyword", and "MarketingCategory".

## Warnings/Discrepancies 
- The NDC codes returned by this script will be formatting like the following: "AAAAA-BBBB" instead of the typical complete "AAAAA-BBBB-CC" form to meet VA consistency standards. 
- openFDA has a limited call per keyword of 1000 items returned.  While this limit should not cause an issue with our calls, the possibility is factored into this code.  If you receive a "Warning: Total results for {keyword} exceed the specified limit" message after running this script, please contact me at alyssa.warnock@amida.com or over slack and I will do my best to help troubleshoot this issue. 
- The API_KEY confirmation email is commonly blocked by Amida's email firewall.  If you don't receive your API_KEY within a couple minutes of requesting it, either reach out to IT or check your spam folder. 