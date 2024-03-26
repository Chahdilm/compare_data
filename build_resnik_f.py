

def get_parent_of_ancestor(str_sentence):
    """
    From : {HPOTerm(id='HP:0011804'", " name='Abnormal muscle physiology'"," is_a=['HP:0003011 ! Abnormality of the musculature'])"," HPOTerm(id='HP:0040064'"," name='Abnormality of limbs'",
    ...
    to :
      {'HP:0000001': 'is_a=[])', 'HP:0011804': 'HP:0003011', 'HP:0040064': 'HP:0000118', 'HP:0000118': 'HP:0000001', 'HP:0003011': 'HP:0033127', 'HP:0033127': 'HP:0000118', 'HP:0001324': 'HP:0011804'}
      
    From str into dict 

    """
    ancertor_dict = {}
    one_split = str(str_sentence).split(',')
    is_a = id = ""
    for one_el in one_split:
        #print(one_el)
        if "HPOTerm" in one_el:
            #print(one_el)
            id = one_el.split("id='")[1].replace("'",'')
        elif "name=" in one_el:
            #print('Name : {}'.format(one_el))
            pass
        elif "is_a=" in one_el:
            #print('is_a : {}'.format(one_el))
            is_a_unstruct = one_el.replace("is_a=['",'')
            is_a = is_a_unstruct.split("!")[0].strip()
        ancertor_dict[id] = is_a
    return ancertor_dict

        


#Least commons ancestor
def get_deepest_ancestor(str_sentence_common_ancestor):
    """ 
        trouver l'ancetre commun le plus profond en evalue chaque clé valeur
        il faut que la clé (enfant) ne se retrouve pas dans la valeur du dict (parent)
        From dict to list
        from :{'HP:0000001': 'is_a=[])', 'HP:0011804': 'HP:0003011', 'HP:0040064': 'HP:0000118', 'HP:0000118': 'HP:0000001', 'HP:0003011': 'HP:0033127', 'HP:0033127': 'HP:0000118', 'HP:0001324': 'HP:0011804'}
        key : chilren, value : ancester
        to :['HP:0040064', 'HP:0001324']
    """
    ancertor_dict = get_parent_of_ancestor(str_sentence_common_ancestor)
    #print("AC dict \n : {}".format(ancertor_dict))
    list_LCAs = []  
    for key in ancertor_dict.keys():
        if key not in list(ancertor_dict.values()):
            #print("one LCA : {}".format(key))
            list_LCAs.append(key)
    return list_LCAs


def extracts_LCAdescendant(hpo_LCA,orphacode_item_dict):
    """ From the LCA found all it descendant"""

    ## Extrait tout les descendants a partir du LCA 

    # extrait tout les LCAs trouver
    all_LCA = []
    all_LCA.append(hpo_LCA)
    #print(all_LCA)

    for oneLCA in all_LCA:
        #print(oneLCA)
        # parcourt l'onthology et extrait les enfants 
        list_child = Ontology.get_hpo_object(oneLCA).children
        # parcourt les enfants
        for one_children in list_child:
            if one_children.id not in all_LCA: # si le descendant n'est pas dans la liste de tout les LCAs
                if orphacode_item_dict[one_children.id] != 0: # si le nombre d'occurence est diff de 0 donc non present dans la base 
                    all_LCA.append(one_children.id) 
                    #print("len child {}\t id:{}\tnb occu: {}".format(len(list_child),one_children.id,orphacode_dict[one_children.id]))
    return all_LCA



def enumerated_LCAdescents_per_disease(all_LCA_desd,orphacode_dict):
    """ From  all hpos LCA end their descendant count the disease where its appear"""
    ## pour le LCA et ses descendants on regarde le nombre de maladies ou ils sont presents 
    orpha_LCAs = set()

    for one_orpha in orphacode_dict.keys(): 
        # parcourt en premier tout les orpha
        for onehpochild in all_LCA_desd:
            # pour chaque orpha on regarde si le LCA et ses descants sont present 
            if onehpochild in orphacode_dict[one_orpha]:
                # si l'hpo est present on incremente la liste de la maladie
                orpha_LCAs.add(one_orpha)
    return orpha_LCAs


