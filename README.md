# MCP-ADS

## Overview
MCP-ADS (Modern Claims Processing - Automated Decision Support) is a collection of tools and scripts to retrieve, convert, and manage medical codes from various sources, including UMLS and OpenFDA. The repository provides APIs for fetching medical codes, utilities for working with CDW data, and notebooks for practice and testing.

## Setup
### Prerequisites
- **Python**: Version ~= 3.9
- **[pyenv](https://github.com/pyenv/pyenv) (Recommended)**: For creating virtual environments and managing Python versions.

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/amida-tech/ADS.git
   cd MCP-ADS
   ```
2. Set up a virtual environment using `pyenv` or `venv`:
   ```sh
   pyenv virtualenv 3.9 mcp-ads-env
   pyenv activate mcp-ads-env
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run linting to ensure code quality:
   
- **Pylint**: Check for code issues
   ```sh
   pip install pylint
   pylint your_file.py
   ```

- **autopep8**: Automatically fix formatting issues
   ```sh
   pip install autopep8
   autopep8 --in-place --aggressive your_file.py
   ``` 

- For style guidelines, follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## Project Structure
```
MCP-ADS/
│-- APIs/           # Scripts to pull medical codes from UMLS and OpenFDA
│-- GEMS/           # Scripts to convert ICD-10 codes to ICD-9 codes
│-- Notebooks/      # Practice notebooks for working with UMLS API
│-- utils/          # Utility scripts for CDW code validation and parsing data for SQL queries
│-- requirements.txt # Dependencies
│-- README.md       # Project documentation
```

## Components
### **APIs**
Scripts to pull medical codes from:
- **UMLS**: Retrieves ICD-10, SNOMED-CT, CPT, RxNorm, and LOINC codes
- **OpenFDA**: Retrieves NDC codes

*Note:* Both sets of scripts require API keys. Refer to the individual READMEs in the `APIs/` directory for setup instructions.

### **GEMS**
- Scripts for mapping **ICD-10** codes to **ICD-9** codes using General Equivalence Mappings (GEMs).

### **Notebooks**
- Jupyter notebooks that demonstrate how to interact with the **UMLS API** and return medical codes

### **utils**
- Scripts for:
  - Checking if medical codes exist in **CDW**
  - Auto-populating **CDW Data Locations**
  - Parsing inputs for **SQL queries**

## Usage
- Ensure your API keys are set up in the appropriate environment variables.
- Run scripts using:
  ```sh
  python APIs/your_script.py
  ```
- Explore Jupyter notebooks with:
  ```sh
  jupyter notebook
  ```
