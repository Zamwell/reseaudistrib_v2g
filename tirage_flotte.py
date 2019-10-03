# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 14:15:22 2019

@author: Utilisateur
"""

from modelisation_ev.tirage_modele import creer_flotte, graphe_presence_flotte


flotte,test = creer_flotte(dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, 100)
#graphe_presence_flotte(test)