#######################################################################################################################
import json # use to extrat nb of hpo from hpo.json
from pyhpo import stats, Ontology, HPOSet,term # hpo3
import xmltodict # for the orphcode pd4
import collections # for count nb of hpo in patient or orphacode
import os 
import math # for the log to get the IC
import pandas as pd


#############################################
path_projet = r"C:\Users\Maroua\Desktop\compare_study\\" #r"D:\compare_study\\"

path_input = path_projet + r"\input_files\\"
path_orpha = path_input+r'\orphanet_files'

path_output = path_projet + r"\output_files\\"

#############################################
path_phenopacket = path_output + '\df_hpo_solved_confirmed.xlsx' # df_hpo_solved_confirmed  df_hpo_simulated
# patients confirmed r"D:\DELL\data_patient\json_raw\\"

pd_phenopacket_input = pd.read_excel(path_phenopacket,engine='openpyxl',index_col=0)

#############################################
### I. HPO metric 
# rsd: 16614 terms
# Load hpo3 : 
Ontology()
i=0
# iterating all HPO terms
for term in Ontology:
    i=i+1
print("{} hpo terms".format(i))
# 17059 last hpo3 version

#############################################
### II.Orpha - HPOs 
# rsd : 4210 terms 
# We set IC of these to : 8.345217926676428 = -1 * (log(1 / 4210)

orphacode_info=dict()
all_hpo_orphacode = []
with open(path_orpha+'/en_product4.xml',encoding="ISO-8859-1") as pd_xml:
    root = xmltodict.parse(pd_xml.read())
xml_dict = root['JDBOR']['HPODisorderSetStatusList']['HPODisorderSetStatus']
for one_dict in xml_dict:
    hpo_list = []
    section_disorder = one_dict['Disorder']
    #print(section_disorder['OrphaCode'])
    section_hpo = section_disorder['HPODisorderAssociationList']
    #print(section_hpo.keys())
    # because sometime HPODisorderAssociation dict don't exist 
    if "HPODisorderAssociation" in section_hpo.keys():    
        for one_hpodict in section_hpo['HPODisorderAssociation']:
            hpo_id = one_hpodict['HPO']['HPOId']
            hpo_list.append(hpo_id)
            all_hpo_orphacode.append(hpo_id)
    orphacode_info[section_disorder['OrphaCode']] = set(hpo_list)

#############################################
### IV Count HPOs per patient and HPOs per Orpha
#Compte la fréquence d'apparition des HPO dans les patients puis dans les orphacode
#pd deux dict
                        
# Count HPO per Orphacode
orphacode_hpo_list = collections.Counter(all_hpo_orphacode)

# nb of hpo tot sans doublons
tot_nb_items_hpo_orphacode = sum(list(orphacode_hpo_list.values()))

#nb of different type HPO 
print('nb hpo all : {}\tnb hpo unique : {}\tnb disease : {}'.format(tot_nb_items_hpo_orphacode,len(orphacode_hpo_list),len(orphacode_info)))
 
##########################################################################################

#############################################
# Build patients dict with list of hpo as values
patientsinfo = dict()

patients_json = pd_phenopacket_input['phenopacket'].drop_duplicates().tolist()
for onep in patients_json:
    
    list_hpo = pd_phenopacket_input[pd_phenopacket_input['phenopacket'] == onep]['hpo'].drop_duplicates().tolist()
    patientsinfo[onep] = list_hpo
    list_hpo = []



