
# Librairy
import os 
import json 
import pandas as pd 
import sys


# PATH
PATH_input = r"C:\Users\mchahdil\Desktop\compare_study\\input_files"
PATH_output = r"C:\Users\mchahdil\Desktop\compare_study\\output_files"

PATH_patient_folder = PATH_input + "/phenopacket/"





### Select patients solved confirmed :
# Extract Patient
patients_files = os.listdir(PATH_patient_folder)



### Get HPO from only the patients solved confirmed and curation ( min 5HPO and no negated)

list_case_HPO = []
for one_file in list(patients_files):
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
                        hpo_temp.append(onehpo['type']['id'])
                for onet in hpo_temp:
                    list_case_HPO.append((id_phenopacket, onet,len(hpo_temp)))


case_HPO = pd.DataFrame(list_case_HPO, columns=["phenopacket",'hpo','nb_hpo'])
case_HPO.to_excel(str(PATH_output)+"/df_hpo_simulated.xlsx")




