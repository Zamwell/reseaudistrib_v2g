# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 16:00:15 2019

@author: Utilisateur
"""
import pandas as pd
import numpy as np
from modelisation_ev.utilitaire import trouv_break

class Trajet:
    def __init__(self, dic_modele, dist = -1, mot = ""):
        (prob_dist, prob_quartdist) = dic_modele
        if dist < 0:
            dist = np.round(prob_dist.sample(),decimals=1)
        while dist == 0:
            dist = np.round(prob_dist.sample(),decimals=1)
        while dist >=100:
            dist = 99.9
        for interv_dist,prob_quart in prob_quartdist.items():
            if interv_dist[0] < dist <= interv_dist[1]:
                duree_traj = np.round(prob_quart[0].sample())
                hdep = prob_quart[1].sample()
                break
        else:
            print("dans aucun quartile")
            print(dist)
        self.hdep = hdep
        self.dist = dist
        self.duree = duree_traj
        self.motif = mot

        
    def __lt__(self, other):
        return self.hdep < other.hdep

    def __str__(self):
        return "({}, {}, {}, {})".format(self.hdep, self.dist, self.duree, self.motif)
    
    def __repr__(self):
        return "({}:{}, {}, {}, {})".format(int(self.hdep.seconds//3600),int((self.hdep.seconds % 3600)//60), self.dist, self.duree, self.motif)

class Journee:
    def __init__(self, typ, dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom, dist_trav):
        """
        Renvoie une liste de trajet correspondant à une journée de déplacement
        
        """
        #Pour ajouter de l'aléatoire, on a 15% de chance que la journée ne corresponde pas forcément à la journée type habituelle

            
        trajets_jour=[]
        dic_oblig = {'travail' : ['travmat','domsoir'], 'midi' : ['dommidi','travmidi']}
        
        #On gère déjà les trajets de loisir (leur nombre et leur caractéristiques)
        if 'loisir' in typ:
            nb_lois = dic_nblois[typ].sample()
            lois=[]
            for i in range(nb_lois):
                tranch = dic_tranchlois[typ].sample()
                typ_lois = dic_parklois[typ][tranch].sample()
                duree_lois = dic_dureelois[typ][typ_lois].sample()
                lois.append((tranch,typ_lois,duree_lois))
            lois.sort()
            for typ_traj, modele_typ_traj in dic_param_trajets[typ].items():
                for (tr,ty,dur) in lois:
                    if tr in typ_traj and ty in typ_traj:
                        trajets_jour.append(Trajet(modele_typ_traj, mot = typ_traj))
        #On gère ensuite les trajets obligatoires (= le travail)
        for mot_cle, trajets_oblig in dic_oblig.items():
            if mot_cle in typ:
                for traj in trajets_oblig:
                    trajets_jour.append(Trajet(dic_param_trajets[typ][traj],dist_trav,traj))
        #On classe les trajets en fonction de l'heure de départ
        trajets_jour.sort()
        
        #On vérifie qu'on rentre à la maison au dernier trajet
        if not('dom' in trajets_jour[-1].motif):
            for hor in ['mat','midi','soir']:
                if hor in trajets_jour[-1].motif:
                    trajets_jour.append(Trajet(dic_param_trajets[typ]['dom'+hor],mot = 'dom'+hor))
    #    print(trajets_jour[-1])
        if self.is_journee_coherente(trajets_jour):
            self.li_traj = trajets_jour
        else:
            self.li_traj = []
        self.socmin = None
        
    def __iter__(self):
        return iter(self.li_traj)


    def is_journee_coherente(self, li_traj):
        hdepprec= pd.to_timedelta(0, unit = 'h')
        dureeprec = pd.to_timedelta(0, unit = 'm')
        for traj in li_traj:
            if traj.hdep + pd.to_timedelta(traj.duree, unit='m') < hdepprec + dureeprec:
                return False
            else:
                hdepprec = traj.hdep
                dureeprec = pd.to_timedelta(traj.duree, unit = 'm')
        return True

class Personne:
    def __init__(self, typ_jour_semaine, dist_trav = -1):
        self.type_jour_semaine = typ_jour_semaine
        self.dist_trav = dist_trav
        self.cap_bat = 0.050 #MWh
        self.nrj_km = 0.0002 #MWh par km
        self.journee = []
        self.puis_rech = 0.01 #MW
        self.efficiency = 0.9
    
    def tirer_mobilite_jour_semaine(self, dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom):
        if np.random.rand()>0.85:
            typ = profil_mob.sample()
        else:
            typ = self.type_jour_semaine
        self.journee = Journee(typ, dic_param_trajets,profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, dic_retourdom,self.dist_trav)
        return self.journee
    
    def creer_df(self):
        """
        Crée une dataframe avec l'endroit où la voiture se trouve + l'état de charge du véhicule (HORS RECHARGE)
        """
        df = pd.DataFrame()
        pres_jour = []
        nrj_jour = np.ones(24*4) * 0
        emplacement = 0
        hdepprec = 0
        for traj in self.journee:
            for j in range(hdepprec,int(np.round(traj.hdep.seconds/60/15))):
                pres_jour.append(emplacement)
            for j in range(int(np.round(traj.hdep.seconds/60/15)),int(np.round(traj.hdep.seconds/60/15) + np.round(traj.duree/15))):
                if j < 96:
                    pres_jour.append(4)
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
            pres_jour.append(0)
        
        for traj in self.journee:
            if np.round(traj.duree/15) == 0:
                nrj_jour[int(np.round(traj.hdep.seconds/60/15))] =  self.nrj_km * traj.dist
            else:
                for j in range(int(np.round(traj.hdep.seconds/60/15)),int(np.round(traj.hdep.seconds/60/15) + np.round(traj.duree/15))+1):
                    if j < 96:
                        nrj_jour[j] = self.nrj_km * traj.dist / (np.round(traj.duree/15)+1)
                    else:
                        print("A corriger")       
        df['emplacement'] = pres_jour[:96]
        df['nrj_utilisee'] = nrj_jour[:96]
        
        df['socmin'] = self.def_socmin(pres_jour,nrj_jour)
        return df
    
    def def_socmin(self,pres_jour,nrj_jour):
        socmin = np.ones(24*4)*0.2
        tprec=0
        soc_dep = 0
        temps_charge = 0
        while trouv_break(pres_jour, tprec, 0) != None:
            tdep = trouv_break(pres_jour, tprec, 0)
            try:
                tsuiv = pres_jour.index(0,tdep + 1)
            except:
                tsuiv = 95
            soc_dep += sum(nrj_jour[tdep:tsuiv+1])/self.cap_bat
            temps_charge += (tdep + 1 - tprec)
            for i in range(tprec,tdep+1):
                socmin[i] = max(0.2, 1.1*soc_dep - (tdep - i)*self.puis_rech*self.efficiency/(4*self.cap_bat))
            tprec = tsuiv
        nrj_tot = sum(nrj_jour) / self.cap_bat
        j = 0
        for x in pres_jour[:tprec+1]:
            if x == 0:
                socmin[j] = max(socmin[j], 1.1*nrj_tot - (temps_charge - j)*self.puis_rech*self.efficiency/(self.cap_bat*4))
                j += 1
        for i in range(tprec, len(socmin)):
            socmin[i] = 0.5
        self.journee.socmin = socmin
        return socmin
        