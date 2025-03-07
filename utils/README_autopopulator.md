# CDW AUTOPOPULATOR INSTRUCTIONS

## Script Purpose
This script can be used to generate the CDW Data Locations tab for a condition automatically.

## How to Use:
1) Ensure that the 'CFR to Code Set Mappings' tab as well as the 'Code Set Details' tab are complete. Criteria should be mapped out and codes should ideally be cleaned before this script is utilized. Also make sure that the tabs at the bottom of the sheet are spelled correctly.
2) Create a new blank sheet in the condition file and label it as 'CDW Data Locations'.
3) Click on Extensions > Apps Script. This should open up a new tab under the url script.google.com
4) Copy and paste the java code in cdw_autopopulator into the script. The buttons at the top(Run, Debug, etc.) will likely be grayed out until Ctrl + S is hit. 
5) You may be asked to log in/ authenticate through your google account
6) Next to the debug button, make sure runAllFunctions is selected. This is the wrapper that wraps the other functions together
7) Hit run. 

## Understanding Results
The CDW Data Locations tab should populate itself. Please double check that all rows have no missing data. If there is any missing data, please double check the criteria in both 'Code Set details' and the 'CFR to Code Set Mappings tab'.

## Inputs
- Any google sheet condition file with a finalized 'CFR to Code Set Mappings' tab as well as 'Code Set Details' tab.

## Outputs
- A completed CDW Data Locations tab. 

## Notes/Warnings/Tips
- If there is any DATETIME criteria, the user will need to add this in manually. For examples of  DATETIME criteria, please take a look at some of our previous conditions such as Pleuritis, Thrombo or even GI Cancer. 
- There are console log statements commented throughout the script. The user can use these to troubleshoot if there are any issues. 
- In the wrapper function, the user can comment out functions as they choose. The snomedFormatter function formats the SnomedCodes so that only the code value shows up in the Field Value Example column. Commenting this function out will keep it formatted like all the other codes
- The reOrganizingRows function() ensures that the order of code types (CPT, LOINC ICD-10 etc.) are ordered the same for each specific criteria in the CDW Data Locations tab. If you don't want these ordered, you can comment this function out, OR change the order of how the codes should up by modifying the function itself. This can be done by finding the sortOrder variable with Ctrl + F and modifying the dictionary values. 
- Use the Execution Log to identify potential bugs or areas where the script is getting stuck 

