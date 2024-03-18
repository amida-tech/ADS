# API Data Team Collection 

## Folder Descriptions
- openFDA API 
    - Contains code that gathers NDC codes 
    - Advantages: Gathers all product_ndc codes for a list of drug codes (Excel sheet or manual list input available) 
    - Disadvantages: Currently only gathers NDC codes, and formatted output may be outdated depending on VA feedback

- UMLS API
    - Contains code that gathers SNOMED-CT, ICD10, CPT, LOINC and RxNorm codes (collective or individually)
    - Advantages: gathers all codes commonly required to gather for a eCFR diagnosis codeset.
    - Disadvantages: Requires account with UMLS and access to a UMLS apikey (apikey comes with the account)
