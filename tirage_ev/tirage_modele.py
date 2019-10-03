# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 11:51:41 2019

@author: Utilisateur
"""

import numpy as np
import matplotlib.pyplot as plt
from tirage_ev.electric_vehicle import Personne
from tirage_ev.tirer_jour import presence_jour

def creer_flotte(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, nb_ev):
    pers=[]
    test=[]
    for i in range(nb_ev):
        typ = profil_mob.sample()
        if 'travail' in typ:
            dist = dic_param_trajets[typ]['travmat'][0].sample()
        else:
            dist = -1
        pers.append(Personne(typ,dist))
    for j in range(5):
        test.append([])
        for per in pers:
            li_traj = per.tirer_mobilite_jour_semaine(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom)
            if li_traj != None:
                test[j].append(li_traj)
    return pers, test
    
def init_personne(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom):
    journee_vide = True
    while journee_vide:
        typ = profil_mob.sample()
        if 'travail' in typ:
            dist = dic_param_trajets[typ]['travmat'][0].sample()
        else:
            dist = -1
        per = Personne(typ,dist)
        li = per.tirer_mobilite_jour_semaine(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom)
        journee_vide = (li == [])
    return per

def graphe_presence_flotte(test):    
    arr_hist = np.zeros([5,24*4])
    for li_traj in test[0]:
        arr_hist= arr_hist + presence_jour(li_traj)
    for j in range(1,5):
        arr_hist_j=np.zeros([5,24*4])
        for li_traj in test[j]:
            arr_hist_j = arr_hist_j + presence_jour(li_traj)
        arr_hist = np.concatenate((arr_hist,arr_hist_j),axis=1)
    
    for j in range(5):
        plt.plot(np.arange(24*4*5),arr_hist[j]/len(test[0]))
    
    plt.legend(['Domicile','Travail','Grand Parking','Petit parking','Déplacement'])