# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 12:25:11 2019

@author: Utilisateur
"""

#Ici on va trouver les journées types

import pandas as pd
import modelisation_ev.probmodel as pm
import math
import modelisation_ev.module_modele_jour as mmj
import numpy as np
import os.path


def changer_categorie_motifs(x):
    #On transforme motifs personnels en 5 (catégorie la moins utile) + on transforme les loisirs en deux catégories qui nous intéressent ici : grand et petit parking
    if x == 8.89:
        x = 3
    elif (x == 2.2 or x == 7.72 or x == 7.74 or x == 7.75):
        #ce sont les grands parking
        x = 2
    elif x==2.21 or (x >= 3 and x<=6) or (math.floor(x)==7 and not(x == 7.72 or x == 7.74 or x == 7.75)):
        #ce sont les petits parkings
        x = 3
    return x

def transf_zone_geo(x):
    # On transforme
    if x == "banlieue":
        return 'B'
    elif  x == 'ville centre':
        return 'V'
    elif x == 'commune rurale':
        return 'R'
    elif x == 'ville isolée':
        return 'I'

def combine_trans(dep,arr):
    return str(dep) + ' - ' + str(arr)

def taille_aire_urbaine(x):
    if x == 0:
        return 0
    if 1 <= x < 4:
        return 1
    if 4 <= x < 7:
        return 2
    if x >= 7:
        return 3
    else:
        return -1

def preparer_data():
    """
    Importe, sélectionne les données utiles, traite les colonnes (pour les mettre dans des formats utilisables)
    retourne bdd des déplacements et bdd des individus
    """
    TYPE_JOUR = 1
    MOY_TRANS = [3.30, 3.31]
    DISTANCE_MAX = 100

    print("Importation des bases de données...")

    data = pd.read_csv(os.path.join("modelisation_ev","data","K_deploc.csv"), sep=";", encoding="ISO-8859-1", low_memory = False)
    data_indiv = pd.read_csv(os.path.join("modelisation_ev","data","Q_individu.csv"), sep=";", encoding="ISO-8859-1", low_memory = False)

    print("Importation réussie !")
    
    #On filtre

    data_indiv.loc[:,'IDENT_IND'] = data_indiv['idENT_MEN']*100 + data_indiv['NOI']
    data_filt_inter = data[(data['V2_TYPJOUR'] == TYPE_JOUR) &
                           (data['V2_MORIDOM'] == 1) &
                           (data['V2_MDISTTOT'] > 0) &
                           (data['V2_VAC_SCOL'] == 0) &
                           (data['V2_MDISTTOT'] < DISTANCE_MAX) &
                           (data['V2_MNBMOD'] == 1) &
                           (data['V2_MTP'].isin(MOY_TRANS)) &
                           (data['V2_MFINCONFIRM'] != 1) &
                           (~(data['V2_MDESCOM_UUCat'].isnull())) &
                           (~(data['V2_MORICOM_UUCat'].isnull())) &
                           (~(data['V2_MORICOM_zhu'].isnull())) &
                           (~(data['V2_MDESCOM_zhu'].isnull()))].copy()

    data_indiv = data_indiv[['IDENT_IND','V1_BTRAVT','V1_BTRAVHS','SITUA']].copy()

    #On traite

    data_filt_inter.loc[:,'V2_MORICOM_UUCat'] = data_filt_inter['V2_MORICOM_UUCat'].apply(transf_zone_geo)
    data_filt_inter.loc[:,'V2_MDESCOM_UUCat'] = data_filt_inter['V2_MDESCOM_UUCat'].apply(transf_zone_geo)
    data_filt_inter['SPATIAL'] = np.vectorize(combine_trans)(data_filt_inter['V2_MORICOM_UUCat'],data_filt_inter['V2_MDESCOM_UUCat'])
    li_spat = pd.factorize(data_filt_inter['SPATIAL'])[1]
    data_filt_inter['SPATIAL']= pd.factorize(data_filt_inter['SPATIAL'])[0]

    data_filt_inter.loc[:,'V2_MDESCOM_zhu'] = data_filt_inter['V2_MDESCOM_zhu'].apply(taille_aire_urbaine)
    data_filt_inter.loc[:,'V2_MORICOM_zhu'] = data_filt_inter['V2_MORICOM_zhu'].apply(taille_aire_urbaine)
    data_filt_inter['SPATIAL_ZHU'] = np.vectorize(combine_trans)(data_filt_inter['V2_MORICOM_zhu'],data_filt_inter['V2_MDESCOM_zhu'])
    li_spatzhu = pd.factorize(data_filt_inter['SPATIAL_ZHU'])[1]
    data_filt_inter['SPATIAL_ZHU'] = pd.factorize(data_filt_inter['SPATIAL_ZHU'])[0]

    data_filt = data_filt_inter[['POIDS_JOUR', 'V2_TYPJOUR', 'V2_MORIHDEP',
                                 'V2_MMOTIFDES', 'V2_DUREE', 'V2_MDISTTOT',
                                 'IDENT_IND', 'V2_DURACT','SPATIAL','SPATIAL_ZHU','V2_MORICOM_MDESCOM_indicUU']].copy()

    data_filt.loc[:,'V2_MMOTIFDES'] = data_filt['V2_MMOTIFDES'].apply(changer_categorie_motifs)

    #data_join = data_filt.merge(data_indiv[['IDENT_IND','V1_BTRAVT','V1_BTRAVHS','SITUA']], left_on='IDENT_IND', right_on='IDENT_IND', how='left')

    data_filt.loc[:,'V2_MORIHDEP'] = pd.to_timedelta(data_filt['V2_MORIHDEP'], errors = 'coerce')

    return data_filt, data_indiv

def utilisation_data(df_dep, df_indiv):
    """
    Modélisation en probabilité des différents types de trajets et des différents types de journée
    df_dep : bdd des déplacements
    df_indiv : bdd des individus
    renvoie un dictionnaire de dictionnaire contenant pour chaque type de journée les différents modèles des types de trajets
    renvoie plein de dictionnaires pour les types de journée
    """

    print("Modélisation des différents types de journée...")

    (profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, df) = mmj.modele_jours_type(df_dep, df_indiv)

    #profil_mob = pg.DiscreteDistribution({'domtravail':0.328866,'domtravailmidi':0.08041,'domtravailloisirs' : 0.20649,'domtravailmidiloisirs' : 0.034141, 'domloisirs' : 0.35})

    print("Modélisation réussie !")

    print("Modélisation des types de trajet...")

    modglob_dist, modglob_duree = pm.probglob(df)
    #testmod = pm.cat_spatiale_trajets(modglob_dist,modglob_duree,df)

    dic_param_trajets={}
    dic_param_trajets['domtravail']={}
    dic_param_trajets['domtravailmidi']={}
    dic_param_trajets['domtravailloisirs']={}
    dic_param_trajets['domtravailmidiloisirs']={}
    dic_param_trajets['domloisirs']={}

    dic_param_trajets['domtravail']['travmat'] = pm.probparam(df, 'domtravail', 5, 10.5, 9)
    dic_param_trajets['domtravail']['domsoir'] = pm.probparam(df, 'domtravail', 15, 21, 1)

    dic_param_trajets['domtravailmidi']['travmat'] = pm.probparam(df, 'domtravailmidi', 5, 10.5, 9)
    dic_param_trajets['domtravailmidi']['dommidi'] = pm.probparam(df, 'domtravailmidi', 11, 14, 1)
    dic_param_trajets['domtravailmidi']['travmidi'] = pm.probparam(df, 'domtravailmidi', 12, 15, 9)
    dic_param_trajets['domtravailmidi']['domsoir']= pm.probparam(df, 'domtravailmidi', 15, 21, 1)

    dic_param_trajets['domtravailloisirs']['gparkmat'] = pm.probparam(df, 'domtravailloisirs', 5, 10.5, 2)
    dic_param_trajets['domtravailloisirs']['pparkmat']=pm.probparam(df, 'domtravailloisirs', 5, 10.5, 3)
    dic_param_trajets['domtravailloisirs']['travmat']=pm.probparam(df, 'domtravailloisirs', 5, 10.5, 9)
    dic_param_trajets['domtravailloisirs']['dommat']=pm.probparam(df, 'domtravailloisirs', 5, 10.5, 1)
    dic_param_trajets['domtravailloisirs']['gparkmidi']=pm.probparam(df, 'domtravailloisirs', 11, 14, 2)
    dic_param_trajets['domtravailloisirs']['pparkmidi']=pm.probparam(df, 'domtravailloisirs', 11, 14, 3)
    dic_param_trajets['domtravailloisirs']['travmidi']=pm.probparam(df, 'domtravailloisirs', 11, 15, 9)
    dic_param_trajets['domtravailloisirs']['pparksoir']=pm.probparam(df, 'domtravailloisirs', 15, 23, 3)
    dic_param_trajets['domtravailloisirs']['gparksoir']=pm.probparam(df, 'domtravailloisirs', 15, 23, 2)
    dic_param_trajets['domtravailloisirs']['domsoir']=pm.probparam(df, 'domtravailloisirs', 15, 23, 1)

    dic_param_trajets['domtravailmidiloisirs'] = {}#pas de grand parking
    dic_param_trajets['domtravailmidiloisirs']['pparkmat']=pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 3)
    dic_param_trajets['domtravailmidiloisirs']['travmat']=pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 9)
    dic_param_trajets['domtravailmidiloisirs']['dommat']=pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 1)
    dic_param_trajets['domtravailmidiloisirs']['gparkmidi']=pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 2)
    dic_param_trajets['domtravailmidiloisirs']['dommidi']=pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 1)
    dic_param_trajets['domtravailmidiloisirs']['pparkmidi']=pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 3)
    dic_param_trajets['domtravailmidiloisirs']['travmidi']=pm.probparam(df, 'domtravailmidiloisirs', 11, 15, 9)
    dic_param_trajets['domtravailmidiloisirs']['pparksoir']=pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 3)
    dic_param_trajets['domtravailmidiloisirs']['gparksoir']=pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 2)
    dic_param_trajets['domtravailmidiloisirs']['domsoir']=pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 1)


    dic_param_trajets['domloisirs']['gparkmat'] = pm.probparam(df, 'domloisirs', 5, 10.5, 2)
    dic_param_trajets['domloisirs']['pparkmat']=pm.probparam(df, 'domloisirs', 5, 10.5, 3)
    dic_param_trajets['domloisirs']['dommat']=pm.probparam(df, 'domloisirs', 5, 11, 1)
    dic_param_trajets['domloisirs']['gparkmidi']=pm.probparam(df, 'domloisirs', 11, 14.5, 2)
    dic_param_trajets['domloisirs']['dommidi']=pm.probparam(df, 'domloisirs', 11, 15, 1)
    dic_param_trajets['domloisirs']['pparkmidi']=pm.probparam(df, 'domloisirs', 11, 14.5, 3)
    dic_param_trajets['domloisirs']['pparksoir']=pm.probparam(df, 'domloisirs', 15, 23, 3)
    dic_param_trajets['domloisirs']['gparksoir']=pm.probparam(df, 'domloisirs', 15, 23, 2)
    dic_param_trajets['domloisirs']['domsoir']=pm.probparam(df, 'domloisirs', 15, 23, 1)

    print("Modélisation réussie !")

    return dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom

def initialise_var():
    df_dep, df_ind = preparer_data()
    dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom = utilisation_data(df_dep, df_ind)
    return dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom
