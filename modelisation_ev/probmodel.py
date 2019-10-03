# -*- coding: utf-8 -*-
"""
Created on Fri May  3 18:28:30 2019

@author: Any
"""

import pomegranate as pg
import pandas as pd
import numpy as np
from scipy.special import erfinv
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

def probparam(dfent,typ,hdeb,hfin,mot):
    #Pourquoi pas rajouter un nom en paramètre et le dico pour ajouter au dico le modèle
    df=dfent.copy()
    df=df[(df['V2_MORIHDEP']<=pd.to_timedelta(hfin,unit='h')) 
    & (df['V2_MORIHDEP']>=pd.to_timedelta(hdeb,unit='h')) 
    & (np.floor(df['V2_MMOTIFDES'])==mot)
    & (df['TYPE_JOUR'] ==typ)]
    
    prob_dist = pg.LogNormalDistribution(0, 1)
    prob_dist.fit(df['V2_MDISTTOT'].values.flatten(),
            weights=df['POIDS_JOUR'].values.flatten())
    pg_mu, pg_sigma = prob_dist.parameters
    
    Q = [np.exp(pg_mu + np.sqrt(2*pg_sigma)*erfinv(2*x-1)) for x in [0.25, 0.5, 0.75]]
    Q.append(100)
    Q.insert(0, 0)
    prob_dist
    prob_quartdist = {}
    for i in range(0, len(Q)-1):
        df_dist = df[(df['V2_MDISTTOT'] <= Q[i+1])
                & (df['V2_MDISTTOT'] > Q[i])]
        df_dur = df_dist.copy()

        df_dur['V2_DUREE']=pd.to_timedelta(df_dur['V2_DUREE'],
                unit='Min').dt.round('1Min').dt.total_seconds()//60
        prob_dist_dur = pg.LogNormalDistribution.from_samples(
                df_dur['V2_DUREE'].values.flatten(),
                weights=df_dur['POIDS_JOUR'].values.
                flatten())
#        df_dur=df_dur.groupby(by=['V2_DUREE'], as_index=False)['POIDS_JOUR'].sum()
#        plt.plot(df_dur['V2_DUREE'].values.flatten(),df_dur['POIDS_JOUR'].values.flatten()/(df_dur['POIDS_JOUR'].sum()),df_dur['V2_DUREE'].values.flatten(),prob_dist_dur.probability(df_dur['V2_DUREE'].values.flatten()))
#        plt.show()
        del df_dur
        df_hdep = df_dist.copy()
        df_hdep['V2_MORIHDEP']=df_hdep['V2_MORIHDEP'].dt.round('15Min')
        df_hdep=df_hdep.groupby(by=['V2_MORIHDEP'],as_index=False)['POIDS_JOUR'].sum()
        df_hdep = df_hdep.sort_values(['V2_MORIHDEP'])
        prob_dist_hdep = pg.DiscreteDistribution(dict(zip(df_hdep['V2_MORIHDEP'],df_hdep['POIDS_JOUR'].values.flatten()/(df_hdep['POIDS_JOUR'].sum()))))
#        prob_test = pg.GaussianKernelDensity()
#        prob_test.fit(df_dist['V2_MORIHDEP'].dt.total_seconds()/60)
#        n =plt.hist(df_dist['V2_MORIHDEP'].dt.total_seconds()/60, density = True , bins = (hfin - hdeb)*4)
#        plt.plot(n[1],prob_test.probability(n[1]))
#        plt.show()
#        print(df_dist['V2_MORIHDEP'].count())
        prob_quartdist[(Q[i],Q[i+1])] = (prob_dist_dur,prob_dist_hdep)
    return (prob_dist,prob_quartdist)

def probglob(dfent):
    df=dfent.copy()
    df['V2_DUREE'] = pd.to_timedelta(df['V2_DUREE'], unit='Min').dt.round('1Min').dt.total_seconds()//60
    df=df[df['V2_DUREE']<200].copy()
    prob_dist = pg.LogNormalDistribution(0,1)
    prob_dist.fit(df['V2_MDISTTOT'].values.flatten(),
            weights=df['POIDS_JOUR'].values.flatten())
    prob_dur = pg.LogNormalDistribution.from_samples(
                df['V2_DUREE'].values.flatten(),
                weights=df['POIDS_JOUR'].values.
                flatten())
#    df=df.groupby(by=['V2_DUREE'], as_index=False)['POIDS_JOUR'].sum()
#    plt.plot(df['V2_DUREE'].values.flatten(),df['POIDS_JOUR'].values.flatten()/(df['POIDS_JOUR'].sum()),df['V2_DUREE'].values.flatten(),prob_dur.probability(df['V2_DUREE'].values.flatten()))
#    plt.show()
    return prob_dist, prob_dur

def cat_spatiale_trajets(prob_dist,prob_duree, data, li_spat):
    df = data.copy()
    df['V2_DUREE'] = pd.to_timedelta(df['V2_DUREE'], unit='Min').dt.round('1Min').dt.total_seconds()//60
    df=df[(df['V2_DUREE']<200) & (np.floor(df['V2_MMOTIFDES']) == 9) & (df['V2_MORICOM_MDESCOM_indicUU'] == 1)].copy()
    colors = cm.winter(np.linspace(0, 1, len(li_spat)))
    colors_outli = cm.inferno(np.linspace(0,1,len(li_spat)))
    li_co = {}
    for i in range(len(li_spat)):
