

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


def export_file(path, d_list,str_name):
    with open(path +"\\" + str_name + ".txt", 'a') as f:

        for oneel in d_list:
            # we use ; to split because it's esier to handle 
            f.write(str(oneel) + ";")

#######################################################################################################################
import json # use to extrat nb of hpo from hpo.json
from pyhpo import stats, Ontology, HPOSet,term # hpo3
import xmltodict # for the orphcode pd4
import collections # for count nb of hpo in patient or orphacode
import os 
import math # for the log to get the IC
import pandas as pd


#############################################
path_projet = r"D:\compare_study\\"

path_input = path_projet + r"\input_files\\"
path_orpha = path_input+r'\orphanet_files'

path_output = path_projet + r"\output_files\\"


path_phenopacket = r"D:\DELL\data_patient\json_raw\\"


#############################################
### I. HPO metric 
# rsd: 16614 terms</b>
# Load hpo3 : </b>

Ontology()

#############################################
### II.Orpha - HPOs <br>
# rsd : 4210 terms </b><br>
# We set IC of these to : 8.345217926676428 = -1 * (log(1 / 4210)

orphacode_info=dict()
all_hpo_orphacode = []
with open(path_orpha+'/en_product4.xml') as pd_xml:
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
###  III. Patients - HPOs
#### Get Solved case confirmed
    
 
pd_phenopacket_confirmed = pd.read_excel(path_input + "/PATIENTS SOLVED_FC_v1.xlsx",engine='openpyxl',sheet_name='Feuil2')
pd_phenopacket_confirmed = pd_phenopacket_confirmed[pd_phenopacket_confirmed['Result'] == "yes"]
patients_c = pd_phenopacket_confirmed['Patient ID'].drop_duplicates().tolist()

print("{} patients solved confirmed".format(len(patients_c)))

# path patients
files_json = os.listdir(path_phenopacket)
 
# remove the desktop.ini' and keep only phenopackets
patients_json = []
for op in files_json:
    # select only patients solved confirmed
    op_split= op.split('.')[0]
    if op_split in patients_c:
        patients_json.append(op)


#############################################
# extract info from phenopacket 
patientsinfo = dict()
all_hpo_patients = []

pheno_with_invalid_id =set()
empty_no_phenotypic_feature = set()
for onep in patients_json:
    id_list = []
    with open(path_phenopacket+str("\\"+onep),'r',encoding = 'utf8') as file_phenopacket:
        one_result = json.load(file_phenopacket)

        one_phenopacket_result = one_result['phenopacket']
        id_phenopacket = one_phenopacket_result['id']
        # phenotypicFeatures dict key store hpo
        if 'phenotypicFeatures' in one_phenopacket_result.keys():
            #  list_hpo contains all HPO terms
            list_hpo = one_phenopacket_result['phenotypicFeatures']

            if not bool(list_hpo):
                # if this list is empty
                empty_no_phenotypic_feature.add(id_phenopacket)
            else :
                hpo_temp = []
                for onehpo in list_hpo:
                    if not bool(onehpo):
                        # sometime it s like this  [{}] ... list filled with en empty dict !
                        empty_no_phenotypic_feature.add(id_phenopacket)
                    else:
                        # fill the hpo_temp list
                        try:
                            if (("Invalid id" == onehpo['type.label'])):
                                pheno_with_invalid_id.add(id_phenopacket)
                                pass
                            if ( 'type.negated' not in onehpo.keys()):
                                hpo_temp.append(onehpo['type.id'])
                                all_hpo_patients.append(onehpo['type.id'])

                        except KeyError:
                            # json format dict may also have this structure : label and not type.label

                            if (("Invalid id" == onehpo['type']['label']) ):
                                pheno_with_invalid_id.add(id_phenopacket) 
                                pass
                            if ( 'negated' not in onehpo.keys()):
                                hpo_temp.append(onehpo['type']['id'])
                                all_hpo_patients.append(onehpo['type']['id'])


                if len(hpo_temp) >= 5:
                    if ((id_phenopacket not in pheno_with_invalid_id) and (id_phenopacket not in empty_no_phenotypic_feature)):
                        # if the number of element in hpo_temp is hight than 5 then the phenopacket contains more than 5HPO
                        patientsinfo[id_phenopacket] = hpo_temp

#############################################
### IV Count HPOs per patient and HPOs per Orpha
#Compte la fréquence d'apparition des HPO dans les patients puis dans les orphacode
#pd deux dict

patient_hpo_item = collections.Counter(all_hpo_patients)


# Count HPO per Orphacode
orphacode_hpo_item = collections.Counter(all_hpo_orphacode)

# nb of hpo tot sans doublons
tot_nb_items_hpo_orphacode = sum(list(orphacode_hpo_item.values()))

#nb of different type HPO 
print('nb hpo all : {}\tnb hpo unique : {}\tnb disease : {}'.format(tot_nb_items_hpo_orphacode,len(orphacode_hpo_item),len(orphacode_info)))

#############################################
### V Build the df IC of all hpo in orphanet

