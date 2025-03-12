# CONSISTENCY SCRIPT INSTRUCTIONS

## Script Purpose
The script automates a few tasks and ensures consistency after the code set compilation of a condition is complete. 
1) It will double check that all criteria from the CFR to Code Set Mappings sheet is in the Code Set Details sheet.
2) It will double check that all criteria from the Code Set Details sheet is in the CFR to Code Set Mappings sheet.
3) It will format VARSD codes in both sheets, trim any whitespace, ensure numerical order, proper splitting etc. 
4) It will format criteria in Code Set Details by trimming whitespace, ensure capitalization, proper splitting etc.
5) It will make sure that that rows multiple VARSD Codes match up respectively with multiple criteria in Code Set Details.
6) It will group sort all codes by Code Set(ICD-10, CPT, NDC etc.) and then sort numerically/lexicographically based on the Code
7) It will populate the relevant code sets column (Column E) with the Code Set for each criteria, and label column F are "There are no applicable medical codes for this CFR criteria" if necessary. 
8) It will detect any codes in scientific notation, note them in the execution log, and highlight them *red*.



## NOTES - BEFORE USING
1) Ensure that you have two sheets named 'CFR to Code Set Mappings' and 'Code Set Details'
2) Ensure that you have two columns named 'VARSD Code' and 'CFR Criteria' (column A and B respectively) in both sheets. 
3) Please only use parentheses/commas/dashes and not semicolons/colons/slashes to *describe* criteria. Criteria will not be split correctly otherwise.

        Systemic Therapy: Corticosteroids  - ❌
	    Systemic Therapy/ Corticosteroids  - ❌ 
	    Systemic Therapy; Corticosteroids  - ❌
	    Systemic Therapy(Corticosteroids)  - ✅ 
        Systemic Therapy (Corticosteroids) - ✅
	    Systemic Therapy, Corticosteroids  - ✅
	    Systemic Therapy- Corticosteroids  - ✅

3) When *splitting* criteria do not use parentheses/commas/dashes. Ideally you would want to use semicolons, but if you accidentally put a colon, the script will change it to a semicolon. 

        Fibromyalgia (fibrositis, primary fibromyalgia syndrome); Tender points  - ✅
        Glomerulonephritis; Renal disease caused by viral infection: Nephritis   - ✅
        Surgical therapy, Chronic myelogenous leukemia, In apparent remission    - ❌
        Chemotherapy - Myelosuppressive therapy - Immunosuppressive therapy      - ❌    

4) The script will also sort based on the Code Set column first, then the Code column
5) There script capitalizes every first word in each criteria and makes all other letters lowercase. In the case that you want some criteria to be preserved, please find and modify the 'excludedCriteria' variable in the script. Use commas for multiple criteria. Leave the variable as is if there are no specifications. 

### 🔧 User-Configurable Variable

```javascript
// Modify this variable as needed
 var excludedCriteria = ["AL amyloidosis"].map(value => value.toLowerCase());
// OR 
 var excludedCriteria = ["AL amyloidosis", "Renal involvement in diabetes mellitus type I or II "].map(value => value.toLowerCase());
```


## How to Use:
1) Criteria should be mapped out and codes should be relatively clean before this script is utilized. Also make sure that the tabs at the bottom of the sheet are spelled correctly.
3) Click on Extensions > Apps Script. This should open up a new tab under the url script.google.com.
4) Copy and paste the java code from the consistency_script into the ide. The buttons at the top(Run, Debug, etc.) will likely be grayed out until Ctrl + S is hit. 
5) You may be asked to log in/ authenticate through your google account
6) Next to the debug button, make sure runAll is selected. This is the wrapper that wraps the other functions together
7) Hit run. 

## Understanding Results
The Code Set Details and CFR to Code Set Mappings tab should be cleaned. Please keep an eye on the execution/console log, as there are debugging/informative statements scattered throughout the code that could provide important information. If you have missing criteria in one of the sheets, you will get a notification in the execution/console log, but the script will still run.

## Inputs
- Any google sheet condition file with sheets named 'CFR to Code Set Mappings' and 'Code Set Details', ideally complete or next to complete.

## Outputs
✅ A cleaned and sorted VARSD code column in both Code Set Details and 'CFR to Code Set Mappings'
✅ A cleaned and sorted criteria column in 'Code Set Details'
✅ A populated relevant code set column
✅ Sorted ICD-10, ICD-9, LOINC, RxNorm, CPT, and NDC codes
✅ Multiple criteria matching with VARSD codes in 'Code Set Details'
✅ Highlighted scientific notation codes


## Other Notes/Warnings/Tips
- In the case that the script messes up progress that you have made on the code set, please just go back and restore the latest version of your codes from the version history feature in google sheets. Feel free to run the script as many times as you want.
- Use console log statements throughout the script to troubleshoot if there are any issues. 
- In the wrapper function, the user can comment out functions as they choose.(Comment out the GeneralSorter function if you don't want your codes sorted or comment out scientific_notation_detector if you don't want this functionality etc.)
- Use the Execution Log to identify potential bugs or areas where the script is getting stuck.
- Common errors will be not having tabs spelled correctly and not having columns spelled correctly.
- One specific edge case: There are a *few* codes that fall under a *few* CFR criteria that fall under a small handful of VARSD Codes. A hypothetical example would be something like: 

CFR To Code Set Mappings:
| VARSD CODE         | CRITERIA                      |
|--------------------|-----------------------------|
| 5054; 5250        | Crutches                     |
| 5055; 5250; 5251; 5253 | Limited range of motion |



Code Set Details

| VARSD CODE                     | CRITERIA                           | CODE SET | CODE     | DESCRIPTION                                |
|--------------------------------|------------------------------------|----------|----------|-------------------------------------------|
| 5054; 5055; 5250; 5251; 5253   | Limited range of motion; Crutches  | ICD-10   | I70.231  | Crutches with limited range of motion    |


- In this case the script will not swap Crutches and limited range of motion to become: Crutches; Limited range of motion