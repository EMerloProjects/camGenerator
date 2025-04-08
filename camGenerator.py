import pandas as pd
import numpy as np
import xlrd
import matplotlib
import os
import math
pi = math.pi
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
import csv
from pandas import DataFrame
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import BSpline
from scipy.interpolate import make_smoothing_spline

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
os.system('cls')


### LETTURA FILE EXCEL CON LA LOOKUP TABLE DI M1/M2 IN SALITA
nome_percorso_LUT_salita = str(r'C:\Users\e.merlo\Desktop\lookuptableSalita_FD618-FD821.xlsx')
y_m1_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "A")
y_m2_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "B")
y_r1_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "C")
y_r2_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "D")
y_r3_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "E")
y_r4_salita = pd.read_excel(nome_percorso_LUT_salita, usecols = "F")

yM1Salita = np.array(y_m1_salita)
yM2Salita = np.array(y_m2_salita)
yR1Salita = np.array(y_r1_salita)
yR2Salita = np.array(y_r2_salita)
yR3Salita = np.array(y_r3_salita)
yR4Salita = np.array(y_r4_salita)

### LETTURA FILE EXCEL CON LOOKUP TABLE DI M1/M2 IN DISCESA
nome_percorso_LUT_discesa = str(r'C:\Users\e.merlo\Desktop\lookuptableDiscesa_FD618-FD821.xlsx')
y_m1_discesa = pd.read_excel(nome_percorso_LUT_discesa, usecols = "A")
y_m2_discesa = pd.read_excel(nome_percorso_LUT_discesa, usecols = "B")
y_piattello_discesa = pd.read_excel(nome_percorso_LUT_discesa, usecols = "C")

yM1Discesa = np.array(y_m1_discesa)
yM2Discesa = np.array(y_m2_discesa)
yPiattelloDiscesa = np.array(y_piattello_discesa)


#### LETTURA FILE DI CONFIGURAZIONE 
nomePercorsoConfigurazione = str(r'C:\Users\e.merlo\Desktop\configurazione_cammeFD618-821.xlsx')
configurazioneCamma = pd.read_excel(nomePercorsoConfigurazione, usecols = "B")
configurazioneCammaArray = np.array(configurazioneCamma)

angoloDwellBasso = int(configurazioneCammaArray[0])
angoloDurataSalita = int(configurazioneCammaArray[1])
angoloDwellAlto = int(configurazioneCammaArray[2])

angoloInizioSalita = angoloDwellBasso
angoloFineSalita = angoloInizioSalita + angoloDurataSalita
angoloInizioDiscesa = angoloFineSalita + angoloDwellAlto
angoloFinediscesa = 360


### DEFINIZIONE FUNZIONI

# trova coordinata x del cerchio
def xCerchio(r,n,i):
     result = (math.cos((2*pi)/n*i)*r)
     return result

# trova coordianta y del cerchio
def yCerchio(r,n,i):
     result = (math.sin((2*pi)/n*i)*r)
     return result

# trova indice dell'elemento più vicino al valore nella lista
def indicePiùVicino (lista, valore):
    return min(range(len(lista)), key=lambda i: abs(lista[i]-valore))

# interpola un cursore esterno di un range con un cursore interno di altro range
def trovaCursoreInternoInterpolato (inizioRangeEsterno, fineRangeEsterno, cursoreEsterno, inizioRangeInterno, fineRangeInterno):
    proporzioneRange = (fineRangeInterno - inizioRangeInterno)/(fineRangeEsterno - inizioRangeEsterno)
    cursoreEsternoAssoluto = cursoreEsterno - inizioRangeEsterno
    cursoreInternoInterpolato = (inizioRangeInterno + cursoreEsternoAssoluto*proporzioneRange)
    return int(cursoreInternoInterpolato)

# interpola un cursore esterno di un range, che parte da zero, con un cursore interno di un altro range
def trovaCursoreInternoInterpolatoPartendoDaZero (inizioRangeEsterno, fineRangeEsterno, cursoreEsterno, inizioRangeInterno, fineRangeInterno):
    proporzioneRange = (fineRangeInterno - inizioRangeInterno)/(fineRangeEsterno - inizioRangeEsterno)
    cursoreEsternoAssoluto = cursoreEsterno
    cursoreInternoInterpolato = (inizioRangeInterno + cursoreEsternoAssoluto*proporzioneRange)
    return int(cursoreInternoInterpolato)

# prende un vettore, scarta gli zeri e restituisce un vettore senza zeri
def scartaZeriVettore(vettoreLungo):
    vettoreSenzaZeri = []
    for i in range(len(vettoreLungo)):
        if float(vettoreLungo[i]) != 0:
            vettoreSenzaZeri.append(float(vettoreLungo[i]))
    return vettoreSenzaZeri

# prende un vettore, scarta gli zeri e restituisce un vettore senza zeri e uno con gli indici usati
def scartaZeriVettorepiùIndici(vettoreLungo):
    vettoreSenzaZeri = []
    vettoreIndici = []
    for i in range(len(vettoreLungo)):
        if float(vettoreLungo[i]) != 0:
            vettoreSenzaZeri.append(float(vettoreLungo[i]))
            vettoreIndici.append(float(i))
    return vettoreSenzaZeri, vettoreIndici

# controlla se un valore è dentro un vettore di punti
def isPresent(vettore,valore):
    minchiavero = False
    for i in range(len(vettore)):
      if vettore[i]==valore:
         minchiavero = True
    return minchiavero

# controlla se un valore è dentro un vettore di punti am arrotonda tutto a 2 cifre decimali
def isPresentR2(vettore,valore):
    minchiavero = False
    for i in range(len(vettore)):
      if round(vettore[i],2)==round(valore,2):
         minchiavero = True
    return minchiavero

# disegna un cerchio punto per punto rotto in centesimi di mm
def disegnaPuntiCerchio(xCentroCerchio, yCentroCerchio, raggioCerchio, numeroSezioniCerchio):
   puntiXcerchio = []
   puntiYcerchio = []
   for i in range(0,numeroSezioniCerchio,1):
      puntiXcerchio.append(float(xCentroCerchio + xCerchio(raggioCerchio,numeroSezioniCerchio,i)))
      puntiYcerchio.append(float(yCentroCerchio + yCerchio(raggioCerchio,numeroSezioniCerchio,i)))
   return(puntiXcerchio,puntiYcerchio)

# trova la distanza cartesiana tra i due punti
def distanzaCartesiana(x1,y1,x2,y2):
   xQuadro = (x2-x1)**2
   yQuadro = (y2-y1)**2
   lunghezza = np.sqrt(xQuadro+yQuadro)
   return(lunghezza)

