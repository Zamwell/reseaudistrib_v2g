# -*- coding: utf-8 -*-
"""
Created on Thu May  2 23:29:23 2019

@author: Any
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 18:01:43 2019

@author: Utilisateur
"""

import pandas as pd
import math

def domtravail(li):
    if len([1 for tu in li if not(((math.floor(tu[0])==1) or (math.floor(tu[0])==6) or (math.floor(tu[0])==9)))]) > 0:
        return False
    if len([1 for tu in li if (math.floor(tu[0])==9)]) < 1:
        return False
   
    #la boucle sert à vérifier si y il y a eu retour maison entre deux sessions de travail : on vérifie si un 1.1 est intercalé entre des 9
    indneuf=-1
    untrouve = False
    
    for i,tu in enumerate(li):
        if math.floor(tu[0]) == 9:
            if untrouve and indneuf >= 0:
                return False
            elif untrouve and indneuf < 0:
                untrouve = False
                indneuf = i
            else:
                indneuf = i
        elif math.floor(tu[0]) == 1:
            untrouve = True
                
#Assure de revenir à la maison à la fin de la journee
    if not(math.floor(li[-1][0])==1):
        return False

    return True

def domtravailmidi(li):
    (u,v,x,y)=(False,False,False,False)
    if len([1 for tu in li if not(((math.floor(tu[0])==1) or (math.floor(tu[0])==6) or (math.floor(tu[0])==9)))]) > 0:
        return False
    if len([1 for tu in li if (math.floor(tu[0])==1)]) < 2:
        return False
    if len([1 for tu in li if (math.floor(tu[0])==9)]) < 2:
        return False
    for tu in li:
        if math.floor(tu[0])==1:
            if (pd.to_timedelta(tu[1]) > pd.to_timedelta(11,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(14,unit='h')):
                u=True
            elif (pd.to_timedelta(tu[1]) >pd.to_timedelta(15,unit='h')):
                v=True
        elif math.floor(tu[0])==9:
            if (pd.to_timedelta(tu[1]) > pd.to_timedelta(4,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(11,unit='h')):
                x=True
            elif (pd.to_timedelta(tu[1]) >pd.to_timedelta(11,unit='h')):
                y=True
                
#la boucle sert à vérifier qu'il n'y a bien que 2 blocs de travail : on vérifie si un 1.1 est intercalé entre des 9, si ça arrive 2 fois ou plus c'est pas bon
    indneuf=-1
    untrouve = False
    nbsessiontrav = 0
    for i,tu in enumerate(li):
        if math.floor(tu[0]) == 9:
            if untrouve and indneuf >= 0:
                    nbsessiontrav+=1
                    indneuf= i
                    untrouve = False
                    if nbsessiontrav >=2:
                        return False
            elif untrouve and indneuf < 0:
                untrouve = False
                indneuf = i
            else:
                indneuf = i
        elif math.floor(tu[0]) == 1:
            untrouve = True
   
    #Assure de revenir à la maison à la fin de la journee
    if not(math.floor(li[-1][0])==1):
        return False

    return (x==True and y== True and u==True and v==True)

def domtravailloisirs(li):
    if not(domtravail(li) or domtravailmidiloisirs(li) or domtravailmidi(li)):
        if len([1 for tu in li if not((((math.floor(tu[0])>=1) and (math.floor(tu[0])<8)) or (math.floor(tu[0])==9)))]) > 0:
            return False
        if len([1 for tu in li if tu[0] == 2 or tu[0] == 3]) <1:
            return False
        if len([1 for tu in li if (math.floor(tu[0])==1)]) < 1:
            return False
        if len([1 for tu in li if (math.floor(tu[0])==9)]) < 1:
            return False
        #la boucle sert à vérifier si y il y a eu retour maison entre deux sessions de travail : on vérifie si un 1.1 est intercalé entre des 9
        indneuf=-1
        untrouve = False
        
        for i,tu in enumerate(li):
            if math.floor(tu[0]) == 9:
                if untrouve and indneuf >= 0:
                    return False
                elif untrouve and indneuf < 0:
                    untrouve = False
                    indneuf = i
                else:
                    indneuf = i
            elif math.floor(tu[0]) == 1:
                untrouve = True
                    
        #Assure de revenir à la maison à la fin de la journee
        if not(math.floor(li[-1][0])==1):
            return False

        return True
    else:
        return False

def domtravailmidiloisirs(li):
    if not(domtravailmidi(li)):
        (u,v,x,y)=(False,False,False,False)
        if len([1 for tu in li if not((((math.floor(tu[0])>=1) and (math.floor(tu[0])<8)) or (math.floor(tu[0])==9)))]) > 0:
            return False
        if len([1 for tu in li if tu[0] == 2 or tu[0] == 3]) <1:
            return False
        if len([1 for tu in li if (math.floor(tu[0])==1)]) < 2:
            return False
        if len([1 for tu in li if (math.floor(tu[0])==9)]) < 2:
            return False
        for tu in li:
            if math.floor(tu[0])==1:
                if (pd.to_timedelta(tu[1]) > pd.to_timedelta(11,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(14,unit='h')):
                    u=True
                elif (pd.to_timedelta(tu[1]) >pd.to_timedelta(15,unit='h')):
                    v=True
            elif math.floor(tu[0])==9:
                if (pd.to_timedelta(tu[1]) > pd.to_timedelta(4,unit='h')) and (pd.to_timedelta(tu[1]) < pd.to_timedelta(11,unit='h')):
                    x=True
                elif (pd.to_timedelta(tu[1]) >pd.to_timedelta(11,unit='h')):
                    y=True
                        
            #la boucle sert à vérifier qu'il n'y a bien que 2 blocs de travail : on vérifie si un 1.1 est intercalé entre des 9, si ça arrive 2 fois ou plus c'est pas bon
        indneuf=-1
        untrouve = False
        nbsessiontrav = 0
        for i,tu in enumerate(li):
            if math.floor(tu[0]) == 9:
                if untrouve and indneuf >= 0:
                        nbsessiontrav+=1
                        indneuf= i
                        untrouve = False
                        if nbsessiontrav >=2:
                            return False
                elif untrouve and indneuf < 0:
                    untrouve = False
                    indneuf = i
                else:
                    indneuf = i
            elif math.floor(tu[0]) == 1:
                untrouve = True
    
        #Assure de revenir à la maison à la fin de la journee
        if not(math.floor(li[-1][0])==1):
            return False
        
        return (x==True & y== True & u==True & v==True)
    else:
        return False


    
def domloisirs(li):
    if len([1 for tu in li if not(((math.floor(tu[0])>=1) and (math.floor(tu[0])<8)) )]) > 0:
        return False
    if len([1 for tu in li if (math.floor(tu[0])==1)]) < 1:
        return False
    if len([1 for tu in li if tu[0] == 2 or tu[0] == 3]) <1:
        return False
    
    #Assure de revenir à la maison à la fin de la journee
    if not(math.floor(li[-1][0])==1):
        return False

    return True

#def autre(li):
#    if not(domloisirs(li) or domtravail(li) or domtravailmidi(li) or domtravailloisirs(li) or domtravailmidiloisirs(li)):
#        return True
#    else:
#        return False
