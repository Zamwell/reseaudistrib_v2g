# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 14:15:22 2019

@author: Utilisateur
"""

from tirage_ev.tirage_modele import creer_flotte, graphe_presence_flotte
import os
import pickle

read_data_file = os.path.join("", "data_mod", "var.pkl")

with open(read_data_file, 'rb') as f:
    dic_var = pickle.load(f)

profil_mob = dic_var["profil_mob"]
dic_param_trajets = dic_var["dic_param_trajets"]
dic_nblois = dic_var["dic_nblois"]
dic_tranchlois = dic_var["dic_tranchlois"]
dic_parklois = dic_var["dic_parklois"]
dic_dureelois = dic_var["dic_dureelois"]
dic_retourdom = dic_var["dic_retourdom"]

flotte,test = creer_flotte(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, 400)
#graphe_presence_flotte(test)