# trova il raggio della circonferenza che inscrive la corda data (a parità di arco)
def raggioFromCorda(cordaData, angoloArco):
   metaCorda = cordaData/2
   angoloArcoRadianti = math.radians(angoloArco)
   parteTrigonometrica = math.sin(angoloArcoRadianti/2)
   raggioOttenuto = metaCorda/parteTrigonometrica
   return raggioOttenuto

#campiona ogni 10 elementi l'array
def campiona10(vettore):
   vettoreCampionato = []
   for i in range(0,len(vettore),10):
      vettoreCampionato.append(vettore[i])
   return vettoreCampionato

#campiona ogni 20 elementi l'array
def campiona20(vettore):
   vettoreCampionato = []
   for i in range(0,len(vettore),20):
      vettoreCampionato.append(vettore[i])
   return vettoreCampionato

def campionaOgniTot(vettore, intervalloCampionamento):
   vettoreDaSostituire = []
   for i in range(0, len(vettore), intervalloCampionamento):
      vettoreDaSostituire.append(vettore[i])
   return vettoreDaSostituire

#trova in un array la fine della curva successiva
def trovaInizioFineSerie(vettore):
   settoriInizioFineSerie = []
   giàInSerie = 0

   if len(vettore) > 2:
        settoriInizioFineSerie.append(vettore[0])
        for i in range(1,len(vettore)-1,1):
            if ((vettore[i+1] - vettore[i]) != 1) and (giàInSerie == 0):
                    settoriInizioFineSerie.append(vettore[i])
                    giàInSerie = 1
            if ((vettore[i+1] - vettore[i]) == 1) and (giàInSerie == 1):
                giàInSerie = 0        
        settoriInizioFineSerie.append(vettore[-1])

   return settoriInizioFineSerie


    


### INZIO SCRIPT

# indice di frazioni del cerchio standard
numeroDivisioniCerchio = 3600
sezioniCamma = numeroDivisioniCerchio

raggioMinimoM1 = int(configurazioneCammaArray[9])
raggioMinimoM2 = int(configurazioneCammaArray[10])

proporzioneDimensioneArray = len(yM1Salita)/sezioniCamma

fasiAttiveLeggeDiMoto = 4
angoloFasiAttiveSalita = np.round(angoloDurataSalita/fasiAttiveLeggeDiMoto)


#IMPOSTAZIONI LEGGE DI MOTO
altezzaRuotaAFilo = int(configurazioneCammaArray[4])
altezzaMinPiattello = int(configurazioneCammaArray[5])
altezzaMaxPiattello = int(configurazioneCammaArray[6])

# indice cursore interno alla LUT (per inizio si intende fine fase...)
indiceInizioFase1 = indicePiùVicino(yR1Salita, altezzaRuotaAFilo)
indiceInizioFase2 = indicePiùVicino(yR2Salita, altezzaRuotaAFilo)
indiceInizioFase3 = indicePiùVicino(yR3Salita, altezzaRuotaAFilo)
indiceInizioFase4 = indicePiùVicino(yR4Salita, altezzaRuotaAFilo)
indiceInizioFase5 = indicePiùVicino(yR4Salita, altezzaMaxPiattello)

# durata cursore interno alla LUT
durataCursoreInternoFase1 = indiceInizioFase1-int(0)
durataCursoreInternoFase2 = indiceInizioFase2-indiceInizioFase1
durataCursoreInternoFase3 = indiceInizioFase3-indiceInizioFase2
durataCursoreInternoFase4 = indiceInizioFase4-indiceInizioFase3
durataCursoreInternoFase5 = indiceInizioFase5-indiceInizioFase4


# indice cursore esterno legge di moto (per inizio si intende fine fase...)
inizioEsternoFase1 = int(angoloDwellBasso*10)
inizioEsternoFase2 = int(inizioEsternoFase1 + (1*angoloFasiAttiveSalita*10))
inizioEsternoFase3 = int(inizioEsternoFase1 + (2*angoloFasiAttiveSalita)*10)
inizioEsternoFase4 = int(inizioEsternoFase1 + (3*angoloFasiAttiveSalita)*10)
inizioEsternoFase5 = int(inizioEsternoFase1 + (4*angoloFasiAttiveSalita)*10)
inizioEsternoDiscesa = angoloDwellAlto*10 + inizioEsternoFase4 

# indice di legge di moto di quando finisce la salita e inizia dwell alto
indiceYfineSalita = []

# lunghezza in Y della discesa
spazioDiscesa = yPiattelloDiscesa[0] - yPiattelloDiscesa[-1]

#definizione punti critici sacri da non tagliare in interpolazione
puntiCriticiAlzataM1 = [0] * (numeroDivisioniCerchio+1)
puntiCriticiAlzataM2 = [0] * (numeroDivisioniCerchio+1)
indiceEsternoPuntiCritici = [0] * (numeroDivisioniCerchio+1)


### DISEGNO CERCHIO INTERPOLATO DA LUT
## CAMMA M1
puntiX_M1 = []
puntiY_M1 = []

# # disegno circonferenza a raggio minimo
# puntiXstdM1 = []
# puntiYstdM1 = []

# for t in range(0,3600+1,1):
#    puntiXstd.append(xCerchio(raggioMinimo,numeroDivisioniCerchio,t))
#    puntiYstd.append(yCerchio(raggioMinimo,numeroDivisioniCerchio,t)) 

# disegno circonferenza del mozzo 
puntiXstdMozzo = []
puntiYstdMozzo = []
raggioMozzo = 50

for t in range(0,3600+1,1):
    puntiXstdMozzo.append(xCerchio(raggioMozzo,numeroDivisioniCerchio,t))
    puntiYstdMozzo.append(yCerchio(raggioMozzo,numeroDivisioniCerchio,t)) 

#inizializzazione punti di controllo
puntiInizioFase1_M1 = []
puntiInizioFase2_M1 = []
puntiInizioFase3_M1 = []
puntiInizioFase4_M1 = []
puntiInizioFase5_M1 = []
puntiInizioSalita_M1 = []
puntiInizioDiscesa_M1 = []
puntiFineDiscesa_M1 = [] 

verticaleInizioFase1_M1 = []
verticaleInizioFase2_M1 = []
verticaleInizioFase3_M1 = []
verticaleInizioFase4_M1 = []
verticaleInizioFase5_M1 = []
verticaleInizioSalita_M1 = []
verticaleIniziodiscesa_M1 = []
verticaleFineDiscesa_M1 = []

#punti per diagramma di alzata
asseAngolare_M1 = []
asseAlzata_M1 = []