# from collection dict type to list 
orphacode_hpo_list = list(orphacode_hpo_item.keys())
print('nb of HPO available in Orphanet : {}'.format(len(orphacode_hpo_list)))

# Build dict for each hpo get theirs descants and counts occurend of those hpo in orphanet disease 
# (plus simple apres plus besoin de calculer a chaque fois on va utiliser ce dictionnaire plutot qui est calculer une fois )
dict_hpo_ic = {}
for onehpo in orphacode_hpo_list:
    try :
        all_LCA = extracts_LCAdescendant(onehpo,orphacode_hpo_item)
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
print("This hpo HP:0000924 should be 0,49 : {}".format(dict_hpo_ic['HP:0000924']))

#############################################
### VI Resnik similarity for patient - orpha
#### Get the LCA and its calculated the IC
print('start resnik calcul')
all_interractions_hpo = set()

for one_patient in patientsinfo.keys():
        # get the HPO list of the patient of interest
        hpo_list_POF = patientsinfo[one_patient]

        for one_orpha in orphacode_info.keys():
                # ge the HPO list of the orpha curently tested
                hpo_list_OOI = orphacode_info[one_orpha]
                for onehpo_p in hpo_list_POF:
                    # dict to store the resnik sim of each hpo from orphacode BASED ON A SINGLE HPO PATIENT
                    hpo_ooi_LCA_resnik = {}
                    try :
                        ### get the type HPOTerm for hpo3 library
                        term_patient = Ontology.get_hpo_object(onehpo_p)

                        for onehpo_o in hpo_list_OOI:
                            """ on a besoin de toutes ces sim pour en selectionner un seul et faire la meme chose pour 
                                tout les hpo des patients """
                        
                            ### get the type HPOTerm for hpo3 library
                            term_disease = Ontology.get_hpo_object(onehpo_o)

                            ### Identification des Ancêtres Communs : 
                            all_common_ancestors = term_patient.common_ancestors(term_disease)

                            # we have all the commons ancestor let get the closest which is the firt one in the set (converted in a list)
                            if not list(all_common_ancestors):
                                #print(" cas pas d'ancetre commun retrouver (situation impossible)")
                                #excluded
                                pass
                            else: 
                                ### get the lca based on the list of commons ancestor
                                # contain the get_parent_of_ancestor function
                                list_LCAs = get_deepest_ancestor(all_common_ancestors) 
                                #print("LCAs : {}".format(list_LCAs))

                                for id_LCA in list_LCAs:
                                    try : 
                                        resnik = dict_hpo_ic[id_LCA][0]

                                        # for each hpo FROM ORPHACODE and the hpo for patient get the LCA and store its resnik
                                        hpo_ooi_LCA_resnik[term_disease.id] = [resnik,id_LCA]


                                    except KeyError:
                                        # This HPO is not use in the Orphanet ontho
                                        # set resnik the same as rsd set it
                                        resnik = -math.log(1 / 4210)
                                        hpo_ooi_LCA_resnik[term_disease.id] = [resnik,id_LCA]

                                                                

                                    
                                    
                                # one the dict is build we extract the max resnik
                                max_resnik_disease_hpo = max(hpo_ooi_LCA_resnik, key=hpo_ooi_LCA_resnik.get)
                                max_resnik_disease_hpo_sim = hpo_ooi_LCA_resnik[max_resnik_disease_hpo][0]
                                max_resnik_disease_hpo_LCA = hpo_ooi_LCA_resnik[max_resnik_disease_hpo][1]

                                all_interractions_hpo.add((one_patient,str("ORPHA:"+one_orpha),term_patient.id,max_resnik_disease_hpo,max_resnik_disease_hpo_sim,max_resnik_disease_hpo_LCA))

                    except RuntimeError:
                        # unknow hpo terms
                        # un des deux
                        pass
#df_hpo_no_AC_common = pd.DataFrame(hpo_no_AC_common, columns=["phenopacket",'orphacode','HP_patient','HP_disease'])
#detail_resnik_calcul = pd.DataFrame(all_detail_interactions, columns=["phenopacket",'orphacode','HP_patient','HP_disease','HP_LCA',"nb_times_LCA_in_orphanet",'IC_LCA'])
print('end resnik calcul')

hpo_description = pd.DataFrame(all_interractions_hpo, columns=["phenopacket",'orphacode','HP_patient','HP_max_LCA','resnik','HP_LCA'])
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
        # get unique LCA from this interactions 
        all_hpoLCA = mini_mini_df['HP_LCA'].drop_duplicates()
        # smerge all ic and divided by the number of LCA found for this orpha
        sum_ic = 0
        for oneLCA in all_hpoLCA:
            try:
                hpo_id =dict_hpo_ic[oneLCA][0]
                sum_ic = sum_ic + hpo_id
            except KeyError:
                print("UNKNOW HPO : {}".format(hpo_id))

        final_ic = sum_ic / len(all_hpoLCA)

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

df_resnik_with_rank.to_excel(path_output+"df_resnik_with_rank.xlsx")
print('export resnik')