## Import Libraries
import pandas as pd

##Variables
Condition = "gi cancer" #Update condition
ICD10List = pd.read_excel('G:/My Drive/mcp/VROv2/gems/gi-icd10.xlsx') #Update to your file location
ICD10CodeColumn = 'ICD10 Code' #Update to column name of where the ICD-10 Codes are
ICD10Name = 'Code Description' #Update to column name of where the ICD-10 names are

#Do not change these variables
GEMS = pd.read_csv('GEMs/2018_I10gem.csv', dtype=str)
ICD9desc = pd.read_excel('GEMs/ICD9_CMS32_DESC_LONG_SHORT_DX.xlsx')

## Format ICD10 file for use
ICD10List = ICD10List.rename({ICD10CodeColumn: 'ICD10'}, axis=1)
ICD10List = ICD10List.rename({ICD10Name: 'ICD10 Name'}, axis=1)
ICD10List['ICD10'] = ICD10List['ICD10'].str.replace('.','')

## Join ICD10 code list and GEMs file
AddICD9 = pd.merge(ICD10List, GEMS, on=['ICD10'], how='left')

## Add descriptions 
AddICD9 = pd.merge(AddICD9, ICD9desc, on=['ICD9'], how='left')

##Reformat ICD9 and ICD10 codes, names
AddICD9['ICD9'] = (AddICD9['ICD9'].str[:3] + '.' + AddICD9['ICD9'].str[3:])
AddICD9['ICD10'] = (AddICD9['ICD10'].str[:3] + '.' + AddICD9['ICD10'].str[3:])
ICD9codes = AddICD9
ICD9codes = ICD9codes.rename({'LONG DESCRIPTION': 'ICD9 Name'}, axis=1)

##Convert flags to readable format
def flag1(f): 
    if isinstance(f, str):
        firstflag = str(f[0])
        if firstflag == '1':
            return "Approximate"
        else:
            return "Accurate"
    else:
        return "No Match"

def flag2(f): 
    if isinstance(f, str):
        secondflag = str(f[1])
        if secondflag == '1':
            return "No Corresponding Code"
        elif secondflag == '0':
            return "Corresponding Code"
    else:
        return "No Match"

def flag3(f): 
    if isinstance(f, str):
        thirdflag = str(f[2])
        if thirdflag == '1':
            return "Requires Combination"
        elif thirdflag == '0':
            return "Does not requires Combination"
    else:
        return "No Match"

ICD9codes['Match'] = ICD9codes['Flag'].apply(flag1)
ICD9codes['Corresponding Code'] = ICD9codes['Flag'].apply(flag2)
ICD9codes['Requires Combination'] = ICD9codes['Flag'].apply(flag3)

#print(ICD9codes)

##Format dataframe 
FinalICD9 = ICD9codes.filter(['ICD10', 'ICD10 Name', 'ICD9', 'ICD9 Name', 'Match', 'Corresponding Code', 'Requires Combination'])

## Save file
filename = f'{Condition}' + '_icd9codes.xlsx'
FinalICD9.to_excel(filename)