#inizio disegno camma
for t in range(0, sezioniCamma+1, 1):
    if t<=(inizioEsternoFase1):
        indiceY = trovaCursoreInternoInterpolato(0,inizioEsternoFase1,t,0,indiceInizioFase1)
        puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[0])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
        puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[0])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

        asseAlzata_M1.append(yM1Salita[0])
        asseAngolare_M1.append(t)  

        if t==(0):
            puntiCriticiAlzataM1[t] = float(yM1Salita[0])

        if t==(inizioEsternoFase1):
           puntiInizioFase1_M1.append(0)
           puntiInizioFase1_M1.append(0)
           puntiInizioFase1_M1.append(puntiX_M1[-1])
           puntiInizioFase1_M1.append(puntiY_M1[-1])

           verticaleInizioFase1_M1 = t

           puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
           indiceEsternoPuntiCritici[t] = t

    elif t>(inizioEsternoFase1) and t<=(inizioEsternoFase2):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase1,inizioEsternoFase2,t,indiceInizioFase1,indiceInizioFase2)
         puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
         puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

         asseAlzata_M1.append(yM1Salita[indiceY])
         asseAngolare_M1.append(t)  

         if t==inizioEsternoFase2:
             puntiInizioFase2_M1.append(0)
             puntiInizioFase2_M1.append(0)
             puntiInizioFase2_M1.append(puntiX_M1[-1])
             puntiInizioFase2_M1.append(puntiY_M1[-1])  

             verticaleInizioFase2_M1 = t

             puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
             indiceEsternoPuntiCritici[t] = t
             
    elif t>(inizioEsternoFase2) and t<=(inizioEsternoFase3):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase1,inizioEsternoFase2,t,indiceInizioFase1,indiceInizioFase2)
         puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
         puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

         asseAlzata_M1.append(yM1Salita[indiceY])
         asseAngolare_M1.append(t)  

         if t==inizioEsternoFase3:
             puntiInizioFase3_M1.append(0)
             puntiInizioFase3_M1.append(0)
             puntiInizioFase3_M1.append(puntiX_M1[-1])
             puntiInizioFase3_M1.append(puntiY_M1[-1])  

             verticaleInizioFase3_M1 = t

             puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
             indiceEsternoPuntiCritici[t] = t

    elif t>(inizioEsternoFase3) and t<=(inizioEsternoFase4):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase3,inizioEsternoFase4,t,indiceInizioFase3,indiceInizioFase4)
         puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M1.append(yM1Salita[indiceY])
         asseAngolare_M1.append(t)  

         if t==inizioEsternoFase4:
              puntiInizioFase4_M1.append(0)
              puntiInizioFase4_M1.append(0)
              puntiInizioFase4_M1.append(puntiX_M1[-1])
              puntiInizioFase4_M1.append(puntiY_M1[-1])

              verticaleInizioFase4_M1 = t

              puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
              indiceEsternoPuntiCritici[t] = t

    elif t>(inizioEsternoFase4) and t<=(inizioEsternoFase5):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase4,inizioEsternoFase5,t,indiceInizioFase4,indiceInizioFase5)
         puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M1.append(yM1Salita[indiceY])
         asseAngolare_M1.append(t)  

         if t==inizioEsternoFase5:
             puntiInizioFase5_M1.append(0)
             puntiInizioFase5_M1.append(0)
             puntiInizioFase5_M1.append(puntiX_M1[-1])
             puntiInizioFase5_M1.append(puntiY_M1[-1])

             verticaleInizioFase5_M1 = t

             puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
             indiceEsternoPuntiCritici[t] = t

             indiceYfineSalita = int(indiceY)
         
    elif t>(inizioEsternoFase5) and t<=(inizioEsternoDiscesa):
         puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceYfineSalita]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Salita[indiceYfineSalita]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M1.append(yM1Salita[indiceYfineSalita])
         asseAngolare_M1.append(t) 

         if t==(inizioEsternoDiscesa):
             puntiInizioDiscesa_M1.append(0)
             puntiInizioDiscesa_M1.append(0)
             puntiInizioDiscesa_M1.append(puntiX_M1[-1])
             puntiInizioDiscesa_M1.append(puntiY_M1[-1])

             verticaleIniziodiscesa_M1 = t

             puntiCriticiAlzataM1[t] = float(yM1Salita[indiceY])
             indiceEsternoPuntiCritici[t] = t       

    elif t>(inizioEsternoDiscesa):
          percentualeDiscesa = (t-(angoloDwellAlto*10 + inizioEsternoFase4))/((360*10)-(angoloDwellAlto*10 + inizioEsternoFase4))
          altezzaLocalePiattello = altezzaMaxPiattello-(spazioDiscesa* percentualeDiscesa)
          indiceY = indicePiùVicino(yPiattelloDiscesa, altezzaLocalePiattello)

          puntiX_M1.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Discesa[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
          puntiY_M1.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,t) + float(yM1Discesa[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

          asseAlzata_M1.append(yM1Discesa[indiceY])
          asseAngolare_M1.append(t)  

          if t==(sezioniCamma):
             puntiFineDiscesa_M1.append(0)
             puntiFineDiscesa_M1.append(0)
             puntiFineDiscesa_M1.append(puntiX_M1[-1])
             puntiFineDiscesa_M1.append(puntiY_M1[-1])

             verticaleFineDiscesa_M1 = t

             #chiudi inizio con fine
             puntiX_M1[t] = puntiX_M1[0]
             puntiY_M1[t] = puntiY_M1[0]

             puntiCriticiAlzataM1[t] = float(yM1Discesa[indiceY])
             indiceEsternoPuntiCritici[t] = t


# indice di quanta percentuale della fase attiva del moto è lunga la fase di salita piattello
rapportoInizioSalitaRispettoDurataFasi = round(float(configurazioneCammaArray[7]),2)
durataFaseInizioSalita = (angoloDurataSalita/fasiAttiveLeggeDiMoto)*rapportoInizioSalitaRispettoDurataFasi

# riscrizione fase salita piattello
for t in range(0, int(durataFaseInizioSalita*10)+1, 1):
    indiceRiscritturaPuntiZero = int(inizioEsternoFase1-(durataFaseInizioSalita*10))
    cursoreTlocale = inizioEsternoFase1-(durataFaseInizioSalita*10) + t 
    indiceRiscritturaPunti = int(cursoreTlocale)
    indiceY = trovaCursoreInternoInterpolatoPartendoDaZero(indiceRiscritturaPuntiZero,inizioEsternoFase1-1,t,0,indiceInizioFase1-1)
    puntiX_M1[indiceRiscritturaPunti] =  xCerchio(raggioMinimoM1,numeroDivisioniCerchio,indiceRiscritturaPunti) + float(yM1Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(indiceRiscritturaPunti)))
    puntiY_M1[indiceRiscritturaPunti] =  yCerchio(raggioMinimoM1,numeroDivisioniCerchio,indiceRiscritturaPunti) + float(yM1Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(indiceRiscritturaPunti)))

    asseAlzata_M1[indiceRiscritturaPunti] = yM1Salita[indiceY]

    if t==(0):
      puntiInizioSalita_M1.append(0)
      puntiInizioSalita_M1.append(0)
      puntiInizioSalita_M1.append(puntiX_M1[int(indiceRiscritturaPunti)])
      puntiInizioSalita_M1.append(puntiY_M1[int(indiceRiscritturaPunti)])

      verticaleInizioSalita_M1 = indiceRiscritturaPunti

      puntiCriticiAlzataM1[indiceRiscritturaPunti] = float(yM1Salita[indiceY])
      indiceEsternoPuntiCritici[indiceRiscritturaPunti] = indiceRiscritturaPunti
    
    if t==(int(durataFaseInizioSalita*10)):
      puntiInizioFase1_M1.append(0)
      puntiInizioFase1_M1.append(0)
      puntiInizioFase1_M1.append(puntiX_M1[int(indiceRiscritturaPunti)])
      puntiInizioFase1_M1.append(puntiY_M1[int(indiceRiscritturaPunti)])

      verticaleInizioFase1_M1 = indiceRiscritturaPunti

      puntiCriticiAlzataM1[indiceRiscritturaPunti] = float(yM1Salita[indiceY])
      indiceEsternoPuntiCritici[indiceRiscritturaPunti] = indiceRiscritturaPunti

