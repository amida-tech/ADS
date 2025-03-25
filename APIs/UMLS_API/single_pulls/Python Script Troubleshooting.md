# Single Pulls File Reported Troubleshooting
The purpose of this document is to address common troubleshooting issues reported with the UMLS scripts that do not occur consistently enough to be accounted for in the script programatically, but have quick fixes that can be applied outside of the script.  

It is unclear if the VSCode solution works for Jupyter Notebook (JN) Python users.  Updates to this document will occur as more instances of errors occur.

Please report any unexpected errors to: Alyssa Warnock, Hannah Barker, and/or Jessica Peterson.

## UMLS Python Script Troubleshooting and Error Documentation
There are two types of errors that can be outputted from these scripts.  There are "Python Script Error" responses and "Server Error Response Code(s)".  The "Python Script Error" responses will most likely output a keyword, CUI code, or URL that you can use to find the information you are looking for.  "Server Error Response Codes" are feedback codes from UMLS and can't always be addressed within Python.

### Python Script Error Responses
#### "Error processing keyword: {string}: {e}"
- Problem: This problem occurs in the chunk where Python queries UMLS for CUI codes associated with certain keywords. If an error arises while querying a particular keyword, the keyword and specific error will be outputted in the terminal.
- Solution: The solution is dependent upon the error received.  If the specific error has not been reported yet, please let Alyssa Warnock (alyssa.warnock@amida.com) know to update the documentation.

#### "Error occured while processing {IDENTIFIER}: {except_error}"
- Problem: This problem occurs int he chunk where Python queries decendant codes.  This is not in all python scripts. If an error arises while querying a particular code, the code and specific error will be outputted in the terminal. 
- Solution: The solution is dependent upon the error received.  If the specific error has not been reported yet, please let Alyssa Warnock (alyssa.warnock@amida.com) know to update the documentation.

