#!/usr/bin/env python
# coding: utf-8


## CHANGE INPUTS HERE ##
apikey = 'YOUR API KEY HERE'
string_list = ["Prednisone Intensol", "Adrenalin", "Ventolin HFA", "Xopenex", "Accolate", "Advair Diskus", "Advair", "Aerospan HFA",
               "Alvesco", "Asmanex Twisthaler", "Breo Ellipta", "Cinqair", "Dulera", "Dupixent", "Fasenra", "Flovent HFA", 
               "Flovent", "Nucala", "Pulmicort Flexhaler", "QVAR RediHaler", "Serevent Diskus", "Serevent", "Singulair", "Spiriva Respimat", 
               "Symbicort", "Trelegy Ellipta", "Xolair", "Zyflo", "Rayos", "Auvi-Q", "Proventil HFA", "Proventil", "Xopenex HFA", "Xopenex", "Advair HFA", 
               "Asmanex HFA", "Asmanex", "Flovent Diskus", "Pulmicort Respules", "Zyflo CR", "Medrol", "Epipen 2-Pak", "Epipen", "Proair HFA", "Proair",
               "Xopenex Concentrate", "Millipred", "EpiPen Jr 2-Pak", "ProAir RespiClick", "Orapred", "Symjepi", "ODT", 
               "AirDuo RespiClick", "AirDuo", "Pediapred", "Wixela Inhub", "ArmonAi RespiClick", "ArmonAi", "Arnuit Ellipta", "Prednisone", "Epinephrine", "Albuterol", "Levalbuterol", "Zafirlukast", "Fluticasone", "Flunisolide", "Ciclesonide", 
               "Reslizumab", "Mometasone", "Dupilumab", "Benralizumab", "Fluticasone", "Mepolizumab", "Budesonide", "Beclomethasone", 
               "Montelukast", "Tiotropium", "Budesonide", "Fluticasone Furoate", "Omalizumab", "Zileuton", "methylprednisolone", 
               "prednisolone", "Salmeterol", "Formoterol", "Umeclidinium", "Vilanterol"]
Excel_Sheet_Name = "Asthma RxNorm Sheet"



## DO NOT CHANGE CODE BELOW THIS LINE ## 
import requests 
import argparse
import numpy as np
import pandas as pd
version = 'current'



# Collect Data Pulled 
ui_code_RxNorm = []
rootSource_RxNorm = []
name_RxNorm = []

for x in np.arange(0, len(string_list), 1):
    value = string_list[x]
    URL = f"https://uts-ws.nlm.nih.gov/rest/search/current?apiKey={apikey}&string={value}&sabs=RXNORM&returnidType=code&pageSize=2000"
    response = requests.get(URL)
    variable = response.json()
    
    if 'result' in variable:
        # Pull ui code
        for y in np.arange(0, len(variable['result']['results']), 1):
            ui_code_RxNorm.append(variable['result']['results'][y]['ui'])

        # Pull rootSource code
        for y in np.arange(0, len(variable['result']['results']), 1):
            rootSource_RxNorm.append(variable['result']['results'][y]['rootSource'])

        # Pull RxNorm name code
        for y in np.arange(0, len(variable['result']['results']), 1):
            name_RxNorm.append(variable['result']['results'][y]['name'])
    else: 
        continue

RxNorm_pd = pd.DataFrame({"Data Concept": "RxNorm Code", "Data Sub-Concept": "N/A", "Coding Standard": rootSource_RxNorm, "Code Value": ui_code_RxNorm, "Code Description": name_RxNorm}).drop_duplicates().reset_index(drop=True)
RxNorm_pd


# Converts the SNOMED-CT CUI Codes from the chunk above into SNOMEDCT_US Codes
base_uri = 'https://uts-ws.nlm.nih.gov'
cui_list = RxNorm_pd["Code Value"]

sabs = 'RXNORM'
RXNORM_name = []
RXNORM_code = []
RXNORM_root = []

for cui in cui_list:
        page = 0
        
        # o.write('SEARCH CUI: ' + cui + '\n' + '\n')
        
        while True:
            page += 1
            path = '/search/'+version
            query = {'apiKey':apikey, 'string':cui, 'sabs':sabs, 'returnIdType':'code', 'pageNumber':page}
            output = requests.get(base_uri+path, params=query)
            output.encoding = 'utf-8'
            #print(output.url)
        
            outputJson = output.json()

            results = (([outputJson['result']])[0])['results']
            
            if len(results) == 0:
                if page == 1:
                    #print('No results found for ' + cui +'\n')
                    # o.write('No results found.' + '\n' + '\n')
                    break
                else:
                    break
                    
            for item in results:
                RXNORM_code.append(item['ui'])
                RXNORM_name.append(item['name'])
                RXNORM_root.append(item['rootSource'])
        else: 
            continue
                
RXNORM_trans_df = pd.DataFrame({"Data Concept": "RxNorm Code", "Data Sub-Concept": "N/A", "Coding Standard": RXNORM_root, "Code Value": RXNORM_code, "Code Description": RXNORM_name})



# RXNORM_trans_df


excel_name = f'{Excel_Sheet_Name}' + ".xlsx"

RXNORM_trans_df.to_excel(excel_name)