## CAMMA M2
puntiX_M2 = []
puntiY_M2 = []


#inizializzazione punti di controllo
puntiInizioFase1_M2 = []
puntiInizioFase2_M2 = []
puntiInizioFase3_M2 = []
puntiInizioFase4_M2 = []
puntiInizioFase5_M2 = []
puntiInizioSalita_M2 = []
puntiInizioDiscesa_M2 = []
puntiFineDiscesa_M2 = [] 

verticaleInizioFase1_M2 = []
verticaleInizioFase2_M2 = []
verticaleInizioFase3_M2 = []
verticaleInizioFase4_M2 = []
verticaleInizioFase5_M2 = []
verticaleInizioSalita_M2 = []
verticaleIniziodiscesa_M2 = []
verticaleFineDiscesa_M2 = []

#punti per diagramma di alzata
asseAngolare_M2 = []
asseAlzata_M2 = []

#inizio disegno camma
for t in range(0, sezioniCamma+1, 1):
    if t<=(inizioEsternoFase1):
        indiceY = trovaCursoreInternoInterpolato(0,inizioEsternoFase1,t,0,indiceInizioFase1)
        puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[0])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
        puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[0])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

        asseAlzata_M2.append(yM2Salita[0])
        asseAngolare_M2.append(t)  

        if t==(0):
            puntiCriticiAlzataM2[t] = float(yM2Salita[0])

        if t==(inizioEsternoFase1):
           puntiInizioFase1_M2.append(0)
           puntiInizioFase1_M2.append(0)
           puntiInizioFase1_M2.append(puntiX_M2[-1])
           puntiInizioFase1_M2.append(puntiY_M2[-1])

           verticaleInizioFase1_M2 = t

           puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])

    elif t>(inizioEsternoFase1) and t<=(inizioEsternoFase2):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase1,inizioEsternoFase2,t,indiceInizioFase1,indiceInizioFase2)
         puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
         puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

         asseAlzata_M2.append(yM2Salita[indiceY])
         asseAngolare_M2.append(t)  

         if t==inizioEsternoFase2:
             puntiInizioFase2_M2.append(0)
             puntiInizioFase2_M2.append(0)
             puntiInizioFase2_M2.append(puntiX_M2[-1])
             puntiInizioFase2_M2.append(puntiY_M2[-1])  

             verticaleInizioFase2_M2 = t

             puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])
             
    elif t>(inizioEsternoFase2) and t<=(inizioEsternoFase3):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase1,inizioEsternoFase2,t,indiceInizioFase1,indiceInizioFase2)
         puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY])*math.cos(2*pi/(numeroDivisioniCerchio)*(t)))
         puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY])*math.sin(2*pi/(numeroDivisioniCerchio)*(t)))

         asseAlzata_M2.append(yM2Salita[indiceY])
         asseAngolare_M2.append(t)  

         if t==inizioEsternoFase3:
             puntiInizioFase3_M2.append(0)
             puntiInizioFase3_M2.append(0)
             puntiInizioFase3_M2.append(puntiX_M2[-1])
             puntiInizioFase3_M2.append(puntiY_M2[-1])  

             verticaleInizioFase3_M2 = t

             puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])

    elif t>(inizioEsternoFase3) and t<=(inizioEsternoFase4):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase3,inizioEsternoFase4,t,indiceInizioFase3,indiceInizioFase4)
         puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M2.append(yM2Salita[indiceY])
         asseAngolare_M2.append(t)  

         if t==inizioEsternoFase4:
              puntiInizioFase4_M2.append(0)
              puntiInizioFase4_M2.append(0)
              puntiInizioFase4_M2.append(puntiX_M2[-1])
              puntiInizioFase4_M2.append(puntiY_M2[-1])

              verticaleInizioFase4_M2 = t

              puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])

    elif t>(inizioEsternoFase4) and t<=(inizioEsternoFase5):
         indiceY = trovaCursoreInternoInterpolato(inizioEsternoFase4,inizioEsternoFase5,t,indiceInizioFase4,indiceInizioFase5)
         puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M2.append(yM2Salita[indiceY])
         asseAngolare_M2.append(t)  

         if t==inizioEsternoFase5:
             puntiInizioFase5_M2.append(0)
             puntiInizioFase5_M2.append(0)
             puntiInizioFase5_M2.append(puntiX_M2[-1])
             puntiInizioFase5_M2.append(puntiY_M2[-1])

             verticaleInizioFase5_M2 = t

             puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])
             indiceEsternoPuntiCritici[t] = t
         
    elif t>(inizioEsternoFase5) and t<=(inizioEsternoDiscesa):
         puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceYfineSalita]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
         puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Salita[indiceYfineSalita]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

         asseAlzata_M2.append(yM2Salita[indiceYfineSalita])
         asseAngolare_M2.append(t) 

         if t==(inizioEsternoDiscesa):
             puntiInizioDiscesa_M2.append(0)
             puntiInizioDiscesa_M2.append(0)
             puntiInizioDiscesa_M2.append(puntiX_M2[-1])
             puntiInizioDiscesa_M2.append(puntiY_M2[-1])

             verticaleIniziodiscesa_M2 = t

             puntiCriticiAlzataM2[t] = float(yM2Salita[indiceY])     

    elif t>(inizioEsternoDiscesa):
          percentualeDiscesa = (t-(angoloDwellAlto*10 + inizioEsternoFase4))/((360*10)-(angoloDwellAlto*10 + inizioEsternoFase4))
          altezzaLocalePiattello = altezzaMaxPiattello-(spazioDiscesa* percentualeDiscesa)
          indiceY = indicePiùVicino(yPiattelloDiscesa, altezzaLocalePiattello)

          puntiX_M2.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Discesa[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(t))))
          puntiY_M2.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,t) + float(yM2Discesa[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(t))))

          asseAlzata_M2.append(yM2Discesa[indiceY])
          asseAngolare_M2.append(t)  

          if t==(sezioniCamma):
             puntiFineDiscesa_M2.append(0)
             puntiFineDiscesa_M2.append(0)
             puntiFineDiscesa_M2.append(puntiX_M2[-1])
             puntiFineDiscesa_M2.append(puntiY_M2[-1])

             verticaleFineDiscesa_M2 = t

             #chiudi inizio con fine
             puntiX_M2[t] = puntiX_M2[0]
             puntiY_M2[t] = puntiY_M2[0]

             puntiCriticiAlzataM2[t] = float(yM2Discesa[indiceY])
             indiceEsternoPuntiCritici[t] = t


