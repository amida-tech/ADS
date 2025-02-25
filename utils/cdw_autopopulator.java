/* 
 CDW DATA LOCATIONS + FIELD VALUE EXAMPLE POPULATOR
*/

//global variable since it is used in multiple functions
var codeMap = {};

//clears the sheet to prepare the script
var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("CDW Data Locations");
if (sheet) sheet.clear();



// conditionDictionary function is responsible for creating a dictionary of conditions and codes

function conditionDictionary() {
  // create variables 
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var cdwSheet = ss.getSheetByName("CDW Data Locations");
  var codeSetSheet = ss.getSheetByName("Code Set Details");

  var cdwData = cdwSheet.getDataRange().getValues();
  var codeSetData = codeSetSheet.getDataRange().getValues();

  var cfrIndexCDW = cdwData[0].indexOf("CFR Criteria");
  var fieldExampleIndex = cdwData[0].indexOf("Field Value Example");
  var codeSetIndexCDW = cdwData[0].indexOf("Code Set"); // Code Set in CDW Data Locations

  var cfrIndexCodeSet = codeSetData[0].indexOf("CFR Criteria");
  var codeIndex = codeSetData[0].indexOf("Code");
  var descIndex = codeSetData[0].indexOf("Code Description");
  var inCDWIndex = codeSetData[0].indexOf("In CDW");
  var codeSetIndexCodeSet = codeSetData[0].indexOf("Code Set"); // Code Set in Code Set Details

  codeMap = {};


  // Create the code mapping dictionary
  for (var i = 1; i < codeSetData.length; i++) {
        if (codeSetData[i][inCDWIndex] === "Yes") {
        var key = codeSetData[i][cfrIndexCodeSet] + "||" + codeSetData[i][codeSetIndexCodeSet]; // Key: CFR Criteria + Code Set
        var value = codeSetData[i][codeIndex] + ", " + codeSetData[i][descIndex];

        if (!codeMap[key]) {
          codeMap[key] = [];
        }
        codeMap[key].push(value);
      }
  }
  //Prints the dictionary
  
  //console.log(JSON.stringify(codeMap, null, 2));

}  

