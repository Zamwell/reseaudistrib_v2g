# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 15:00:42 2019

@author: Utilisateur
"""
from modelisation_ev.utilitaire import encadrer
import pandas as pd

def som_freq(df_freq, tdep):
    """
    Renvoie l'intégrale de la différence de fréquence à 50Hz sur 15 minutes
    """
    li_freq = df_freq['freq'].values
    som = 0
    for freq in li_freq[tdep:tdep + 6*15]:
        som += encadrer(-0.2,freq - 50,0.2)/0.2
    return som/(6*15)

def creer_df_freq(df_freq):
    """
    Créer une dataframe de l'intégrale de la diff de fréquence à 50Hz toutes les 15 minutes
    """
    li_freq= []
    df = pd.DataFrame()
    for i in range(24*4):
        li_freq.append(som_freq(df_freq, (6*15)*i))
    df['freq'] = li_freq
    return df