# indice di quanta percentuale della fase attiva del moto è lunga la fase di salita piattello
rapportoInizioSalitaRispettoDurataFasi = round(float(configurazioneCammaArray[7]),2)
durataFaseInizioSalita = (angoloDurataSalita/fasiAttiveLeggeDiMoto)*rapportoInizioSalitaRispettoDurataFasi

# riscrizione fase salita piattello
for t in range(0, int(durataFaseInizioSalita*10)+1, 1):
    indiceRiscritturaPuntiZero = int(inizioEsternoFase1-(durataFaseInizioSalita*10))
    cursoreTlocale = inizioEsternoFase1-(durataFaseInizioSalita*10) + t 
    indiceRiscritturaPunti = int(cursoreTlocale)
    indiceY = trovaCursoreInternoInterpolatoPartendoDaZero(indiceRiscritturaPuntiZero,inizioEsternoFase1-1,t,0,indiceInizioFase1-1)
    puntiX_M2[indiceRiscritturaPunti] =  xCerchio(raggioMinimoM2,numeroDivisioniCerchio,indiceRiscritturaPunti) + float(yM2Salita[indiceY]*math.cos(2*pi/(numeroDivisioniCerchio)*(indiceRiscritturaPunti)))
    puntiY_M2[indiceRiscritturaPunti] =  yCerchio(raggioMinimoM2,numeroDivisioniCerchio,indiceRiscritturaPunti) + float(yM2Salita[indiceY]*math.sin(2*pi/(numeroDivisioniCerchio)*(indiceRiscritturaPunti)))

    asseAlzata_M2[indiceRiscritturaPunti] = yM2Salita[indiceY]

    if t==(0):
      puntiInizioSalita_M2.append(0)
      puntiInizioSalita_M2.append(0)
      puntiInizioSalita_M2.append(puntiX_M2[int(indiceRiscritturaPunti)])
      puntiInizioSalita_M2.append(puntiY_M2[int(indiceRiscritturaPunti)])

      verticaleInizioSalita_M2 = indiceRiscritturaPunti

      puntiCriticiAlzataM2[indiceRiscritturaPunti] = float(yM2Salita[indiceY])
      indiceEsternoPuntiCritici[indiceRiscritturaPunti] = indiceRiscritturaPunti
    
    if t==(int(durataFaseInizioSalita*10)):
      puntiInizioFase1_M2.append(0)
      puntiInizioFase1_M2.append(0)
      puntiInizioFase1_M2.append(puntiX_M2[int(indiceRiscritturaPunti)])
      puntiInizioFase1_M2.append(puntiY_M2[int(indiceRiscritturaPunti)])

      verticaleInizioFase1_M2 = indiceRiscritturaPunti

      puntiCriticiAlzataM2[indiceRiscritturaPunti] = float(yM2Salita[indiceY])
      indiceEsternoPuntiCritici[indiceRiscritturaPunti] = indiceRiscritturaPunti



# plt.figure()
# plt.plot(asseAngolare_M1,asseAlzata_M1, linewidth=3)
# plt.plot(asseAngolare_M2,asseAlzata_M2, linewidth=3)
# plt.title("DIAGRAMMA ALZATA CAMMA M1/M2 SUPER GREZZO")
# plt.xlabel("DECIMI ANGOLO")
# plt.ylabel("ALZATA Y")


#### FASE DI CAMPIONAMENTO DEL MOVIMENTO

risultatoScartazeriM1 = scartaZeriVettorepiùIndici(puntiCriticiAlzataM1)
risultatoScartazeriM2 = scartaZeriVettorepiùIndici(puntiCriticiAlzataM2)

puntiCriticiAlzataM1Campionati = risultatoScartazeriM1[0]
puntiCriticiAlzataM2Campionati = risultatoScartazeriM2[0]
indiceEsternoPuntiCriticiCampionati = risultatoScartazeriM1[1] #non so perchè mettondo M2 crasha tutto

plt.figure()
plt.plot(indiceEsternoPuntiCriticiCampionati, puntiCriticiAlzataM1Campionati)
plt.plot(indiceEsternoPuntiCriticiCampionati, puntiCriticiAlzataM2Campionati)
plt.title("DIAGRAMMA ALZATA CAMPIONATO")
plt.xlabel("DECIMI ANGOLO")
plt.ylabel("ALZATA Y")

plt.axvline(x=verticaleInizioFase1_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleInizioFase2_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleInizioFase3_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleInizioFase4_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleInizioFase5_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleInizioSalita_M1, color='r', linestyle='--', linewidth=2)
plt.axvline(x=verticaleIniziodiscesa_M1, color='m', linestyle='--', linewidth=2)
plt.axvline(x=verticaleFineDiscesa_M1, color='m', linestyle='--', linewidth=2)


# trova punti critici che appartengono alla salita e altri che sono della discesa

quantiPuntiCritici = len(indiceEsternoPuntiCriticiCampionati)

