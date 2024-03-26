

import pandas as pd 
import xmltodict

# PATH
PATH_input = r"C:\Users\mchahdil\Desktop\compare_study\\input_files\\"
PATH_output = r"C:\Users\mchahdil\Desktop\compare_study\\output_files\\"

PATH_patient_folder = r"C:\Users\mchahdil\Desktop\data_patient\json_raw\\"


orpha_pd = PATH_input + "/orphanet_files/en_product4.xml"


orphacode_info = set()

with open(orpha_pd) as pd_xml:
    root = xmltodict.parse(pd_xml.read())
xml_dict = root['JDBOR']['HPODisorderSetStatusList']['HPODisorderSetStatus']
for one_dict in xml_dict:

    section_disorder = one_dict['Disorder']
    #print(section_disorder['OrphaCode'])
    section_type = section_disorder['DisorderType']
    section_group = section_disorder['DisorderGroup']

   # extract the element from balise
    values_type = list(section_type['Name'].values())[1]
    values_group = list(section_group['Name'].values())[1]

    orphacode_info.add((str("ORPHA:")+section_disorder['OrphaCode'],values_type,values_group))

df_orphacode_info= pd.DataFrame(orphacode_info, columns=["OrphaCode",'type','group'])

df_orphacode_info.to_excel(PATH_output+"orphacode_type.xlsx")

 