#### "JSONDecodeError encountered for CUI: {cui}. Skipping this entry."
- Problem: This error commonly occurs when UMLS can't keep up with Python's requests.  Sometimes the code that throws the error may still be in the final output.  This is because all this error says is that Python is receiving something that it didn't expect at the time it processed it, but UMLS is fast and may have returned the information right after Python threw the error.  The only way to confirm this is to see if the SNOMED-CT code (or other related medical code) is in the outputted code set. Follow the solution steps below to find the applicable code.  
- Solution: 
1. Navigate to the [UMLS Web Browser](https://uts.nlm.nih.gov/uts/umls/home)
2. Input the outputted CUI code into the UMLS's search engine and click Enter on your keyboard (ex: [C0554107](https://uts.nlm.nih.gov/uts/umls/searchResults?searchString=C0554107&returnType=code&tree=SNOMEDCT_US))
3. Filter "Vocabularies" on the left-hand side of the screen to filter for the applicable code (ex: "SNOMED-CT")
4. Click on the final result (there should only be 1) (ex: [Appendicular pain (275406005)](https://uts.nlm.nih.gov/uts/umls/vocabulary/SNOMEDCT_US/275406005))
5. The value in the parentheses (ex: "275406005") next to the code description (ex: "Appendicular pain") is the corresponding code for your JSONDecodeError value.
6. Make sure that this SNOMED-CT code is in your final output.  Sometimes it'll still be processed in the final output.  If the code is not in your final output, add it to your final outputted excel sheet. 
7. NOTE: If you get multiple JSONDecodeErrors (>15), I'd recommend re-running the script.

#### "Error: Timeout occurred while processing: {IDENTIFIER}. Skipping this entry"
- Problem: This error occurs when an HTTP request to retrieve data for the given medical code takes longer than the specified timeout limit, causing the request to fail and be skipped.
- Solution: 
1. Check that your internet connection is stable
2. Re-run the script 
3. If that doesn't work, try increasing the timeout limit to 20 seconds instead of 10 seconds (Ctrl+F "timeout=10")

### Server Error Response Codes
Reference [this website](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) for a list of Server Error Response Code.  Some examples of these codes are: 502, 404, etc.

### Multiple JSONDecodeError Responses
If your script returns a large number of JSONDecodeError messages for codes, it may be more time effective to re-run the script. Before re-running the script, follow the troubleshooting steps below to decrease the chance of recieving the error again.
- Full Error Text: "JSONDecodeError: Expecting value: line 1 column 1 (char 0)"
- Reason: The JSON returned is not in the format Python is expecting
- Solution: 
    1. Open your Condition Keyword.xlsx file.
     2. Delete the last row of empty data
        2a. For example: If you have 25 keywords, your last keyword (accounting for the column titles) will be on row 26.  Delete row 27.
    3. Run the UMLS script again. 

### ICD-10 Only Script Troubleshooting
#### "Error: Received status code {response.status_code} for keyword: {value}"
- Problem: This error occurs when the Clinical Tables supplemental API call for ICD-10 codes runs into a specific error. This is a general catch-all for errors. 
- Solution: The solution is dependent upon the error received.  If the specific error has not been reported yet, please let Alyssa Warnock (alyssa.warnock@amida.com) know to update the documentation.

### SNOMED-CT Only Script Troubleshooting
#### "Error processing Semantic Type for CUI {cui}: {e}"
- Problem: This error occurs when the script is unable to pull the Semantic Type for a certain CUI code from UMLS.
- Solution: 
1. Navigate to the [UMLS Web Browser](https://uts.nlm.nih.gov/uts/umls/home)
2. Input the outputted CUI code into the UMLS's search engine and click Enter on your keyboard (ex: [C0554107](https://uts.nlm.nih.gov/uts/umls/searchResults?searchString=C0554107&returnType=code&tree=SNOMEDCT_US))
3. Select the "Concepts" tab directly below the search bar (ex: [C0554107](https://uts.nlm.nih.gov/uts/umls/searchResults?searchString=C0554107&returnType=concept&tree=SNOMEDCT_US))
4. The "Semantic Type" will be located right under the code's description (ex: [Appendicular pain (C0554107)
Semantic Types: Sign or Symptom](https://uts.nlm.nih.gov/uts/umls/searchResults?searchString=C0554107&returnType=concept&tree=SNOMEDCT_US&vocabulary=SNOMEDCT_US))
5. NOTE: If you have multiple results, filter from SNOMED-CT under the "Vocabularies" column in the left-hand side of the screen (You shouldn't have to do this, because there should only be 1 code associated with your CUI code)

#### "JSONDecodeError for Semantic Group (URI: {sem_uri}). Skipping this entry."
- Problem: This error commonly occurs when UMLS can't keep up with Python's requests.  Sometimes the code that throws the error may still be in the final output.  This is because all this error says is that Python is receiving something that it didn't expect at the time it processed it, but UMLS is fast and may have returned the information right after Python threw the error.  The only way to confirm this is to see if hte SNOMED-CT code is in the outputted code set. Follow the solution steps below to find the SNOMED-CT code.
- Solution: 
1. Click on the returned URI (ex: [URI Example](https://uts-ws.nlm.nih.gov/rest/semantic-network/2024AB/TUI/T184))
2. If clicking on the returned URI does not work, copy it into your browser of choice
3. JSON should load on the browser. 
4. Click "pretty print" in the top left-hand corner of your browser. 
5. Scroll to the bottom of the JSON or use "CTRL + F" to find the "semanticTypeGroup" > "expandedForm".  The value assigned to "expandedForm" is the Semantic Group for the CUI you are looking for. 
6. NOTE: The Semantic Group should be one of the following eight categories:
- Anatomy
- Chemicals & Drugs
- Devices
- Disorders
- Genes & Molecular Sequences
- Living Beings
- Physiology
- Procedures
If you find a variable that is NOT one of these eight, you are most likely looking at the Semantic Type value instead and should keep looking for one of those eight categories. 

#### "Error processing Semantic Group URI for {sem_uri}: {e}"
- Problem: This error could occur for many reasons.  It's recommend that you check [this website](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) for more details on the specific server error that was output.
- Solution: Follow the steps for "JSONDecodeError for Semantic Group (URI: {sem_uri}). Skipping this entry." troubleshooting to pull the Semantic Group information for this CUI code