puntiCriticiM1Salita = puntiCriticiAlzataM1Campionati[1:(quantiPuntiCritici-2)] #parte da 1 perchè il primo punto è la partenza ed è lineare
punticriticiM2Salita = puntiCriticiAlzataM2Campionati[1:(quantiPuntiCritici-2)]
indiceEsternoPuntiCriticiSalita = indiceEsternoPuntiCriticiCampionati[1:(quantiPuntiCritici-2)]

puntiCriticiM1Discesa = puntiCriticiAlzataM1Campionati[-2:]
puntiCriticiM2Discesa = puntiCriticiAlzataM2Campionati[-2:]
indiceEsternoPuntiCriticiDiscesa =  indiceEsternoPuntiCriticiCampionati[-2:]

#togli quel salto tra inizioFase1 e (iniziofase1-1) nella riscrittura della fase di salita
del puntiCriticiM1Salita[1]
del punticriticiM2Salita[1]
del indiceEsternoPuntiCriticiSalita[1]

#definizione di spline per fasi di salita e discesa con tangente iniziale nulla
bcTypeSalita = ((1,0),(1,0))
bcTypeDiscesa = ((1,0),(1,0))

splineM1Salita = CubicSpline(indiceEsternoPuntiCriticiSalita, puntiCriticiM1Salita, bc_type=bcTypeSalita)
splineM2Salita = CubicSpline(indiceEsternoPuntiCriticiSalita, punticriticiM2Salita, bc_type=bcTypeSalita)
splineM1Discesa = CubicSpline(indiceEsternoPuntiCriticiDiscesa, puntiCriticiM1Discesa, bc_type=bcTypeDiscesa)
splineM2Discesa = CubicSpline(indiceEsternoPuntiCriticiDiscesa, puntiCriticiM2Discesa, bc_type=bcTypeDiscesa)

# splineM1Salita = make_smoothing_spline(indiceEsternoPuntiCriticiSalita, puntiCriticiM1Salita)
# splineM2Salita = make_smoothing_spline(indiceEsternoPuntiCriticiSalita, punticriticiM2Salita)
# definizione punti ascissa di salita e discesa
newxM1Salita = np.linspace(indiceEsternoPuntiCriticiSalita[0], indiceEsternoPuntiCriticiSalita[-1],int(indiceEsternoPuntiCriticiSalita[-1]-indiceEsternoPuntiCriticiSalita[0])+1)
newxM1Discesa = np.linspace(indiceEsternoPuntiCriticiDiscesa[0], indiceEsternoPuntiCriticiDiscesa[-1],int(indiceEsternoPuntiCriticiDiscesa[-1]-indiceEsternoPuntiCriticiDiscesa[0])+1)
newxM2Salita = np.linspace(indiceEsternoPuntiCriticiSalita[0], indiceEsternoPuntiCriticiSalita[-1],int(indiceEsternoPuntiCriticiSalita[-1]-indiceEsternoPuntiCriticiSalita[0])+1)
newxM2Discesa = np.linspace(indiceEsternoPuntiCriticiDiscesa[0], indiceEsternoPuntiCriticiDiscesa[-1],int(indiceEsternoPuntiCriticiDiscesa[-1]-indiceEsternoPuntiCriticiDiscesa[0])+1)

newyM1Salita = splineM1Salita(newxM1Salita)
newyM2Salita = splineM2Salita(newxM2Salita)
newyM1Discesa = splineM1Discesa(newxM1Discesa)
newyM2Discesa = splineM2Discesa(newxM2Discesa)

### GIUNTA CAMMA CON CAMMA INTERPOLATA
#creiamo una funzione che se becca la presenza di un elemento nelle nuove x prende le nuove y, altrimenti prende le y vecchie

puntiX_M1Final = []
puntiY_M1Final = []

puntiX_M2Final = []
puntiY_M2Final = []

# dipingi camma M1 nuova
for i in range(0, sezioniCamma+1, 1):
    if isPresent(newxM1Salita,i) == True:
        puntiX_M1Final.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,i) + float(newyM1Salita[i-int(newxM1Salita[0])]*math.cos(2*pi/(numeroDivisioniCerchio)*(i))))
        puntiY_M1Final.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,i) + float(newyM1Salita[i-int(newxM1Salita[0])]*math.sin(2*pi/(numeroDivisioniCerchio)*(i))))
    elif isPresent(newxM1Discesa,i)== True:
        puntiX_M1Final.append(xCerchio(raggioMinimoM1,numeroDivisioniCerchio,i) + float(newyM1Discesa[i-int(newxM1Discesa[0])]*math.cos(2*pi/(numeroDivisioniCerchio)*(i))))
        puntiY_M1Final.append(yCerchio(raggioMinimoM1,numeroDivisioniCerchio,i) + float(newyM1Discesa[i-int(newxM1Discesa[0])]*math.sin(2*pi/(numeroDivisioniCerchio)*(i))))
    else:
     puntiX_M1Final.append(puntiX_M1[i])
     puntiY_M1Final.append(puntiY_M1[i])

# dipingi camma M2 nuova
for i in range(0, sezioniCamma+1, 1):
    if isPresent(newxM2Salita,i) == True:
        puntiX_M2Final.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,i) + float(newyM2Salita[i-int(newxM2Salita[0])]*math.cos(2*pi/(numeroDivisioniCerchio)*(i))))
        puntiY_M2Final.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,i) + float(newyM2Salita[i-int(newxM2Salita[0])]*math.sin(2*pi/(numeroDivisioniCerchio)*(i))))
    elif isPresent(newxM2Discesa,i)== True:
        puntiX_M2Final.append(xCerchio(raggioMinimoM2,numeroDivisioniCerchio,i) + float(newyM2Discesa[i-int(newxM2Discesa[0])]*math.cos(2*pi/(numeroDivisioniCerchio)*(i))))
        puntiY_M2Final.append(yCerchio(raggioMinimoM2,numeroDivisioniCerchio,i) + float(newyM2Discesa[i-int(newxM2Discesa[0])]*math.sin(2*pi/(numeroDivisioniCerchio)*(i))))
    else:
     puntiX_M2Final.append(puntiX_M2[i])
     puntiY_M2Final.append(puntiY_M2[i])


# disegna diagramma alzata M1/M2 finale
newAsseAlzata_M1 = []
newAsseAlzata_M2 = []

newAsseAngolare_M1 = []
newAsseAngolare_M2 = []


for i in range(0, sezioniCamma+1, 1):
    newAsseAngolare_M1.append(i)
    if isPresent(newxM1Salita,i) == True:
        newAsseAlzata_M1.append(float(newyM1Salita[i-int(newxM1Salita[0])]))
    elif isPresent(newxM1Discesa,i)== True:
        newAsseAlzata_M1.append(float(newyM1Discesa[i-int(newxM1Discesa[0])]))
    else:
     newAsseAlzata_M1.append(float(asseAlzata_M1[i]))
   

