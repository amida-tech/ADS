# API Data Team Collection 

## Folder Descriptions
- openFDA API 
    - Contains code that gathers NDC codes 
    - Advantages: Gathers all product_ndc codes for a list of drug codes (Excel sheet or manual list input available) 
    - Disadvantages: Currently only gathers NDC codes, and formatted output may be outdated depending on VA feedback

- UMLS API (Recommended)
    - Contains code that gathers SNOMED-CT, ICD10, CPT, LOINC and RxNorm codes (collective or individually)
    - Advantages: gathers all codes commonly required to gather for a eCFR diagnosis codeset and outputs files in the official format.
    - Disadvantages: Requires account with UMLS and access to a UMLS apikey (apikey comes with the account)

- SNOWSTORM API (Not Recommended for Use)
    - Contains code that gathers SNOMED-CT and ICD10 codes 
    - Advantages: Does not require an API key or outside account, returns very detailed and reliable SNOMED-CT codes.
    - Disadvantages: Limited to about 500 calls a day, cannot handle large calls, ICD10 codes do not map to an official ICD10 name (only returns their related SNOMED-CT name), and does not output files in the official format.