/*
Example of dictionary that will be created: 
{
  "Kidney removal; Minimum rating for kidney removal||CPT": [
    "50230, Nephrectomy, including partial ureterectomy, any open approach including rib resection; radical, with regional lymphadenectomy and/or vena caval thrombectomy",
    "50234, Nephrectomy with total ureterectomy and bladder cuff; through same incision",
  ],
  "Kidney transplant; Following transplant surgery; Minimum rating following transplant surgery||SNOMED-CT": [
    "128631000119109, Chronic graft-versus-host disease following kidney transplant",
    "703048006, Post-renal transplant vesicoureteric reflux",
    "122531000119108, Lymphoproliferative disorder following kidney transplant",
  ],
  "Kidney transplant; Following transplant surgery; Minimum rating following transplant surgery||ICD-10": [
    "Z48.22, Encounter for aftercare following kidney transplant"
  ],
  "Kidney transplant; Following transplant surgery; Minimum rating following transplant surgery||ICD-9": [
    "996.81, Complications of transplanted kidney"
  ],
  "Glomerular Filtration Rate||LOINC": [
    "87430-5, Cystatin C & Glomerular filtration rate by Cystatin C-based formula panel:-:Pt:Ser/Plas:-",
    "88293-6, Glomerular filtration rate/1.73 sq M.predicted.black:ArVRat:Pt:Ser/Plas/Bld:Qn:Creatinine-based formula (CKD-EPI)",
  ]
}

*/
function columnPopulator() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sourceSheet = ss.getSheetByName("CFR to Code Set Mappings");
    const destinationSheet = ss.getSheetByName("CDW Data Locations");
    const codeSetSheet = ss.getSheetByName("Code Set Details");


    // ensure that sheet names are correct. If they aren't errors below will show up:
    if (!sourceSheet) {
        Logger.log("Error: 'CFR to Code Set Mappings' sheet not found.");
        return;
    }
    if (!destinationSheet) {
        Logger.log("Error: 'CDW Data Locations' sheet not found.");
        return;
    }
    if (!codeSetSheet) {
        Logger.log("Error: 'Code Set Details' sheet not found.");
        return;
    }


    // Copies columns A and B from "CFR Criteria to Code Set Mappings" to "CDW Data Locations"
    const sourceData = sourceSheet.getRange("A:B").getValues();
    destinationSheet.getRange(1, 1, sourceData.length, 2).setValues(sourceData);

    // Holds data from CDW Data Locations and Code Set Details
    const cdwData = destinationSheet.getDataRange().getValues();
    const codeSetData = codeSetSheet.getDataRange().getValues();

    // Setting column indexes
    const columnBIndex = 1; // Column B (Criteria) in CDW Data Locations
    const codeSetIndexCDW = 3; // Column D (Code Set) in CDW Data Locations

    const cfrIndexCodeSet = codeSetData[0].indexOf("CFR Criteria");
    const codeSetIndexCodeSet = codeSetData[0].indexOf("Code Set");
    const inCDWIndex = codeSetData[0].indexOf("In CDW");

    //Setting column names 

    destinationSheet.getRange(1, 3).setValue("Criteria Example");
    destinationSheet.getRange(1, 4).setValue("Code Set")
    destinationSheet.getRange(1, 5).setValue("CDW Table Name")
    destinationSheet.getRange(1, 6).setValue("CDW Field Name")
    destinationSheet.getRange(1, 7).setValue("Field Value Example")

    let existingEntries = new Set(); // Track (Criteria + Code Set) pairs to avoid duplicates

    for (let i = 1; i < cdwData.length; i++) {
        const criteriaValue = cdwData[i][columnBIndex];
        if (!criteriaValue) continue; // Skip empty values

        //These sets are created below to make sure that there are no duplicate criteria + code set pairings
        let exactMatches = new Set();
        let partialMatches = new Set();
        let regex = new RegExp(`(^|; )${criteriaValue}($|; )`, "i"); // Ensures whole-word matching in semicolon-separated lists

        // Look for exact and partial matches
        for (let j = 1; j < codeSetData.length; j++) {
            // hops back over to Code Set Details and checks if codes are in the CDW and sees if values from CDW data locations match anything here
            if (codeSetData[j][inCDWIndex] === "Yes") {
                let codeSetValue = codeSetData[j][cfrIndexCodeSet];

                if (codeSetValue === criteriaValue) {
                    exactMatches.add(codeSetData[j][codeSetIndexCodeSet]); // Store exact matches
                } 
                
                if (regex.test(codeSetValue)) {
                    partialMatches.add(codeSetData[j][codeSetIndexCodeSet]); // Store valid partial matches
                }
            }
        }

        // Insert unique exact matches
        for (let match of exactMatches) {
            let entryKey = criteriaValue + " | " + match;
            if (!existingEntries.has(entryKey)) {
                let newRow = cdwData[i].slice();
                newRow[codeSetIndexCDW] = match;
                destinationSheet.appendRow(newRow);
                existingEntries.add(entryKey);
            }
        }

        // Insert unique partial matches (even if exact matches exist)
        for (let match of partialMatches) {
            let entryKey = criteriaValue + " | " + match;
            if (!existingEntries.has(entryKey)) {
                let newRow = cdwData[i].slice();
                newRow[codeSetIndexCDW] = match;
                destinationSheet.appendRow(newRow);
                existingEntries.add(entryKey);
            }
        }
    }

    // Remove rows where the Code Set column is blank
    const lastRow = destinationSheet.getLastRow();
    for (let i = lastRow; i > 1; i--) { // Iterate from bottom to top
        if (!destinationSheet.getRange(i, codeSetIndexCDW + 1).getValue()) {
            destinationSheet.deleteRow(i);
        }
    }

  
    //const destinationSheet = ss.getSheetByName("CDW Data Locations");
    const data = destinationSheet.getDataRange().getValues(); // Get all sheet data
    //Conditional logic to fill in rest of the columns.. Feel Free to edit based on requirements
    for (let i = 1; i < data.length; i++) { 
        let columnDValue = data[i][3]; // Column D (index 3 since it's zero-based)
        let columnCValue = ""
        let columnEValue = ""
        let columnFValue = ""
        if (columnDValue === 'ICD-10') {

            columnCValue = "Diagnosis ICD-10 Code"
            columnEValue = "Dim.ICD10, Dim.ICD10DiagnosisVersion"
            columnFValue = "ICD10Code, ICD10Diagnosis"

        } else if (columnDValue === 'ICD-9') {
            columnCValue = "Diagnosis ICD-9 Code"
            columnEValue = "Dim.ICD9, Dim.ICD9DescriptionVersion"
            columnFValue = "ICD9Code, ICD9Diagnosis" 

        } else if (columnDValue === 'SNOMED-CT') {
            columnCValue = "Diagnosis SNOMED-CT Code"
            columnEValue = "Outpat.ProblemList"
            columnFValue = "SNOMEDConceptCode" 

        } else if (columnDValue === 'LOINC') {
            columnCValue = "Result LOINC Code"
            columnEValue = "Dim.LOINC"
            columnFValue = "LOINC, Component" 

        } else if (columnDValue === 'CPT') {
            columnCValue = "Procedure CPT Code"
            columnEValue = "Dim.CPT"
            columnFValue = "CPTCode, CPTName"

        } else if (columnDValue === 'NDC') {
            columnCValue = "NDC medication code"
            columnEValue = "Dim.NationalDrug"
            columnFValue = "DrugNameWithDose"

        } else {
            columnCValue = "No result found"
            columnEValue = "No result found"
            columnFValue = "No result found"
        }

        destinationSheet.getRange(i + 1, 3).setValue(columnCValue);
        destinationSheet.getRange(i + 1, 5).setValue(columnEValue);
        destinationSheet.getRange(i + 1, 6).setValue(columnFValue);
    }

    //Removing "Keyword" rows and "RxNorm" rows

    const columnDIndex = 3; // Column D (0-based index)
    let rowsToDelete = [];

    for (let i = data.length - 1; i >= 0; i--) {

      const cellValue = data[i][columnDIndex] ? data[i][columnDIndex].toString().toLowerCase() : "";

      if (cellValue.includes("keyword") || cellValue.includes("rxnorm")) {
        rowsToDelete.push(i + 1); // Store 1-based row index
        }
    }

    //deleting rows in reverse order
    rowsToDelete.forEach(row => destinationSheet.deleteRow(row));


    

}

