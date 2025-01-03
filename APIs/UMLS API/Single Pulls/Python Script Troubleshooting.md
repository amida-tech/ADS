## Single Pulls File Reported Troubleshooting
The purpose of this document is to address common troubleshooting issues reported with the UMLS scripts that do not occur consistently enough to be accounted for in the script programatically, but have quick fixes that can be applied outside of the script.  

It is unclear if the VSCode solution works for Jupyter Notebook (JN) Python users.  Updates to this document will occur as more instances of errors occur.

Please report any unexpected errors to: Alyssa Warnock, Hannah Barker, and/or Jessica Peterson.

### JSONDecodeError
- Affected Scripts: SNOMED-CT and LOINC 
- Full Error Text: "JSONDecodeError: Expecting value: line 1 column 1 (char 0)"
- Reason: The JSON returned is not in the format Python is expecting
- Solution: 
    - VSCode: 
        1. Open your Condition Keyword.xlsx file.
        2. Delete the last row of empty data
            2a. For example: If you have 25 keywords, your last keyword (accounting for the column titles) will be on row 26.  Delete row 27.
        3. Run the UMLS script again. 
    - JN: 
        1. Create 3 new JN chunks (click "insert cell below" 3 times)
        2. Find "SNOMED_CT_df" (~line 99), copy the code **after** SNOMED_CT_df and place it into the first created chunk (1/3)
        3. Find "SNOMED_CT_trans_df" (~line 59 (of the new chunk)), copy the code **after** SNOMED_CT_trans_df and place it into the second created chunk (2/3)
        4. Find "SNOMED_CT_decend" (~line 54 (of the new chunk)), copy the code **after** SNOMED_CT_decend and place it into the third created chunk (3/3) 
        5. Click "Restart the kernel, then re-run the whole notebook (with dialog)"