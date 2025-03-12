// This script ensures consistency within the Code Set Details and CFR to Code Set Mappings sheets. Please see the readme for more information on how to use this script.


function validateAndStoreCriteria() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var criteriaSheet = ss.getSheetByName("CFR to Code Set Mappings");
    var codeSetSheet = ss.getSheetByName("Code Set Details");
  
    var cfrCriteriaData = criteriaSheet.getDataRange().getValues();
    var codeSetData = codeSetSheet.getDataRange().getValues();
  
    // Identify column indices
    var criteriaIndex = cfrCriteriaData[0].indexOf("CFR Criteria");
    var codeSetCriteriaIndex = codeSetData[0].indexOf("CFR Criteria");
    var cfrVASRDIndex = cfrCriteriaData[0].indexOf("VASRD Code");
    var codeSetVASRDIndex = codeSetData[0].indexOf("VASRD Code");
  
    if (criteriaIndex === -1 || codeSetCriteriaIndex === -1 || cfrVASRDIndex === -1 || codeSetVASRDIndex === -1) {
      Logger.log("❌ Error: One or more required columns not found. Check 'CFR Criteria' and 'VASRD Code' in both sheets.");
      return;
    }
  
    //  Store unique CFR criteria from "CFR to Code Set Mappings"
    var uniqueCFRSet = new Set();
    for (var i = 1; i < cfrCriteriaData.length; i++) {
      let cfrValue = cfrCriteriaData[i][criteriaIndex];
      if (cfrValue) {
        cfrValue.split(";")
        .map(c => c.trim().toLowerCase()) 
        .forEach(c => uniqueCFRSet.add(c));
    }
  }
  
    //  Store unique criteria from "Code Set Details"
    var uniqueCodeSet = new Set();
    for (var i = 1; i < codeSetData.length; i++) {
      let codeSetValue = codeSetData[i][codeSetCriteriaIndex];
      if (codeSetValue) {
      codeSetValue.split(";")
        .map(c => c.trim().toLowerCase()) 
        .forEach(c => uniqueCodeSet.add(c));
    }
  }
  
  
  
  
    //  Check if each CFR criterion exists in Code Set Details
    var missingCriteria = [];
    uniqueCFRSet.forEach(criterion => {
      if (!uniqueCodeSet.has(criterion)) {
        missingCriteria.push(criterion);
      }
    });
  
    if (missingCriteria.length > 0) {
      Logger.log(` Some criteria from CFR to Code Set Mappings are missing in Code Set Details. 
      Missing Criteria: 
      ${JSON.stringify(missingCriteria, null, 2)}`);
    } else {
      Logger.log(" All Criteria from CFR to Code Set Mappings exists in Code Set Details!");
    }
  
  
    var moreMissingCriteria = [];
    uniqueCodeSet.forEach(criterion => {
      if (!uniqueCFRSet.has(criterion)) {
        moreMissingCriteria.push(criterion);
      }
    });
  
  
    if (moreMissingCriteria.length > 0) {
      Logger.log(` Some criteria from Code Set Details are missing from CFR to Code Set Mappings. 
      Missing Criteria: 
      ${JSON.stringify(moreMissingCriteria, null, 2)}`);
    } else {
      Logger.log(" All Criteria from Code Set Details exists in CFR to Code Set Mappings!");
    }
  
    
  }
  
  
  
  // format Varsd Code - formats VARSD codes in both sheets
  function formatVASRDCodes() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var codeSetSheet = ss.getSheetByName("Code Set Details");
    var data = codeSetSheet.getDataRange().getValues();
    // Identify column index for "VASRD Code"
    var headerRow = data[0];  
    var codeSetVASRDIndex = headerRow.indexOf("VASRD Code"); // Ensure it's a 1D array
  
    var updatedData = [];
    updatedData.push(headerRow); // Keep header row unchanged
  
    // Loop through rows, starting from the second row (index 1)
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
  
      if (row[codeSetVASRDIndex]) {
        var codes = row[codeSetVASRDIndex].toString()
          .replace(/[,/;:]/g, ";") // Replace commas and slashes with semicolon
          .split(";") // Split into an array
          .map(code => code.trim()) // Trim spaces
          .map(code => parseInt(code, 10)) // Convert to number for sorting
          .sort((a, b) => a - b) // Sort numerically
          .map(code => code.toString()) // Convert back to string
          .join("; "); // Join back with semicolon
  
        row[codeSetVASRDIndex] = codes; // Update row with modified values
      }
  
      updatedData.push(row); // Store updated row
    }
  
    // Overwrite the entire range with sorted values
    codeSetSheet.getRange(1, 1, updatedData.length, updatedData[0].length).setValues(updatedData);
  
    var CFRSheet = ss.getSheetByName("CFR to Code Set Mappings");
    var data_2 = CFRSheet.getDataRange().getValues();
    var headerRow_2 = data_2[0];  
    var CFRVASRDIndex = headerRow_2.indexOf("VASRD Code"); // Ensure it's a 1D array
  
    var updatedData_2 = [];
    updatedData_2.push(headerRow_2);
  
    // Loop through rows, starting from the second row (index 1)
    for (var i = 1; i < data_2.length; i++) {
      var row_2 = data_2[i];
  
    if (row_2[CFRVASRDIndex]) {
        var codes_2 = row_2[CFRVASRDIndex].toString()
          .replace(/[,/;:]/g, ";") // Replace commas slashes, colon with semicolon
          .split(";") // Split into an array
          .map(codes => codes.trim()) // Trim spaces
          .map(codes => parseInt(codes, 10)) // Convert to number for sorting
          .sort((a, b) => a - b) // Sort numerically
          .map(codes => codes.toString()) // Convert back to string
          .join("; "); // Join back with semicolon
  
        row_2[CFRVASRDIndex] = codes_2; // Update row with modified values
      }
  
      updatedData_2.push(row_2); // Store updated row
    }
  
    // Overwrite the entire range with sorted values
    CFRSheet.getRange(1, 1, updatedData_2.length, updatedData_2[0].length).setValues(updatedData_2);
  
  }
  
  
  
  function criteriaFormatter() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var codeSetSheet = ss.getSheetByName("Code Set Details");
    var mappingSheet = ss.getSheetByName("CFR to Code Set mappings");
  
    if (!codeSetSheet || !mappingSheet) {
      Logger.log("Sheets not found!");
      return;
    }
  
    var data = codeSetSheet.getDataRange().getValues(); // Read all data
    var updatedData = [...data]; // Clone to avoid modifying original data structure
  
    // ⚠️ Modify this list/variable below to exclude specific criteria from formatting. separate multiple criteria with commas. ⚠️
    var excludedCriteria = ["PLACEHOLDER FOR CRITERIA"].map(value => value.toLowerCase());
    var excludedSet = new Set(excludedCriteria);
  
    // Step 1: Format capitalization in Column B (excluding specified criteria)
    for (var i = 1; i < data.length; i++) { // Skip header row
      var originalValue = data[i][1] ? data[i][1].toString().trim() : ""; // Ensure valid string
      var splitValues = originalValue.split(/[/;:]/).map(code => code.trim()); // Split & trim
  
      // Capitalize criteria unless they are in the excluded set
      var formattedValues = splitValues.map(code =>
        excludedSet.has(code.toLowerCase()) ? code : code.charAt(0).toUpperCase() + code.slice(1).toLowerCase()
      );
  
      updatedData[i][1] = formattedValues.join("; "); // Update only column B
    }
  
     // Step 2: Build a mapping of criteria to corresponding codes
    var mappingData = mappingSheet.getRange("A2:B" + mappingSheet.getLastRow()).getValues();
    var criteriaToCode = {};
    
    mappingData.forEach(row => {
      let code = row[0];
      let criteria = row[1];
  
      if (criteria && typeof code === "string" && code.includes(";")) {
        return; // Skip multiple codes
      }
  
      if (!isNaN(code) && criteria) {
        criteriaToCode[criteria.trim()] = parseInt(code, 10);
      }
    });
  
    for (var i = 1; i < updatedData.length; i++) {
      if (!updatedData[i][1]) {
        continue; // Skip empty criteria
      }
  
      let criteriaList = updatedData[i][1].split(";").map(c => c.trim()); // Split criteria
      
      // Map criteria to codes, filter valid ones, and sort numerically
      let sortedItems = criteriaList
        .map(criteria => ({
          criteria,
          code: criteriaToCode[criteria] || Number.MAX_VALUE // Assign MAX_VALUE if no code found
        }))
        .filter(item => item.code !== Number.MAX_VALUE) // Remove criteria without valid codes
        .sort((a, b) => a.code - b.code); // Sort by code
  
      let sortedCriteria = sortedItems.map(item => item.criteria);
      let sortedCodes = sortedItems.map(item => item.code);
  
      if (sortedCriteria.length === criteriaList.length && sortedCriteria.join("; ") !== updatedData[i][1]) {
        updatedData[i][1] = sortedCriteria.join("; "); // Update sorted criteria in Column B
        updatedData[i][0] = sortedCodes.join("; "); // Store sorted VARSD codes in Column A
      }
    }
  
    codeSetSheet.getRange(1, 1, updatedData.length, updatedData[0].length).setValues(updatedData);
  
   
  }
  
  
  
  
  
  function GeneralSorter(){
  
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Code Set Details");
  
    var lastRow = sheet.getLastRow();
    var lastColumn = sheet.getLastColumn();
    
    if (lastRow <= 1) return; // Check if there's no data
  
    // Get entire data range (excluding header row)
    var range = sheet.getRange(2, 1, lastRow - 1, lastColumn);
    var values = range.getValues(); // Get all data
  
    // Sort first by Column C (index 2), then by Column D (index 3)
    values.sort((a, b) => {
      var colC_a = isNaN(a[2]) ? a[2].toString() : Number(a[2]); 
      var colC_b = isNaN(b[2]) ? b[2].toString() : Number(b[2]);
      
      var colCComparison = colC_a < colC_b ? -1 : colC_a > colC_b ? 1 : 0;
  
      if (colCComparison === 0) {
        var colD_a = isNaN(a[3]) ? a[3].toString() : Number(a[3]);
        var colD_b = isNaN(b[3]) ? b[3].toString() : Number(b[3]);
  
        return colD_a < colD_b ? -1 : colD_a > colD_b ? 1 : 0;
      }
    
      return colCComparison;
    });
  
  
    // Write sorted data back to the sheet (keeping all columns aligned)
    range.setValues(values);
  
  }
  
  
  
  function relevantCodeSetColumn() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
  
    // Part 1 - Creating dictionary from "Code Set Details" sheet
    var codeSetSheet = ss.getSheetByName("Code Set Details"); // Adjust if needed
    if (!codeSetSheet) {
      Logger.log("Code Set Details sheet not found!");
      return;
    }
  
    var lastRow = codeSetSheet.getLastRow();
    if (lastRow <= 1) return; // Check if there's no data
  
    var data = codeSetSheet.getRange(2, 2, lastRow - 1, 2).getValues(); // Get Columns B & C
    var dictionary = {}; // Object to store key-value pairs (case-insensitive)
  
    data.forEach(row => {
      var keys = row[0].split(";").map(key => key.trim().toLowerCase()); // Convert keys to lowercase
      var value = row[1].toString().trim(); // Keep the value unchanged (not lowercase)
      
      keys.forEach(key => {
        if (!dictionary[key]) {
          dictionary[key] = []; // Initialize as an array
        }
        if (!dictionary[key].includes(value)) { // Avoid duplicate values for the same key
          dictionary[key].push(value);
        }
      });
    });
  
    // Removing instances of "Keyword" in dictionary since we don't want those in the relevant code set column
    Object.keys(dictionary).forEach(key => {
      dictionary[key] = dictionary[key].filter(value => value.toLowerCase() !== "keyword");
    });
  
    //debugging
    //Logger.log(JSON.stringify(dictionary, null, 2));
  
    // Part 2 - Populating Relevant Code Sets in "CFR to Code Set Mappings" sheet
    var cfrSheet = ss.getSheetByName("CFR to Code Set Mappings");
    if (!cfrSheet) {
      Logger.log("CFR To Code Set Mappings sheet not found!");
      return;
    }
  
    var lastRowCFR = cfrSheet.getLastRow();
    if (lastRowCFR <= 1) return; // Check if there's no data
  
    // Get CFR Criteria (Column B) and Relevant Code Sets (Column E)
    var cfrCriteriaRange = cfrSheet.getRange(2, 2, lastRowCFR - 1, 1); // Column B (CFR Criteria)
    var codeSetRange = cfrSheet.getRange(2, 5, lastRowCFR - 1, 1); // Column E (Relevant Code Sets)
    var columnFRange = cfrSheet.getRange(2, 6, lastRowCFR - 1, 1); // Column F 
  
  
    var cfrCriteriaValues = cfrCriteriaRange.getValues(); // Column B values
    var codeSetValues = []; // Array to store updated Column E values
    var columnFValues = []; // Array to store messages for Column F
  
  
    // Loop through CFR Criteria and match with dictionary keys 
    for (var i = 0; i < cfrCriteriaValues.length; i++) {
      var criteriaOriginal = cfrCriteriaValues[i][0].trim(); 
      var criteriaLower = criteriaOriginal.toLowerCase(); // Convert to lowercase for comparison
  
      if (dictionary[criteriaLower] && dictionary[criteriaLower].length > 0) {
        codeSetValues.push([dictionary[criteriaLower].join(", ")]); // Join array into comma-separated string
        columnFValues.push([""]); // Leave Column F empty if there is a match
      } else {
        codeSetValues.push(["N/A"]);
        columnFValues.push(["There are no applicable medical codes for this CFR criteria"]); // Add message in Column F
      }
    }
  
    // Write updated values back to Column E & Column F
    codeSetRange.setValues(codeSetValues);
    columnFRange.setValues(columnFValues);
  
    Logger.log("Relevant code set column populated.");
  }
  
  
  
  function scientific_notation_detector() {
      var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Code Set Details");
      if (!sheet) return;
      
      var range = sheet.getRange("D2:D" + sheet.getLastRow());
      var displayValues = range.getDisplayValues(); // Get displayed values
      var backgrounds = range.getBackgrounds(); // Get existing background colors
  
      for (var i = 0; i < displayValues.length; i++) {
          var cellValue = displayValues[i][0]; 
          
  
          if (cellValue.includes("+")) { 
              backgrounds[i][0] = "#FF0000"; // Highlight in red if "+" detected
              Logger.log("Detected scientific notation: " + cellValue);
          } else {
              backgrounds[i][0] = "#FFFFFF"; 
          }
      }
  
      range.setBackgrounds(backgrounds); 
  }
  
  

  
  function runAll() {
  
    validateAndStoreCriteria(); // checks if all criteria exist in Code Set Details from CFR to Code Set Mappings and the other way around 
    formatVASRDCodes(); // formats all VARSD Codes in both sheets
    criteriaFormatter(); // formats criteria in alphabetical order, trims whitespace, splits on semicolon etc.
    GeneralSorter(); // sorts all codes based on Code Set column first, and then code column
    relevantCodeSetColumn(); // populates relevant code set column in CFR to Code Set Mappings sheet
    scientific_notation_detector(); // highlights codes that are in scientific notation to red
  
  
  }
  
  
  
  
  
  
  
  
  
  
  
  
  