// FieldValueExamplePopulator uses the dictionary created in conditionDictionary and randomly selects a value from a key 
function FieldValueExamplePopulator() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const cdwSheet = ss.getSheetByName("CDW Data Locations");

  // Fetch data from the sheet
  const cdwData = cdwSheet.getDataRange().getValues();

  // Setting indexes for columns
  const cfrIndexCDW = 1; 
  const codeSetIndexCDW = 3; 
  const fieldExampleIndex = 6; 


  // Populate the "Field Value Example" column in CDW Data Locations
  for (var j = 1; j < cdwData.length; j++) {
    var cfrValue = cdwData[j][cfrIndexCDW];
    var codeSetValue = cdwData[j][codeSetIndexCDW];
    var key = cfrValue + "||" + codeSetValue;

    var selectedValue = null;

    // 1. Checking for an exact match in criteria. Some criteria have multiple pairings i.e. (Kidney Removal & Minimum rating for Kidney Removal)
    if (codeMap[key] && codeMap[key].length > 0) {
      var randomIndex = Math.floor(Math.random() * codeMap[key].length);
      selectedValue = codeMap[key][randomIndex];
    } else {
      // 2. If no exact match, check for partial match in combined criteria
      for (var combinedKey in codeMap) {
        var [combinedCriteria, combinedCodeSet] = combinedKey.split("||");

        if (combinedCodeSet.toLowerCase().trim() === codeSetValue.toLowerCase().trim()) { // Ensure Code Set matches
            var criteriaParts = combinedCriteria.toLowerCase().trim().split("; "); // Normalize text and split multiple criteria

            // Allow partial matching (e.g., "Minimum rating for kidney removal" should match "Minimum Rating for Kidney Removal")
            if (criteriaParts.some(criterion => cfrValue.toLowerCase().trim().includes(criterion))) {
                var randomIndex = Math.floor(Math.random() * codeMap[combinedKey].length);
                selectedValue = codeMap[combinedKey][randomIndex];
                break; // Stop at the first match found
            }
        }
    }
}

    // 3. Populate the field if a value was found
    if (selectedValue) {
      cdwSheet.getRange(j + 1, fieldExampleIndex + 1).setValue(selectedValue);
    } else {
      Logger.log("No match found for: " + key);
    }
  }

}

