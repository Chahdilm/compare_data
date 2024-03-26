
# Librairy
import os 
import json 
import pandas as pd 
import sys


# PATH
PATH_input = r"C:\Users\mchahdil\Desktop\compare_study\\input_files"
PATH_output = r"C:\Users\mchahdil\Desktop\compare_study\\output_files"

PATH_patient_folder = r"C:\Users\mchahdil\Desktop\data_patient\json_raw\\"





pd_phenopacket_confirmed = pd.read_excel(PATH_input + "/PATIENTS SOLVED_FC_v1.xlsx",engine='openpyxl',sheet_name='Feuil2')
pd_phenopacket_confirmed = pd_phenopacket_confirmed[pd_phenopacket_confirmed['Result'] == "yes"]
patients_c = pd_phenopacket_confirmed['Patient ID'].drop_duplicates().tolist()

print("{} patients solved confirmed".format(len(patients_c)))


### Select patients solved confirmed :
# Extract Patient
patients_files = os.listdir(PATH_patient_folder)

patients_c_files = []
for one_file in patients_files:
    splited = one_file.split('.')[0]
    if splited in patients_c:
        patients_c_files.append(one_file)
        p_index = patients_c.index(splited)
        # verification 
        print("{}\t{}".format(one_file,patients_c[p_index] ))


### Get HPO from only the patients solved confirmed and curation ( min 5HPO and no negated)

list_case_HPO = []
for one_file in list(patients_c_files):
    with open(PATH_patient_folder + str(one_file)) as phenopacket_json:
        one_result = json.load(phenopacket_json)

        one_phenopacket_result = one_result['phenopacket']
        id_phenopacket = one_phenopacket_result['id']
        #print(id_phenopacket)

        hpo_temp = []

        # phenotypicFeatures dict key store hpo
        if 'phenotypicFeatures' in one_phenopacket_result.keys():
            #  list_hpo contains all HPO terms
            list_hpo = one_phenopacket_result['phenotypicFeatures']
            # if this list is empty
            if not bool(list_hpo):
                pass
            else :
                # HERE dict hpo not empty and exist !!
                hpo_temp = []

                for onehpo in list_hpo:
                    # sometime it s like this  [{}] ... list filled with en empty dict !
                    if not bool(onehpo):
                        pass
                    else:
                        # fill the hpo_temp list
                        # negated part !!
                        try:
                            if (("Invalid id" == onehpo['type.label'])):
                                pass
                            if ( 'type.negated' not in onehpo.keys()):
                                hpo_temp.append(onehpo['type.id'])

                        except KeyError:
                            # json format dict may also have this structure : label and not type.label
                            if (("Invalid id" == onehpo['type']['label']) ):
                                pass
                            if ( 'negated' not in onehpo.keys()):
                                hpo_temp.append(onehpo['type']['id'])
                #if len(hpo_temp) >= 5:
                for onet in hpo_temp:
                    list_case_HPO.append((id_phenopacket, onet,len(hpo_temp)))


case_HPO = pd.DataFrame(list_case_HPO, columns=["phenopacket",'hpo','nb_hpo'])
case_HPO.to_excel(str(PATH_output)+"/df_hpo_solved_confirmed.xlsx")




