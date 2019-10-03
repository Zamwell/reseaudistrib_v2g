# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 14:41:16 2019

@author: Utilisateur
"""

import numpy as np
import math
import modelisation_ev.fonction_bool as fb
import pandas as pd
import pomegranate as pg
import matplotlib.pyplot as plt

def modele_jours_type(df, df_gens):
    #Va renvoyer les modèles associés au type de jour (domicile travail, domicile travail loisirs), le nombre de loisir par jour, le moment de ces loisirs, ect
    data_journee=pd.DataFrame()
    data_journee = df.copy()
    typjour = [name for name,f in fb.__dict__.items() if callable(f)]
    dic_tranchlois={}
    dic_nblois={}
    dic_parklois={}
    dic_dureelois={}        
    dic_retourdom={}
    
    data_journee['MOTIF_HDEP']=list(zip(data_journee['V2_MMOTIFDES'],data_journee['V2_MORIHDEP']))
    data_journee = data_journee.sort_values(['IDENT_IND','V2_MORIHDEP']).groupby(['IDENT_IND'])['MOTIF_HDEP'].apply(lambda x:list(x)).reset_index()
    nb_profil_mob = [len(data_journee[data_journee['MOTIF_HDEP'].map(f)]['MOTIF_HDEP'].values) for name,f in fb.__dict__.items() if callable(f)]
    nb_profil_mob = [x/sum(nb_profil_mob) for x in nb_profil_mob]
    profil_mob=pg.DiscreteDistribution(dict(zip([name for name,f in fb.__dict__.items() if callable(f)],nb_profil_mob)))
    print("     Catégorisation des journées types effectuée !")
    
    data_typjour=pd.DataFrame()
    data_typjour = df.copy()
    data_typjour['LIMOTIF']=list(data_typjour['V2_MMOTIFDES'])
    data_typjour = data_typjour.sort_values(['IDENT_IND','V2_MORIHDEP']).groupby(['IDENT_IND'])['LIMOTIF'].apply(lambda x:list(x)).reset_index()

    #On calcule différents paramètres dont on aura besoin pour modéliser les jours (une partie nombre loisirs/individu, type de jour, catégorisation des loisirs par leur tranche horaire)
    
    data_typjour['NBLOIS'] = data_typjour['LIMOTIF'].apply(compter_lois)
    
    data_typjour['TYPE_JOUR'] = data_journee['MOTIF_HDEP'].apply(trier_jour)
    
    data_typjour['NBLOIS_MAT']=data_journee['MOTIF_HDEP'].apply(compter_matin)
    data_typjour['NBLOIS_MIDI']=data_journee['MOTIF_HDEP'].apply(compter_midi)
    data_typjour['NBLOIS_SOIR']=data_journee['MOTIF_HDEP'].apply(compter_soir)
    data_typjour['NBLOIS_GRANDPARK'] = data_typjour['LIMOTIF'].apply(compter_grand_parking)
    data_typjour['NBLOIS_PETITPARK'] = data_typjour['LIMOTIF'].apply(compter_petit_parking)
    tranche_hor_lois = ['NBLOIS_MAT','NBLOIS_MIDI','NBLOIS_SOIR']
    park_lois = ['NBLOIS_GRANDPARK', 'NBLOIS_PETITPARK']
    data_typjour['RETDOM'] = data_typjour['LIMOTIF'].apply(retour_maison)
    df.loc[:,'TRANCHE'] = pd.Series(list(zip(df['V2_MMOTIFDES'],df['V2_MORIHDEP']))).apply(tranche_hor).values
   #bout de code permettant d'afficher un histogramme de répartition des trajets de loisir dans la journée en fonction du type de jour    
#
#    data_typjour['LOIS_HIST'] = data_journee['MOTIF_HDEP'].apply(hist_lois)
#    arr_hist = data_typjour[data_typjour['TYPE_JOUR']=='domtravailmidiloisirs']['LOIS_HIST'].values
#    hist_tot = np.zeros(24)
#    for x in arr_hist:
#        hist_tot = hist_tot + x
#    plt.bar(np.arange(24), hist_tot/sum(hist_tot))
    
   #Calcule les probas de loisirs selon les tranches horaires pour chaque type de jour
    for typ in typjour:     
        if "loisirs" in typ:
            nb_tranchlois = [data_typjour[data_typjour['TYPE_JOUR']==typ][x].sum() for x in tranche_hor_lois]
            nb_tranchlois = [x/sum(nb_tranchlois) for x in nb_tranchlois]
            dic_tranchlois[typ] = pg.DiscreteDistribution(dict(zip(['mat','midi','soir'],nb_tranchlois)))

    #Calcule les probas du nombre de loisirs pour chaque type de jour
    for typ in typjour:
        if "loisirs" in typ:
            nb_lois = data_typjour[data_typjour['TYPE_JOUR']==typ]['NBLOIS'].value_counts(normalize=True)
            nb_lois = nb_lois.drop(nb_lois[nb_lois<0.005].index)
            dic_nblois[typ] = pg.DiscreteDistribution(dict(zip(nb_lois.index,nb_lois.values/nb_lois.sum())))
#            print(dic_nblois[typ])
#    print(profil_lois_domlois)

    #Calcule la proportion de loisir avec petit ou grand parking pour chaque type de jour. la répartition est toujours 2/3 petits parking 1/3 grand quelque soit le type de jour
    df_loisindiv=df[['IDENT_IND','V2_DURACT', 'V2_MMOTIFDES','TRANCHE']].merge(data_typjour, left_on ='IDENT_IND', right_on = 'IDENT_IND', how='left')
    for typ in typjour:
        if "loisirs" in typ:
            dic_parklois[typ]={}
            for hor in ['mat','midi','soir']:
                nb_parklois = [df_loisindiv[(df_loisindiv['TYPE_JOUR']==typ) & (df_loisindiv['TRANCHE']==hor)][x].sum() for x in park_lois]
                nb_parklois = [x/sum(nb_parklois) for x in nb_parklois]
                dic_parklois[typ][hor] = pg.DiscreteDistribution(dict(zip(['gpark','ppark'],nb_parklois)))
    
    #Calcule la durée du loisir en fonction de son parking et dy type de jour. C'est selon une loi exponentielle pour les petits parkings et une log normale pour les grands parkings
    for i,typ in enumerate(typjour):
        if "loisirs" in typ:
            dic_dureelois[typ] = {}
            dur_ppark = df_loisindiv[(df_loisindiv['TYPE_JOUR']==typ) & (df_loisindiv['V2_MMOTIFDES'].apply(est_petit_parking)) & (df_loisindiv['V2_DURACT']>0) & (df_loisindiv['V2_DURACT']<301)]['V2_DURACT']
            dur_gpark = df_loisindiv[(df_loisindiv['TYPE_JOUR']==typ) & (df_loisindiv['V2_MMOTIFDES'].apply(est_grand_parking)) & (df_loisindiv['V2_DURACT']>0) & (df_loisindiv['V2_DURACT']<301)]['V2_DURACT']
            prob_gpark = pg.LogNormalDistribution(0,1)
            prob_gpark.fit(dur_gpark.values.flatten())
#            plt.figure(2*i)
#            n = plt.hist(dur_gpark.values, density=True, bins=60)
#            plt.plot(n[1], prob_gpark.probability(n[1]))
            dic_dureelois[typ]['gpark']=prob_gpark
            prob_ppark = pg.ExponentialDistribution(1)
            prob_ppark.fit(dur_ppark.values.flatten())
#            plt.figure(2*i+1)
#            n = plt.hist(dur_ppark.values, density=True, bins=60)
#            plt.plot(n[1], prob_ppark.probability(n[1]))
            dic_dureelois[typ]['ppark'] = prob_ppark
    
#    data_typjour=data_typjour.merge(df_gens[['IDENT_IND','V1_BTRAVT','V1_BTRAVHS','SITUA']], left_on='IDENT_IND', right_on='IDENT_IND', how='left')
    
    df_sortie = df.merge(data_typjour[['IDENT_IND', 'TYPE_JOUR', 'RETDOM']], left_on ='IDENT_IND', right_on = 'IDENT_IND', how='left')
#    print(data_typjour[data_typjour['TYPE_JOUR']==''])
    
    for typ in typjour:
        if 'loisirs' in typ:
            dat = data_typjour[data_typjour['TYPE_JOUR']==typ]['RETDOM']
            taux_retour = dat.sum()/dat[dat==0].count()
            dic_retourdom[typ] = pg.DiscreteDistribution(dict(zip([1,0],[taux_retour, 1-taux_retour])))
    return profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, df_sortie








def retour_maison(li):
    nbret = 0
    lois = False
    for i,x in enumerate(li):
        if x == 1.1 and lois:
            if i<len(li) - 1:
                nbret+=1
                lois = False
        elif x == 2 or x == 3:
            lois = True
        elif lois:
            lois = False
    return nbret

def compter_lois(liste):
    #compte le nombre de trajet vers un loisir dans la journée. fonction map
    nb=0
    for x in liste:
        if x == 2 or x == 3:
            nb+=1
    return nb

def trier_jour(liste):
    #renvoie le type de jour (domloisirs, domtravailmidi...). fonction map
    nom=''
    for name,f in fb.__dict__.items():
        if callable(f) and f(liste):
            nom=name
    return str(nom)

def compter_matin(li):
    nb=0
    for tu in li:
        if (math.floor(tu[0]) > 1 and math.floor(tu[0]) < 6) or (math.floor(tu[0])==7):
            if (pd.to_timedelta(tu[1]) >= pd.to_timedelta(7.5,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(10,unit='h')):
                nb+=1
    return nb


def compter_midi(li):
    nb=0
    for tu in li:
        if tu[0] == 2 or tu[0] == 3:
            if (pd.to_timedelta(tu[1]) >= pd.to_timedelta(11,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(14.5,unit='h')):
                nb+=1
    return nb

def hist_lois(li):
    #répartit les trajets de loisir selon leur horaire. sert à tracer un graphe de probabilité des trajets. fonction map 
    hist=np.zeros(24)
    for tu in li:
        if tu[0] == 2 or tu[0] == 3:
            hist[pd.to_timedelta(tu[1]).seconds//(3600)]+=1
    return hist

def compter_soir(li):
    nb=0
    for tu in li:
        if tu[0] == 2 or tu[0] == 3:
            if (pd.to_timedelta(tu[1]) >= pd.to_timedelta(15,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(23,unit='h')):
                nb+=1
    return nb

def tranche_hor(tu):
    (mot, hdep) = tu
    if mot in [2,3]:
        if (pd.to_timedelta(hdep) >= pd.to_timedelta(7.5,unit='h')) and (pd.to_timedelta(hdep) < pd.to_timedelta(10,unit='h')):
            return "mat"
        elif (pd.to_timedelta(hdep) >= pd.to_timedelta(11,unit='h')) and (pd.to_timedelta(hdep) < pd.to_timedelta(14.5,unit='h')):
            return "midi"
        elif (pd.to_timedelta(hdep) >= pd.to_timedelta(15,unit='h')) and (pd.to_timedelta(hdep) < pd.to_timedelta(23,unit='h')):
            return "soir"
        else:
            return "oupsi"
    else:
        return np.nan

def compter_grand_parking(li):
    return len([1 for x in li if x == 2])

def compter_petit_parking(li):
    return len([1 for x in li if x == 3 ])

def est_grand_parking(el):
    return el == 2

def est_petit_parking(el):
    return el == 3
#df = modele_jours_type(data_filt, data_indiv)