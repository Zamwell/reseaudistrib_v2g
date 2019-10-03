# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 16:09:42 2019

@author: Utilisateur
"""

import pandas as pd
import numpy as np
from modelisation_ev.utilitaire import trouv_break, flatten

def tirer_jour(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom):
    typ = profil_mob.sample()
    trajets_jour=[]
    dic_oblig = {'travail' : ['travmat','domsoir'], 'midi' : ['dommidi','travmidi']}
    if 'loisir' in typ:
        nb_lois = dic_nblois[typ].sample()
        lois=[]
        for i in range(nb_lois):
            tranch = dic_tranchlois[typ].sample()
            typ_lois = dic_parklois[typ][tranch].sample()
            duree_lois = dic_dureelois[typ][typ_lois].sample()
            lois.append((tranch,typ_lois,duree_lois))
        lois.sort()
        for typ_traj, modele_typ_traj in dic_param_trajets[typ].items():
            for (tr,ty,dur) in lois:
                if tr in typ_traj and ty in typ_traj:
                    param_traj = flatten([tirer_trajet(modele_typ_traj),typ_traj])
                    trajets_jour.append(trajet(*param_traj))
    for mot_cle, trajets_oblig in dic_oblig.items():
        if mot_cle in typ:
            for traj in trajets_oblig:
                trajets_jour.append(trajet(*flatten([tirer_trajet(dic_param_trajets[typ][traj]),traj])))
    trajets_jour.sort()
    if not('dom' in trajets_jour[-1].motif):
        for hor in ['mat','midi','soir']:
            if hor in trajets_jour[-1].motif:
                trajets_jour.append(trajet(*flatten([tirer_trajet(dic_param_trajets[typ]['dom'+hor]),'dom'+hor])))
#    print(trajets_jour[-1])
    if is_journee_coherente(trajets_jour):
        return trajets_jour
    else:
        return None
        
    
    
            
    
def presence_jour(li_traj):
    """
    Sert à faire le graphe de répartition de la présence des gens dans l'espace
    """
    li_pres = np.zeros([5,24*4])
    emplacement = 0
    hdepprec = 0
    for traj in li_traj:
        for j in range(hdepprec,int(np.round(traj.hdep.seconds/60/15))):
            li_pres[emplacement][j]+=1
        for j in range(int(np.round(traj.hdep.seconds/60/15)),int(np.round(traj.hdep.seconds/60/15) + np.round(traj.duree/15))):
            if j < 96:
                li_pres[4][j]+=1
            else:                
                print((traj.hdep),np.round(traj.duree/15))
                print(int(np.round(traj.hdep.seconds/60/15)),int(np.round(traj.hdep.seconds/60/15) + np.round(traj.duree/15)))
        hdepprec = int(np.round(traj.hdep.seconds/60/15) + np.round(traj.duree/15))
        if 'trav' in traj.motif:
            emplacement = 1
        elif 'ppark' in traj.motif:
            emplacement = 3
        elif 'gpark' in traj.motif:
            emplacement = 2
        else:
            emplacement = 0
    for j in range(hdepprec,24*4):
        li_pres[0][j]+=1
    return li_pres