#############################################
### V Build the df IC of all hpo in orphanet
# Build dict for each hpo get theirs descants and counts occurend of those hpo in orphanet disease 
# (plus simple apres plus besoin de calculer a chaque fois on va utiliser ce dictionnaire plutot qui est calculer une fois )
dict_hpo_ic = {}
for onehpo in orphacode_hpo_list:
    try :
        all_LCA = extracts_LCAdescendant(onehpo,orphacode_hpo_list)
        #print("Le nb de LCA et ses descendants : {}".format(len(all_LCA)))

        orpha_LCAs = enumerated_LCAdescents_per_disease(all_LCA,orphacode_info)
        numerator_ic = len(orpha_LCAs)
        #print('Nb of diseases annotated with LCA and theirs descendant : {}'.format(numerator_ic) )

        ic = -math.log(len(orpha_LCAs) / len(orphacode_info))
        #print("IC : {}".format(ic))
        dict_hpo_ic[onehpo] = [ic,numerator_ic]
    except RuntimeError:
        print("{} Unknown HPO term".format(onehpo))


 
### verication with know ic (cf script  whhy_not_the_same.ipynb
print("This hpo HP:0000924 should be 0,51 : {}".format(dict_hpo_ic['HP:0000924']))

#############################################
### VI Resnik similarity for patient - orpha
print('start resnik calcul')
all_interractions_hpo = set()
i = 0 # count patient iteration until the len of the patient list 
for one_patient in patientsinfo.keys():
    print(i)
    #if one_patient == "P0001068" :
    # the HPO list of the patient of interest
    hpo_list_POF = patientsinfo[one_patient]
    #hpo_list_POF = ['HP:0040068'] # 0007149 0040068

    for one_orpha in orphacode_info.keys():
        #if one_orpha == "178400" :  # 324442  178400
            # the HPO list of the orpha curently tested
            hpo_list_OOI = orphacode_info[one_orpha]
            #hpo_list_OOI = ['HP:0011842'] # 0003438

            for onehpo_p in hpo_list_POF:
                # for each hpos from disease get the LCA (based on the hpo(onehpo_p) patient from hpo_list_POF), its resnik and occu
                hpo_ooi_LCA_resnik = {} # dict have the same lenght as hpo_list_POF
                try :
                    ### get the type HPOTerm for hpo3 library
                    term_patient = Ontology.get_hpo_object(onehpo_p)

                    for onehpo_o in hpo_list_OOI:

                        ### get the type HPOTerm for hpo3 library
                        term_disease = Ontology.get_hpo_object(onehpo_o)

                        ### Got the commons ancestors :
                        all_common_ancestors = term_patient.common_ancestors(term_disease)
                        # from all_common_ancestors get the LCA
                        if not list(all_common_ancestors):
                            #excluded
                            pass
                        else:
                            # from all_common_ancestors extract the LCA
                            list_LCAs = get_deepest_ancestor(all_common_ancestors) # contain the get_parent_of_ancestor function
                            # loop because sometimes we have selevral LCA
                            for id_LCA in list_LCAs:
                                try :
                                    resnik = dict_hpo_ic[id_LCA][0]
                                    hpo_LCA_count=dict_hpo_ic[id_LCA][1]

                                    # for each hpo FROM ORPHACODE and the hpo for patient get the LCA and store its resnik
                                    hpo_ooi_LCA_resnik[term_disease.id] = [resnik,id_LCA,hpo_LCA_count]


                                except KeyError:
                                    # This HPO is not use in the Orphanet ontho
                                    # set resnik the same as rsd set it
                                    resnik = 0 #-math.log(1 / 4210)
                                    replaced_term = list(HPOSet.from_queries([id_LCA]).replace_obsolete())[0]
                                    hpo_ooi_LCA_resnik[term_disease.id] = [resnik,id_LCA,0]

                            # extract the LCA with the hight resnik values
                            max_resnik_disease_hpo = max(hpo_ooi_LCA_resnik, key=hpo_ooi_LCA_resnik.get)
                            max_hpo_resnik = hpo_ooi_LCA_resnik[max_resnik_disease_hpo][0]
                            max_hpo_id = hpo_ooi_LCA_resnik[max_resnik_disease_hpo][1]
                            max_hpo_id_occu = hpo_ooi_LCA_resnik[max_resnik_disease_hpo][2]

                            all_interractions_hpo.add((one_patient,str("ORPHA:"+one_orpha),term_patient.id,max_resnik_disease_hpo,max_hpo_id,max_hpo_id_occu))

                except RuntimeError:
                    # unknow hpo terms
                    # un des deux
                    pass
    i = i+1

