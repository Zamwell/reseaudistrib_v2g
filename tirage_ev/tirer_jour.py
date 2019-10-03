# -*- coding: utf-8 -*-
"""
A supprimer, juste utilisé pour creer un graphe
"""

import pandas as pd
import numpy as np
from modelisation_ev.utilitaire import trouv_break, flatten

    
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