#        sprint(li_spat[i])
        if df[df['SPATIAL']==i]['V2_DUREE'].count()!= 0:
            df_filt = df[df['SPATIAL']==i].copy()
            te = sm.OLS(df_filt['V2_MDISTTOT'].values,df_filt['V2_DUREE'].values.reshape(-1,1))
            res = te.fit()
            influ = res.get_influence()
            (cook,p) = influ.cooks_distance
            df_filt['COOK'] = cook
            cook_outlier = [(df_filt['V2_DUREE'].values[o],df_filt['V2_MDISTTOT'].values[o]) for o,t in enumerate(cook) if t>4/len(cook)]
            print(cook_outlier)
            plt.scatter(df_filt[df_filt['COOK']<=8/len(cook)]['V2_DUREE'],df_filt[df_filt['COOK']<=8/len(cook)]['V2_MDISTTOT'],color = colors[i])
            plt.plot(df_filt['V2_DUREE'],res.predict(df_filt['V2_DUREE'].values))
            plt.scatter(df_filt[df_filt['COOK']>8/len(cook)]['V2_DUREE'],df_filt[df_filt['COOK']>8/len(cook)]['V2_MDISTTOT'],color = colors_outli[i])
            modele_sans_outlier = sm.OLS(df_filt[df_filt['COOK']<=4/len(cook)]['V2_MDISTTOT'].values,df_filt[df_filt['COOK']<=4/len(cook)]['V2_DUREE'].values.reshape(-1,1))
            res_ss_outli = modele_sans_outlier.fit()
            plt.plot(df_filt['V2_DUREE'],res_ss_outli.predict(df_filt['V2_DUREE'].values))
            plt.show()
            li_co[li_spat[i]] = [np.round(res.params[0]*60,decimals=1),np.round(res.rsquared*100,decimals = 2),df[df['SPATIAL']==i]['V2_MDISTTOT'].count()]
            print(np.round(res.rsquared*100,decimals = 2),np.round(res_ss_outli.rsquared*100,decimals = 2))
        else:
            li_co[li_spat[i]] = [0]
    print(li_co)
#    plt.scatter(df[df['V2_MORICOM_MDESCOM_indicUU']==1]['V2_MDISTTOT'],df[df['V2_MORICOM_MDESCOM_indicUU']==1]['V2_DUREE'],color = 'm')
    return li_co

def cat_spatiale_trajets_zhu(prob_dist,prob_duree, data, li_spat):
    df = data.copy()
    df['V2_DUREE'] = pd.to_timedelta(df['V2_DUREE'], unit='Min').dt.round('1Min').dt.total_seconds()//60
    df=df[(df['V2_DUREE']<200) & (np.floor(df['V2_MMOTIFDES']) == 2) & (df['V2_MORICOM_MDESCOM_indicUU'] == 1)].copy()
    colors = cm.winter(np.linspace(0, 1, len(li_spat)))
    colors_outli = cm.inferno(np.linspace(0,1,len(li_spat)))
    li_co = {}
    for i in range(len(li_spat)):
#        sprint(li_spat[i])
        if df[df['SPATIAL_ZHU']==i]['V2_DUREE'].count()!= 0:
            df_filt = df[df['SPATIAL_ZHU']==i].copy()
            plt.scatter(df_filt['V2_DUREE'].values,df_filt['V2_MDISTTOT'])
            te = sm.OLS(df_filt['V2_MDISTTOT'].values,df_filt['V2_DUREE'].values.reshape(-1,1))
            res = te.fit()
            influ = res.get_influence()
            (cook,p) = influ.cooks_distance
            df_filt['COOK'] = cook
            cook_outlier = [(df_filt['V2_DUREE'].values[o],df_filt['V2_MDISTTOT'].values[o]) for o,t in enumerate(cook) if t>4/len(cook)]
#            print(cook_outlier)
#            plt.scatter(df_filt[df_filt['COOK']<=8/len(cook)]['V2_DUREE'],df_filt[df_filt['COOK']<=8/len(cook)]['V2_MDISTTOT'],color = colors[i])
#            plt.plot(df_filt['V2_DUREE'],res.predict(df_filt['V2_DUREE'].values))
#            plt.scatter(df_filt[df_filt['COOK']>8/len(cook)]['V2_DUREE'],df_filt[df_filt['COOK']>8/len(cook)]['V2_MDISTTOT'],color = colors_outli[i])
            if len(cook_outlier)>0:
                modele_sans_outlier = sm.OLS(df_filt[df_filt['COOK']<=4/len(cook)]['V2_MDISTTOT'].values,df_filt[df_filt['COOK']<=4/len(cook)]['V2_DUREE'].values.reshape(-1,1))
                res_ss_outli = modele_sans_outlier.fit()
#            plt.plot(df_filt['V2_DUREE'],res_ss_outli.predict(df_filt['V2_DUREE'].values))
#            plt.show()
            li_co[li_spat[i]] = [np.round(res.params[0]*60,decimals=1),np.round(res.rsquared*100,decimals = 2),df_filt['V2_MDISTTOT'].count()]
            #print(np.round(res.rsquared*100,decimals = 2),np.round(res_ss_outli.rsquared*100,decimals = 2))
        else:
            li_co[li_spat[i]] = [0]
    plt.show()
    print(li_co)
#    plt.scatter(df[df['V2_MORICOM_MDESCOM_indicUU']==1]['V2_MDISTTOT'],df[df['V2_MORICOM_MDESCOM_indicUU']==1]['V2_DUREE'],color = 'm')
    return li_co