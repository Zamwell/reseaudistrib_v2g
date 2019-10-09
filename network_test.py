# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:51:44 2019

@author: Utilisateur
"""

import pandas as pd
import pandapower.control as pc
from pandapower.timeseries import OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
import os
from construction_reseau.creation_reseau import creer_reseau, evol_charge, deploiement_EV, deploiement_EV_freqreg
from construction_reseau.elements_evolutifs import def_charge, def_EV, def_EV_QReg, def_prod, prod_regulee
from exploitation_res.graphiques import plot_graph, plot_pertes, comp_pertes, plot_soc_noeud, plot_ajout_charge
from exploitation_res.calculs import calc_pertes, calc_ecart_tension
from construction_reseau.frequence_reseau import creer_df_freq
from pandapower.control.controller.storage.ElectricVehicleControl import EVControl
from pandapower.control.controller.storage.ElectricVehicleQRegControl import EVQRegControl
import pickle

net = creer_reseau()

df_charge = pd.read_csv("scale_timeserie.csv", sep=";", encoding="ISO-8859-1", low_memory = False, index_col= "time")
df_prod = pd.read_csv("prod_scale_timeserie.csv", sep=";", encoding="ISO-8859-1", low_memory = False, index_col= "time")
df_freq = pd.read_csv("freq_timeserie.csv", sep=";", encoding="ISO-8859-1", low_memory = False, index_col= "time")

evol_charge(net, df_charge, pmax = 3)

prod_regulee(net, 0, df_prod, 2)

net.trafo.tap_step_percent = 0.625
net.trafo.tap_pos = -5
#cont = pc.controller.trafo.DiscreteTapControl.DiscreteTapControl(net, 0, 0.995, 1.05)

def create_output_writer(net, time_steps, output_dir):
    ow = OutputWriter(net, time_steps, output_path=output_dir, output_file_type=".csv")
    # these variables are saved to the harddisk after / during the time series loop
    ow.log_variable('res_bus', 'p_mw')
    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('storage','p_mw')
    ow.log_variable('res_line', 'loading_percent')
    ow.log_variable('res_line', 'i_ka')
    ow.log_variable('storage', 'soc_percent')
    ow.log_variable('res_line', 'pl_mw')
    ow.log_variable('res_sgen', 'q_mvar')
    return ow



time_steps = range(0,24*4-1)

output_dir = os.path.join("", "res_timeseries")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

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


ow = create_output_writer(net, time_steps, output_dir=output_dir)
 
 # 5. the main time series function
run_timeseries(net, time_steps, output_writer=ow)
 
ecart_base = calc_ecart_tension(output_dir, drop = [0,1,2,3])
 
 
 # line loading results
 #plot_graph(output_dir, "res_line", "loading_percent.xls", "line loading [%]","Line Loading")
 
 # load results
plot_graph(output_dir, "res_bus", "p_mw.csv","P [MW]", "Bus Loads", drop = [0,1,2,3,4,5] )

 # voltage results
plot_graph(output_dir, "res_bus", "vm_pu.csv", "voltage mag. [p.u.]","Voltage Magnitude")

plot_graph(output_dir, "res_sgen","q_mvar.csv", "Q [MVAr]", "Prod Reactive Power")
 
df_base = calc_pertes(output_dir)
 
df_frequence = creer_df_freq(df_freq)
evs = []
net_base = net.deepcopy()

#for per in flotte:
#    if len(evs)>4:
#        break
#    if per.journee.li_traj != []:
#        evs.append(pd.concat([per.creer_df(),df_frequence], axis = 1))
#
#for j in range(len(evs)):
#    def_EV(net,j+8,evs[j], efficiency = 0.9)

deploiement_EV_freqreg(net,dic_param_trajets, profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, df_frequence)


ow = create_output_writer(net, time_steps, output_dir=output_dir)
    
run_timeseries(net, time_steps, output_writer=ow)

ecart_ev = calc_ecart_tension(output_dir, drop = [0,1,2,3])
print(ecart_ev)



#for i in range(len(evs)):
#    net.storage = net.storage.iloc[0:0]
#    mask_control = net.controller.controller.apply(lambda x : str(x))
#    net.controller = net.controller[~ ( (mask_control.values == "EVControl") | (mask_control.values == "EVQRegControl"))].copy()
#    for j in range(len(evs)-1):
#        def_EV(net,(j+i+1)%5+8,evs[(j+i+1) % 5], efficiency = 0.9)
#    def_EV_QReg(net, i+8, evs[i], efficiency = 0.9)
#        
#    ow = create_output_writer(net, time_steps, output_dir=output_dir)
#    
#    run_timeseries(net, time_steps, output_writer=ow)
#    
#    ecart_encours = calc_ecart_tension(output_dir, drop = [0,1,2,3])
#    print(ecart_encours)
#    if ecart_encours < ecart_ev:
#        conf_opti = i
#        ecart_ev = ecart_encours


plot_graph(output_dir, "res_bus", "vm_pu.csv", "voltage mag. [p.u.]","Voltage Magnitude")


df_ev = calc_pertes(output_dir)


plot_ajout_charge(output_dir, "storage", "p_mw.csv", net.storage)

#load soc
#plot_graph(output_dir, "storage", "soc_percent.csv","State Of Charge [%]", "Batteries SOC")

comp_pertes(df_base, df_ev)

#print(ecart_ev)
#print(conf_opti)