for i in range(0, sezioniCamma+1, 1):
    newAsseAngolare_M2.append(i)
    if isPresent(newxM2Salita,i) == True:
        newAsseAlzata_M2.append(float(newyM2Salita[i-int(newxM2Salita[0])]))
    elif isPresent(newxM2Discesa,i)== True:
        newAsseAlzata_M2.append(float(newyM2Discesa[i-int(newxM2Discesa[0])]))
    else:
     newAsseAlzata_M2.append(float(asseAlzata_M2[i]))


plt.figure(figsize=(10,6))
plt.plot(newAsseAngolare_M1,newAsseAlzata_M1, linewidth= 3)
plt.plot(newAsseAngolare_M2,newAsseAlzata_M2, linewidth= 3)
plt.title("DIAGRAMMA ALZATA CAMMA M1/M2 FINALE")
plt.xlabel("DECIMI ANGOLO")
plt.ylabel("ALZATA Y + ZONE DOPPIO CONTATTO")

#### TEST CONTROLLO INTERPOLAZIONE CORDA RISPETTO CORDA PUNTERIA

raggioPunteria = float(configurazioneCammaArray[8])/(2)
raggioPunteriaSicurezza = raggioPunteria + float(2)

dxM1 = np.gradient(puntiX_M1Final)
dyM1 = np.gradient(puntiY_M1Final)
ddxM1 = np.gradient(dxM1)
ddyM1 = np.gradient(dyM1)

curvaturaM1 = np.abs(dxM1 * ddyM1 - dyM1 * ddxM1) / ((dxM1**2 + dyM1**2)**(3/2))
raggioCruvaturaMinmoM1 = 1 / np.max(curvaturaM1)
raggiCurvaturaM1 = 1/(curvaturaM1)

indicePuntoDoppioContattoM1 = []
for i in range (0, len(raggiCurvaturaM1)-2,1):
    # se la forma della camma è convessa (posso impuntarmi) e la curvatura è più piccola del raggio minimo allora devo riscrivere il punto:
    if ( (puntiY_M1Final[i]<puntiY_M2Final[i+2]) & (raggiCurvaturaM1[i+1] < raggioPunteriaSicurezza) ): 
        indicePuntoDoppioContattoM1.append(i)

puntiX_M1FinalDoppioContatto = []
puntiY_M1FinalDoppioContatto = []

for i in range(0,len(indicePuntoDoppioContattoM1),1):
   puntiX_M1FinalDoppioContatto.append(newAsseAngolare_M1[indicePuntoDoppioContattoM1[i]])
   puntiY_M1FinalDoppioContatto.append(newAsseAlzata_M1[indicePuntoDoppioContattoM1[i]])

plt.plot(puntiX_M1FinalDoppioContatto,puntiY_M1FinalDoppioContatto, color='red', linewidth= 4, label='M1 NON RIPRODUCIBILE')


dxM2 = np.gradient(puntiX_M2Final)
dyM2 = np.gradient(puntiY_M2Final)
ddxM2 = np.gradient(dxM2)
ddyM2 = np.gradient(dyM2)

curvaturaM2 = np.abs(dxM2 * ddyM2 - dyM2 * ddxM2) / ((dxM2**2 + dyM2**2)**(3/2))
raggioCruvaturaMinmoM2 = 1 / np.max(curvaturaM2)
raggiCurvaturaM2 = 1/(curvaturaM2)

indicePuntoDoppioContattoM2 = []
for i in range (0, len(raggiCurvaturaM2)-2,1):
    if ( (puntiY_M2Final[i]<puntiY_M2Final[i+2]) & (raggiCurvaturaM2[i+1] < raggioPunteriaSicurezza) ):
        indicePuntoDoppioContattoM2.append(i)

puntiX_M2FinalDoppioContatto = []
puntiY_M2FinalDoppioContatto = []

for i in range(0,len(indicePuntoDoppioContattoM2),1):
   puntiX_M2FinalDoppioContatto.append(newAsseAngolare_M2[indicePuntoDoppioContattoM2[i]])
   puntiY_M2FinalDoppioContatto.append(newAsseAlzata_M2[indicePuntoDoppioContattoM2[i]])

plt.plot(puntiX_M2FinalDoppioContatto,puntiY_M2FinalDoppioContatto, color='magenta', linewidth= 4, label='M2 NON RIPRODUCIBILE')
plt.legend()

# print(' derivata m1 x: \n')
# print(str(dxM1) + '\n')
# print(str(ddxM1) + '\n')
# print(' derivata m2 x: \n')
# print(str(dxM2) + '\n')
# print(str(ddxM2) + '\n')
# print(' derivata m1 y: \n')
# print(str(dyM1) + '\n')
# print(str(ddyM1) + '\n')
# print(' derivata m2 y: \n')
# print(str(dyM2) + '\n')
# print(str(ddyM2) + '\n')

# calcoliamo la fresa minima di taglio
raggioMinimoFresaM1 = []
raggioMinimoFresaM2 = []    


### RISCRIVI LA CAMMA IN BASE ALLA CURVATURA DELLA PUNTERIA 

indiciSezioniDoppioContattoM1 = trovaInizioFineSerie(indicePuntoDoppioContattoM1)
indiciSezioniDoppioContattoM2 = trovaInizioFineSerie(indicePuntoDoppioContattoM2)

print(' indici punti doppio contatto: \n')
print(str(indicePuntoDoppioContattoM1) + '\n')
print(str(indiciSezioniDoppioContattoM2) + '\n')



#### SEZIONE PRINTERIA PORTAMI VIA

#plt.xlabel("RAGGIO MINIMO CURVATURA M1 = " + str(raggioCruvaturaMinmoM1) + '\n' + "RAGGIO MINIMO CURVATURA M2 = " + str(raggioCruvaturaMinmoM2))

# plt.axvline(x=verticaleInizioFase1_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleInizioFase2_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleInizioFase3_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleInizioFase4_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleInizioFase5_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleInizioSalita_M1, color='r', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleIniziodiscesa_M1, color='m', linestyle='--', linewidth=2)
# plt.axvline(x=verticaleFineDiscesa_M1, color='m', linestyle='--', linewidth=2)


print("RAGGIO MINIMO CURVATURA M1 = " + str(raggioCruvaturaMinmoM1))
print("RAGGIO MINIMO CURVATURA M2 = " + str(raggioCruvaturaMinmoM2))

