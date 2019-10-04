# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:41:07 2019

@author: Utilisateur
"""

from modelisation_ev.initialisation_modele import initialise_var
import config

"""df_dep, df_indiv = preparer_data()
    
dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois,dic_parklois, dic_dureelois, dic_retourdom = utilisation_data(df_dep, df_indiv)
"""

config.init()

dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom = initialise_var()



with open(os.path.join("data_mod","var.pkl"), "wb") as f:
    f.write(pickle.dumps(dic))


#config.dic_param_trajets = dic_param_trajets
#config.profil_mob = profil_mob
#config.dic_nblois = dic_nblois
#config.dic_tranchlois = dic_tranchlois
#config.dic_parklois = dic_parklois
#config.dic_dureelois = dic_dureelois
#config.dic_retourdom = dic_retourdom