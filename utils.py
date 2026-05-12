import matplotlib.pyplot as plt
import serial, struct, time
import os
dimensionDeLEspaceDeBroderieX=150
dimensionDeLEspaceDeBroderieY=150
def lectureCSV(repertoire,nomfichier):
    #print(nomfichier)
    chemin=repertoire+"\\" + nomfichier
    fichier = open(chemin , "r")
    TEXT=fichier.readlines()
    fichier.close()     
    #print('text',len(TEXT))
    donneesBrutes=[]
    for ligne in TEXT[0: -1]:
        if len(ligne)>1:
            if ligne[1]=='*': 
                #print(ligne)
                l=ligne.split(",")
                #print(l)
                donneesBrutes.append((float(l[3][1:-1]),float(l[4][1:-2])))

    return donneesBrutes

def lectureDerniereBroderie(repertoire):
    chemin=repertoire+"\\derniereBroderie.txt"
    if os.path.exists(chemin):
        fichier = open(chemin , "r")
        TEXT=fichier.readlines()
        fichier.close()     
        #print('text',len(TEXT))
        donneesBrutes=[]
        for ligne in TEXT:
            if len(ligne)>1:
                l=ligne.split(",")
                donneesBrutes.append((float(l[0]),float(l[1])))
        #afficheGraphique(donneesBrutes)
        return donneesBrutes
    else:
        return []

def envoiePoint(ser,x, y):
    data = struct.pack('<ff', x, y)
    ser.write(data)
    #print(f"Envoyé: ({x}, {y})")

    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print("Arduino:", line)
            if line == "OK":
                break


def demandeInitialisationAxe(ser):
    time.sleep(1)
    data = struct.pack('<ff', -150, -150)  # Envoie des coordonnées hors de la zone de broderie pour signaler l'initialisation  
    ser.write(data)
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print("Arduino:", line)
            if line == "axe X initialise":
                break


def lancementBroderie(donnees,numeroPort,repertoire,canvas, facteur_affichage, dimension_plateau_x):
    fichier = open(repertoire+'\\derniereBroderie.txt', "w")
    autorisationPourBroder=True
    for coo in donnees:
        fichier.write(str(float(coo[0])) + "," + str(float(coo[1])) + "\n")
        if coo[0]>dimensionDeLEspaceDeBroderieX or coo[1]>dimensionDeLEspaceDeBroderieY or coo[0]<0 or coo[1]<0:
            print("Attention, il y a des points qui sortent du domaine de brodage : ",coo)
            autorisationPourBroder=False
    fichier.close()
    ser = serial.Serial(numeroPort, 115200, timeout=1)
    time.sleep(1)
    print("Connexion établie, initialisation des axes...")
    demandeInitialisationAxe(ser)
    if autorisationPourBroder:
        for coo in donnees[:172]:
            print(coo)
            envoiePoint(ser,float(coo[0]), float(coo[1]))
            supprimePremiereLigne(repertoire+'\\derniereBroderie.txt')
            modifie_dessin(canvas, coo, facteur_affichage, dimension_plateau_x)
    print("Broderie terminée.")
    ser.close()

def supprimePremiereLigne(chemin):
    try:
        if os.path.exists(chemin):
            with open(chemin, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) > 1:
                with open(chemin, 'w', encoding='utf-8') as f:
                    f.writelines(lines[1:])
        return True
    except KeyboardInterrupt:
        print("Opération interrompue par l'utilisateur.")
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression de la première ligne : {e}")
        return False
        

def afficheGraphique2(donnees,vitesse):
    fig, ax = plt.subplots()
    X=[coo[0] for coo in donnees]
    Y=[coo[1] for coo in donnees]
    xmin=min(X)-10
    xmax=max(X)+10
    ymin=min(Y)-10
    ymax=max(Y)+10
    for i in range(int(len(donnees)/vitesse)):####################manque les 9 derniers points
        if i%10==0:
            ax.clear()
            ax.set_xlim(xmin,xmax)
            ax.set_ylim(ymin,ymax)
            histX = X[0:i*vitesse]
            histY = Y[0:i*vitesse]
            ax.plot(histX, histY,'b-')
        ax.plot(X[i*vitesse], Y[vitesse*i],'r+')        
        plt.pause(0.001)
    ax.clear()
    ax.set_xlim(xmin,xmax)
    ax.set_ylim(ymin,ymax)
    ax.plot(X, Y,'b-')
    ax.plot(X[-1], Y[-1],'r+')
    plt.show()

def afficheGraphique1(donnees,v):#trop de points rouges
    X=[coo[0] for coo in donnees]
    Y=[coo[1] for coo in donnees]
    xmin=min(X)-10
    xmax=max(X)+10
    ymin=min(Y)-10
    ymax=max(Y)+10
    plt.xlim(xmin,xmax)
    plt.ylim(ymin,ymax)
    for i in range(int(len(donnees)/v)):####################manque les 9 derniers points
        plt.plot(X[v*i-v-1:v*i], Y[v*i-v-1:v*i],'b-')
        #plt.plot(X[0:i], Y[0:i],'b-')
        plt.pause(0.001)
    plt.show()

def afficheGraphique(donnees):
    plt.plot([coo[0] for coo in donnees], [coo[1] for coo in donnees],'b-')
    plt.axis([0,150,0,150])
    plt.show()



def lister_les_ports():
    # Récupère la liste de tous les ports série détectés
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        #print("Aucun port série détecté. Vérifiez vos branchements.")
        return ["pas de port détecté"]

#    print(f"--- {len(ports)} Port(s) détecté(s) ---")
    liste_ports = []
    
    for port in ports:
        # port.device est le nom (ex: COM3)
        # port.description est le nom du matériel (ex: Arduino Uno)
        #print(f"Port: {port.device} | Description: {port.description}")
        liste_ports.append(port.device)
        
    return liste_ports



def modifie_dessin(canvas, coordonnees, facteur_affichage, dimension_plateau_x):
    """
    Dessine un point sur le canevas passé en argument.
    canvas : objet tkinter.Canvas
    coordonnees : tuple (x, y)
    facteur_affichage : float
    dimension_plateau_x : float
    couleur : couleur du point
    """
    x = 50 + coordonnees[0] * facteur_affichage
    y = 50 + dimension_plateau_x * facteur_affichage - coordonnees[1] * facteur_affichage
    r = 3
    canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="")
    canvas.update()