print('end resnik calcul')

hpo_description = pd.DataFrame(all_interractions_hpo, columns=["phenopacket",'orphacode','HP_patient','HP_max_disease','HP_LCA','occu_LCA'])
# remove all row with HP:0000001 in the hpo_description
hpo_description_f= hpo_description[~hpo_description['HP_LCA'].str.contains("HP:0000001")]
print('set hpo_description_f')


#############################################
##### Calcul Resnik
print('start merge resnik')

list_df_pheno= hpo_description_f['phenopacket'].drop_duplicates().to_list()
list_df_orpha= hpo_description_f['orphacode'].drop_duplicates().to_list()

all_interaction_resnik = []
for onephenopacket in list_df_pheno:
    # split the df by patients
    mini_df= hpo_description_f[hpo_description_f['phenopacket']== onephenopacket]
    
    for oneorphacode in list_df_orpha:
        # split by orpha
        mini_mini_df= mini_df[mini_df['orphacode']==oneorphacode]
        # for eacorpha extract all hpo LCA related to orphacode -patient interaction 
        all_hpoLCA = mini_mini_df['HP_LCA'].drop_duplicates().tolist()

        # for all LCA get the resnik 
        best_LCAs_resnik = {key: value[0] for key, value in dict_hpo_ic.items() if key in all_hpoLCA}
        
        sum_ic = sum(best_LCAs_resnik.values())
        final_ic = sum_ic / len(all_hpoLCA) # divided by the tot number of hpos patients

        all_interaction_resnik.append((onephenopacket,oneorphacode,final_ic))

print('end merge resnik')

df_resnik = pd.DataFrame(all_interaction_resnik, columns=["phenopacket",'ORPHAcode','resnik'])
print("create final resnik df")

#############################################
# etablir le rank cad pour chaque maladie garder uniquement le top 50

# construiction a partir de la df resnik d'un dict de df 
list_df_pheno= df_resnik['phenopacket'].drop_duplicates().to_list()
list_df_orpha= df_resnik['ORPHAcode'].drop_duplicates().to_list()

all_interaction_resnik = []
dict_of_resnik_df = {}

for onephenopacket in list_df_pheno:
    # split the df by patients
    mini_df= df_resnik[df_resnik['phenopacket']== onephenopacket]
    # sort by score
    df_op = mini_df.sort_values('resnik',ascending=False)
    # keep the top 50
    #df_op = df_op.head(200)
    df_op = df_op.head(50)

    df_op.reset_index(drop=True)
    dict_of_resnik_df[onephenopacket] = df_op

    df_op= pd.DataFrame([], columns=["phenopacket",'ORPHAcode','resnik'])

print('build rank into dict of df and keep top 50')

#############################################
all_interractions=[]


for key,dfval in dict_of_resnik_df.items():
    #print("set the df for the patient {}".format(key))
    dict_df_one_P_hpo3 = dfval.to_dict('index')

    i = 0 # for the rank
    for value in dict_df_one_P_hpo3.values():
        hpo3_onepheno = value['phenopacket']
        hpo3_oneorpha= value['ORPHAcode']
        hpo3_onescore= value['resnik']

        i = i + 1
        
        all_interractions.append((hpo3_onepheno,hpo3_oneorpha,hpo3_onescore,i))

print('build rank into df')


df_resnik_with_rank = pd.DataFrame(all_interractions, columns=["phenopacket",'ORPHAcode','resnik','rank'])
print('save final resnik df')
#############################################
### Export

df_resnik_with_rank.to_excel(path_output+"df_resnik_simu_50_rank.xlsx")
print('export resnik')