icd_input = 'icd_brain'
cpt_input = 'cpt_brain'
ndc_input = 'ndc'
keyword_input = ''

# parse input files
def read_inputs(filename, code):
    """
    Summary: Parses and concatenate input values depending on codeset type (ICD, CPT, NDC, etc.)
    Args: filename(str): filename located in input folder
          code(str): type of code set (icd, cpt, keyword)
    Returns: string: code set values
    """
    if filename is None or filename == '':
        return f'No filename provided for {code} type'

    with open(f'./codeset/input/{filename}.txt', "r") as file:

        # parses and split text files into specific lists for inputs to sql query
        if code == 'icd':
            codeset = "".join(f"{line.rstrip()[:3]}," for line in file)
            codeset = list(set(codeset.split(",")))

        if code == 'cpt':
            codeset = "".join(f"{line.rstrip()}," for line in file)
            codeset = codeset.rstrip(',')

        if code == 'ndc':
            codeset = "".join(f"'{line.rstrip()[:13]}'," for line in file)

        if code == 'keyword':
            codeset = "".join(f"CPTName LIKE '%{line.rstrip()}%' OR " for line in file)

    return f'{code} codeset: {codeset} ============================'


if __name__ == '__main__':

    code_list = [(icd_input,'icd'), (cpt_input,'cpt'), (ndc_input, 'ndc'), (keyword_input, 'keyword')]
    
    # loops through each type of codeset
    for filename, code in code_list:
        print(f"{read_inputs(filename, code)}")
        print(f'                               ')