print("puntiCriticiAlzataM1Campionati \t = \t" + str(puntiCriticiAlzataM1Campionati))
print("puntiCriticiAlzataM2Campionati \t = \t" + str(puntiCriticiAlzataM2Campionati))
print("indiceEsternoPuntiCriticiCampionati \t = \t" + str(indiceEsternoPuntiCriticiCampionati))

#### SALVA I PUNTI IN UN .csv DA ESPORTARE IN SOLDIWORKS

with open("ZZZpuntiM1_SWformat.txt", "w") as fileM1:
    for i in range(0, sezioniCamma+1, 1):
       if i == sezioniCamma: #cucisci la fine con l'inizio
         pezzo1 = str(round(puntiX_M1Final[0],2))
         pezzo2 = str(round(puntiY_M1Final[0],2))
         pezzoNullo = str('0.0')
         fileM1.write(pezzo1 + '\t' + pezzo2 + '\t' + pezzoNullo + '\n')
       else:
         pezzo1 = str(round(puntiX_M1Final[i],2))
         pezzo2 = str(round(puntiY_M1Final[i],2))
         pezzoNullo = str('0.0')
         fileM1.write(pezzo1 + '\t' + pezzo2 + '\t' + pezzoNullo + '\n')

with open("ZZZpuntiM2_SWformat.txt", "w") as fileM2:
    for i in range(0, sezioniCamma+1, 1):
       if i == sezioniCamma:
         pezzo1 = str(round(puntiX_M2Final[0],2))
         pezzo2 = str(round(puntiY_M2Final[0],2))
         pezzoNullo = str('0.0')
         fileM2.write(pezzo1 + '\t' + pezzo2 + '\t' + pezzoNullo + '\n')
       else:
         pezzo1 = str(round(puntiX_M2Final[i],2))
         pezzo2 = str(round(puntiY_M2Final[i],2))
         pezzoNullo = str('0.0')
         fileM2.write(pezzo1 + '\t' + pezzo2 + '\t' + pezzoNullo + '\n')

with open("ZZZcentroCamma.txt", "w") as fileCentro:
  for i in range(0, sezioniCamma+1, 1):
    pezzo1 = str(round(puntiXstdMozzo[i],2))
    pezzo2 = str(round(puntiYstdMozzo[i],2))
    pezzoNullo = str('0.0')
    fileCentro.write(pezzo1 + '\t' + pezzo2 + '\t' + pezzoNullo + '\n')

with open("ZZZasse0.txt", "w") as fileAsseZero:
    fileAsseZero.write('0.0\t0.0\t0.0\n')
    raggio = str(int(raggioMinimoM1))
    fileAsseZero.write(raggio+'\t0.0\t0.0\n')

with open("ZZZpuntaFreccia.txt", "w") as fileFreccia:
    xpunta = str(int(raggioMinimoM1)+10)
    xsx = str(int(raggioMinimoM1)+5)
    xdx = str(int(raggioMinimoM1)+15)
    fileFreccia.write(xsx + '\t5.0\t0.0\n')
    fileFreccia.write(xpunta + '\t-10.0\t0.0\n')
    fileFreccia.write(xdx + '\t5.0\t0.0\n')

with open("ZZZcorpoFreccia.txt", "w") as fileCorpo:
    xCorpo = str(int(raggioMinimoM1)+10)
    fileCorpo.write(xCorpo + '\t10.0\t0.0\n')
    fileCorpo.write(xCorpo + '\t0.0\t0.0\n')

with open("ZZZdiagrammaAlzataM1.txt", "w") as fileAlzataM1:
    for i in range(0, sezioniCamma+1, 1):
       alzataYm1 = str(newAsseAlzata_M1[1])
       asseTemporale = str(newAsseAngolare_M1[t])
       fileAlzataM1.write(asseTemporale +'\n'+ alzataYm1)

with open("ZZZdiagrammaAlzataM2.txt", "w") as fileAlzataM2:
    for i in range(0, sezioniCamma+1, 1):
       alzataYm2 = str(newAsseAlzata_M2[1])
       asseTemporale = str(newAsseAngolare_M2[t])
       fileAlzataM2.write(asseTemporale +'\n'+ alzataYm2)


#### SALVA I PUNTI IN UN .txt PER LE LOOKUP TABLE DELLE CAMME

with open("ZZZlookuptable_M1.txt", "w") as lookUpTableM1:
    lookUpTableM1.write('DECIMI ANGOLO CAMMA' + '\t' + 'ALZATA PIATTELLO' + '\t' + 'ALZATA TEORICA RISPETTO PIATTELLO' + '\n')
    for i in range(0, sezioniCamma+1, 1):
       if i == sezioniCamma: #cucisci la fine con l'inizio
         angolo = str(round(newAsseAngolare_M1[0],2))
         alzataCamma = str(round(newAsseAlzata_M1[0],2))
         alzataSuPiattello = str(round(newAsseAlzata_M1[0] - 2, 2))
         lookUpTableM1.write(angolo + '\t' + alzataCamma + '\t' + alzataSuPiattello + '\n')
       else:
         angolo = str(round(newAsseAngolare_M1[i],2))
         alzataCamma = str(round(newAsseAlzata_M1[i],2))
         alzataSuPiattello = str(round(newAsseAlzata_M1[i] - 2, 2))
         lookUpTableM1.write(angolo + '\t' + alzataCamma + '\t' + alzataSuPiattello + '\n')

with open("ZZZlookuptable_M2.txt", "w") as lookUpTableM2:
    lookUpTableM2.write('DECIMI ANGOLO CAMMA' + '\t' + 'ALZATA PIATTELLO' + '\t' + 'ALZATA TEORICA RISPETTO PIATTELLO' + '\n')
    for i in range(0, sezioniCamma+1, 1):
       if i == sezioniCamma: #cucisci la fine con l'inizio
         angolo = str(round(newAsseAngolare_M2[0],2))
         alzataCamma = str(round(newAsseAlzata_M2[0],2))
         alzataSuPiattello = str(round(newAsseAlzata_M2[0] - 2, 2))
         lookUpTableM2.write(angolo + '\t' + alzataCamma + '\t' + alzataSuPiattello + '\n')
       else:
         angolo = str(round(newAsseAngolare_M2[i],2))
         alzataCamma = str(round(newAsseAlzata_M2[i],2))
         alzataSuPiattello = str(round(newAsseAlzata_M2[i] - 2, 2))
         lookUpTableM2.write(angolo + '\t' + alzataCamma + '\t' + alzataSuPiattello + '\n')



### COMANDO FINALE (TENERE ALLA FINE DI TUTTO SEMPRE CAZZO)
plt.show()
   
   





