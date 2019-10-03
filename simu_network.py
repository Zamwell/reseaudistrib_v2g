# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:17:39 2019

@author: Utilisateur
"""

import pandapower as pp
import pandapower.networks
from random import random
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

fig = plt.figure()
figou = plt.figure()
ax = fig.add_subplot(111, projection='3d')
axou = figou.add_subplot(111, projection ='3d')

net = pp.networks.create_dickert_lv_network(feeders_range='middle', customer = 'multiple')


x = np.arange(47)
xi = np.arange(45)
y = np.arange(10)
X,Y = np.meshgrid(x,y)
Xi,Yi = np.meshgrid(xi,y)
Z = np.zeros((len(y),len(x)))
W=np.zeros((len(y),len(xi)))

for i in range(len(y)):
    pp.runpp(net, calculate_voltage_angles=True)
    Z[i]=net.res_bus['vm_pu'].values
    W[i]=net.load.p_mw.values
    net.load.p_mw = net.load.p_mw.apply(lambda x: x + random()*x - 0.5*x)
ax.plot_surface(X, Y, Z,cmap=cm.viridis)
axou.plot_surface(Xi,Yi,W,cmap=cm.viridis)

def reg_q(u,p):
    """
    Renvoie la valeur de q de la loi Q=f(U) d'Enedis NOI-RES60E
    u = tension au noeud
    p = puissance max de l'install
    (régu en boucle fermée
    temps de réponse = 30s
    précision +/- 5% de Pmax)
    """
    if 0.9725 < u < 1.0375:
        return 0
    elif u <= 0.96:
        return -p*0.4
    elif u >= 1.05:
        return p*0.35
    elif 0.96 < u <= 0.9725:
        return -p*0.4*(0.9725-u)/0.0125
    elif 1.0375 <= u < 1.05:
        return p*0.35(u - 1.0375)/0.0125

def opti_agg(nb_ve, signal_freq, u_reseau):
    """
    L'agrégateur va optimiser le déploiement de ses VE participant à la régulation 
    de fréquence pour minimiser ses pertes dû au coût de réactif.
    """
    


horizon = np.arange(0,96)

for t in horizon:
    #K new loads
    #K tension
    #VVO sans EV
    #opti agg
    #VVO avec EV
    #K tension
    True