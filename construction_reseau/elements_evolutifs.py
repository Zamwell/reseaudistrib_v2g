# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:19:04 2019

@author: Utilisateur
"""
import pandas as pd
import pandapower as pp
import pandapower.timeseries as pt
from pandapower.control import ConstControl
from pandapower.control.controller.storage.ElectricVehicleControl import EVControl
from pandapower.control.controller.storage.ElectricVehicleQRegControl import EVQRegControl
from pandapower.control.controller.prod.ProdQRegulatedControl import ProdQRegulatedControl

def def_charge(net, index, df_scale, Pmax):
    df = pd.DataFrame()
    df['charge'] = df_scale['scale'].values * Pmax
    ds = pt.DFData(df)
    ConstControl(net, element="load", variable = 'p_mw', element_index = index, data_source = ds, set_q_from_cosphi = False, profile_name="charge")
    return net

def def_EV(net, bus, df, efficiency = 1):
    ev = pp.create_storage(net, bus, p_mw = 0, max_e_mwh = 0.5, name = "ev bus"+str(bus), soc_percent=0.5)
    ds = pt.DFData(df)
    EVControl(net, gid = ev, data_source=ds, efficiency = efficiency)
    return net

def def_EV_QReg(net, bus, df, efficiency = 1):
    ev = pp.create_storage(net, bus, p_mw = 0, max_e_mwh = 0.5, name = "ev bus"+str(bus), soc_percent=0.5)
    ds = pt.DFData(df)
    EVQRegControl(net, gid = ev, data_source=ds, efficiency = efficiency)


def def_prod(net, index, df_scale, Pmax):
    df = pd.DataFrame()
    df['prod'] = df_scale['scale'].values * Pmax
    ds = pt.DFData(df)
    ConstControl(net, element="sgen", variable = 'p_mw', element_index = index, data_source = ds, profile_name="prod")
    
def prod_regulee(net, index, df_scale, pmax):
    df = pd.DataFrame()
    df['prod'] = df_scale['scale'].values * pmax
    ds = pt.DFData(df)
    ProdQRegulatedControl(net, gid = index, data_source=ds, pmax = pmax)
    