# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:11:42 2019

@author: Utilisateur
"""

import pandapower as pp
from construction_reseau.elements_evolutifs import def_charge, def_EV,def_EV_QReg, def_EV_base
from numpy.random import rand
from tirage_ev.tirage_modele import init_personne
import os
import pandas as pd

def creer_reseau():
    net = pp.create_empty_network()

    bus1 = pp.create_bus(net, name="HTB noeud", vn_kv=110,type="b")
    bus2 = pp.create_bus(net, name="HTB transfo", vn_kv=110, type ="n")
    bus3 = pp.create_bus(net, name="HTA transfo", vn_kv=20, type="n")
    bus4 = pp.create_bus(net, name = "barre HTA", vn_kv=20, type="b")
    bus5 = pp.create_bus(net, name = "noeud 1 HTA", vn_kv = 20, type = "b")
    bus6 = pp.create_bus(net, name = "noeud 2 HTA", vn_kv = 20, type = "b")
    bus7 = pp.create_bus(net, name = "noeud 3 HTA", vn_kv = 20, type = "b")
    bus8 = pp.create_bus(net, name = "noeud 4 HTA", vn_kv = 20, type = "b")
    bus9 = pp.create_bus(net, name = "noeud 5 HTA", vn_kv = 20, type = "b")
    bus10 = pp.create_bus(net, name = "noeud 6 HTA", vn_kv = 20, type = "b")
    bus11 = pp.create_bus(net, name = "noeud 7 HTA", vn_kv = 20, type = "b")
    bus12 = pp.create_bus(net, name = "noeud 8 HTA", vn_kv = 20, type = "b")
    bus13 = pp.create_bus(net, name = "noeud 9 HTA", vn_kv = 20, type = "b")

    pp.create_ext_grid(net, bus1, vm_pu = 1, va_degree = 50)

    trafo1 = pp.create_transformer(net, bus2, bus3, name="HTB/HTA transfo", std_type="40 MVA 110/20 kV")

    line1 = pp.create_line(net, bus4, bus5, length_km=1, std_type="NAYY 4x150 SE",  name="Line 1")
    line2 = pp.create_line(net, bus5, bus6, length_km=1, std_type="NAYY 4x150 SE",  name="Line 2")
    line3 = pp.create_line(net, bus6, bus7, length_km=1, std_type="NAYY 4x150 SE",  name="Line 3")
    line4 = pp.create_line(net, bus7, bus8, length_km=1, std_type="NAYY 4x150 SE",  name="Line 4")
    line5 = pp.create_line(net, bus4, bus9, length_km=1, std_type="NAYY 4x150 SE",  name="Line 5")
    line6 = pp.create_line(net, bus9, bus10, length_km=1, std_type="NAYY 4x150 SE",  name="Line 6")
    line7 = pp.create_line(net, bus10, bus11, length_km=1, std_type="NAYY 4x150 SE",  name="Line 7")
    line8 = pp.create_line(net, bus11, bus12, length_km=1, std_type="NAYY 4x150 SE",  name="Line 8")
    line9 = pp.create_line(net, bus12, bus13, length_km=1, std_type="NAYY 4x150 SE",  name="Line 9")

    sw1 = pp.create_switch(net, bus1, bus2, et="b", type="CB", closed=True)
    sw2 = pp.create_switch(net, bus3, bus4, et="b", type="CB", closed=True)

    pp.create_load(net, bus5, p_mw=3, q_mvar=0.5, name="load1")
    pp.create_load(net, bus6, p_mw=3, q_mvar=0.5, scaling=1, name="load2")
    pp.create_load(net, bus7, p_mw=3, q_mvar=0.5, scaling=1, name="load3")
    pp.create_load(net, bus8, p_mw=3, q_mvar=0.5, scaling=1, name="load4")
    pp.create_load(net, bus9, p_mw=3, q_mvar=0.5, scaling=1, name="load5")
    pp.create_load(net, bus10, p_mw=3, q_mvar=0.5, scaling=1, name="load6")
    pp.create_load(net, bus11, p_mw=3, q_mvar=0.5, scaling=1, name="load7")
    pp.create_load(net, bus12, p_mw=3, q_mvar=0.5, scaling=1, name="load8")
    pp.create_load(net, bus13, p_mw=3, q_mvar=0.5, scaling=1, name="load9")

    pp.create_sgen(net, bus7, p_mw=2, q_mvar=-0.5, name="static generator", type="wind")

    return net

def evol_charge(net, df, pmax):
    for i in range(9):
        def_charge(net,i, df, pmax)

def deploiement_EV(net,dic_param_trajets, profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, taux_penet = 0.30, p_evse_mw = 0.01, k_flotte = False):
    try:
        if  k_flotte == True:
            raise UserWarning("")
        net_flotte = pp.from_pickle(os.path.join("construction_reseau","data","flotte.p"))
        net.storage = net_flotte.storage.copy()
        for control in net_flotte.controller.iterrows():
            control[1].controller.net = net
        net_flotte.controller['name'] = net_flotte.controller.controller.apply(lambda x : str(x))
        net.controller = pd.concat([net.controller, net_flotte.controller[net_flotte.controller.name.str.contains('EV')].drop(['name'],axis=1)], ignore_index = True)
    except UserWarning:
        print("Calcul de la flotte...")
        nb_ev_fin = 0
        for x in net.load.itertuples():
            bus = x[2]
            p_noeud = x[3]
            nb_ev_max = int(p_noeud / 0.02)
            for i in range(nb_ev_max):
                if rand() <= taux_penet:
                    per = init_personne(dic_param_trajets, profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom)
                    def_EV_base(net, bus, per.creer_df(), per)
                    nb_ev_fin += 1
        pp.to_pickle(net,os.path.join("construction_reseau","data","flotte.p"))
        print(nb_ev_fin)

def deploiement_EV_freqreg(net,dic_param_trajets, profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, df_freq, taux_penet = 0.30, p_evse_mw = 0.01, k_flotte = False):
    try:
        if  k_flotte == True:
            raise UserWarning("")
        net_flotte = pp.from_pickle(os.path.join("construction_reseau","data","flotte.p"))
        net.storage = net_flotte.storage.copy()
        for control in net_flotte.controller.iterrows():
            control[1].controller.net = net
        net_flotte.controller['name'] = net_flotte.controller.controller.apply(lambda x : str(x))
        net.controller = pd.concat([net.controller, net_flotte.controller[net_flotte.controller.name.str.contains('EV')].drop(['name'],axis=1)], ignore_index = True)
    except UserWarning:
        print("Calcul de la flotte...")
        nb_ev_fin = 0
        for x in net.load.itertuples():
            bus = x[2]
            p_noeud = x[3]
            nb_ev_max = int(p_noeud / 0.02)
            for i in range(nb_ev_max):
                if rand() <= taux_penet:
                    per = init_personne(dic_param_trajets, profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom)
                    if rand() <= 0.2:
                        def_EV_QReg(net, bus, per.creer_df(), per)
                    else:
                         def_EV(net, bus, pd.concat([per.creer_df(), df_freq],axis = 1), per)
                    nb_ev_fin += 1
        pp.to_pickle(net,os.path.join("construction_reseau","data","flotte.p"))
        print(nb_ev_fin)
        