// formats snomed codes to only have the code in "Field Value Example"
function snomedFormatter() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const cdwSheet = ss.getSheetByName("CDW Data Locations");
  const cdwData = cdwSheet.getDataRange().getValues();


  for (var j = 1; j < cdwData.length; j++) {
    var columnFValue = cdwData[j][5]?.toString().trim(); 
    var columnGValue = cdwData[j][6]?.toString(); 

    //Logger.log("Processing Row " + (j + 1) + ": F = " + columnFValue + ", G = " + columnGValue);

    if (columnFValue === "SNOMEDConceptCode" && columnGValue.includes(",")) {
        var updatedValue = columnGValue.split(",")[0].trim(); // Remove everything after the comma
        //Logger.log("Updated G for Row " + (j + 1) + ": " + updatedValue);
        cdwSheet.getRange(j + 1, 7).setValue(updatedValue); // Update Column G 
      }
  }

}

// This function re-organizes rows based on the dictionary SortOrder for consistency
function reOrganizingRows() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("CDW Data Locations");
  var data = sheet.getDataRange().getValues(); 

  if (data.length < 2) return; // Exit if no data
  
  var header = data[0]; // Save the header row
  var rows = data.slice(1); // Get all rows except the header
  

  // Feel free to set your own order for how you would like the codes to be organized per each criteria
  var sortOrder = {
    "ICD-10": 1,
    "ICD-9": 2,
    "SNOMED-CT": 3,
    "CPT": 4,
    "NDC": 5,
    "LOINC": 6
  };

  // Group rows by unique criteria in Column B
  var grouped = {};
  rows.forEach(row => {
    var criteria = row[1]; // Column B (CFR Criteria)
    if (!grouped[criteria]) {
      grouped[criteria] = [];
    }
    grouped[criteria].push(row);
  });

  // Sort each group based on the order in Column D (Code Set)
  var sortedRows = [];
  for (var criteria in grouped) {
    grouped[criteria].sort((a, b) => {
      var codeA = sortOrder[a[3]] || 999; // Column D (Code Set)
      var codeB = sortOrder[b[3]] || 999;
      return codeA - codeB;
    });
    sortedRows = sortedRows.concat(grouped[criteria]);
  }

  // Overwrite the sheet with the sorted data
  sheet.clearContents();
  sheet.appendRow(header);
  sortedRows.forEach(row => sheet.appendRow(row));
}






function runAllFunctions() {
  conditionDictionary(); // Populate codeMap first
  columnPopulator();     // populates columns with information from Code Set Details
  FieldValueExamplePopulator(); //populate field value example
  //Comment the function below out if you would like to see the Snomed code + description 
  snomedFormatter(); //formats snomed codes and just leaves the code instead of the description 
  reOrganizingRows();
}
