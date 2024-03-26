import os
import pandas as pd 
import xmltodict


path_rsd_debug = r"C:\Users\mchahdil\Desktop\data_patient\output_files_22264_phenopackets\output_files\study_population\results\results_noduplicates\resultsORDO\\"
PATH_input = r"C:\Users\mchahdil\Desktop\compare_study\\input_files\\"
PATH_output = r"C:\Users\mchahdil\Desktop\compare_study\\output_files\\"

#####################################################################
# try to get the id based on label

orpha_pd = PATH_input + "/orphanet_files/en_product4.xml"


orphacode_info = []

with open(orpha_pd) as pd_xml:
    root = xmltodict.parse(pd_xml.read())
xml_dict = root['JDBOR']['HPODisorderSetStatusList']['HPODisorderSetStatus']
for one_dict in xml_dict:

    section_disorder = one_dict['Disorder']
    #print(section_disorder['OrphaCode'])
    id_orphacode = section_disorder['OrphaCode']
    section_name = section_disorder['Name']

   # extract the element from balise
    values_name = list(section_name.values())[1]

    orphacode_info.append((str("ORPHA:")+id_orphacode,values_name))

df_orphacode_info= pd.DataFrame(orphacode_info, columns=["id",'label'])

#####################################################################
pd_phenopacket_confirmed = pd.read_excel(PATH_input + "/PATIENTS SOLVED_FC_v1.xlsx",engine='openpyxl',sheet_name='Feuil2')
pd_phenopacket_confirmed = pd_phenopacket_confirmed[pd_phenopacket_confirmed['Result'] == "yes"]
patients_c = pd_phenopacket_confirmed['Patient ID'].drop_duplicates().tolist()

print("{} patients solved confirmed".format(len(patients_c)))
#####################################################################
rsd_output= os.listdir(path_rsd_debug)

debug_file = list()
for onef in rsd_output:
    if 'json.debug.txt' in onef:
        patient = onef.split('.')[0]
        if patient in patients_c:
            debug_file.append(onef)
debug_file

#####################################################################

#debug_file = ['P0000411.json.debug.txt', 'P0000414.json.debug.txt']

# extract all info and put it in list 
all_interactions = []

for onef_txt in debug_file:
    # open file debug.txt
    f =  open((path_rsd_debug + str(onef_txt)),'r') 
    all_debug = f.readlines()
    f.close()

    # after this section read the debug and extract pertinente info
    pheno_id = ""
    methods = ""
    disease_id = ""
    score = ""
    rank = 0
    for oned in all_debug:
        score = ""

        if ('# phenopacket') in oned:
            pheno_id = oned.split(':')[2].strip()
            pheno_id_s = pheno_id.split('.')[0]
            print(pheno_id)
        #if ' report for method: Resnik (symmetric' in oned:
        if ' report for method: Resnik (asymmetric' in oned:
            methods = oned.split(':')[1].strip()
        if " disease: " in oned:
            disease_id = oned.split(':')[1].strip()
            try:
                orphacode = df_orphacode_info[df_orphacode_info['label'] == str(disease_id)]['id'].values[0]
            except:
                orphacode = disease_id
        if ("final score") in oned:
            score = oned.split(' ')[2].strip()
        if ((pheno_id != "") and (methods != "") and (disease_id != "") and (score != "")):   
            rank = rank+1
            all_interactions.append((pheno_id_s,methods,orphacode,score,rank))
            score = "" # because score incremente in the end of the disease


df_rsd= pd.DataFrame(all_interactions, columns=["phenopacket",'methods','ORPHAcode','score','rank'])
# verification manuelle des 4 premier ligne c'est ok 
df_rsd  = df_rsd.drop_duplicates()

#####################################################################

# construiction a partir de la df resnik d'un dict de df 
list_df_pheno= df_rsd['phenopacket'].drop_duplicates().to_list()

dict_of_resnik_df = {}
for onephenopacket in list_df_pheno:
    # split the df by patients
    mini_df= df_rsd[df_rsd['phenopacket']== onephenopacket]
    # keep the top 50
    df_op = mini_df.head(50)
    df_op.reset_index(drop=True)
    dict_of_resnik_df[onephenopacket] = df_op

    df_op= pd.DataFrame([], columns=["phenopacket",'ORPHAcode','score'])
dict_of_resnik_df


all_interractions=[]
for key,dfval in dict_of_resnik_df.items():
    #print("set the df for the patient {}".format(key))
    dict_df_one_P = dfval.to_dict('index')

    i = 0 # for the rank
    for value in dict_df_one_P.values():
        onepheno = value['phenopacket']
        oneorpha= value['ORPHAcode']
        onescore= value['score']

        i = i + 1
        
        all_interractions.append((onepheno,oneorpha,onescore,i))



df_rsd_f = pd.DataFrame(all_interractions, columns=["phenopacket",'ORPHAcode','score','rank'])



df_rsd_f.to_excel(PATH_output+"df_rsd_resnik_asymmetric.xlsx")
