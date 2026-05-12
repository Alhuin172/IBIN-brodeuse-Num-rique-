# IBIN-brodeuse-Num-rique-
Programmes tournants sur la tres sainte BN

Vous trouverez les fichiers suivants :
  - logicielPython.py : programme python à executer sur un pc connecté à l'arduino de la BN
  - utils.py : complement du logiciel
  - recepteurArduino.ino : programme arduino à faire tourner sur l'arduino (j'aime enfoncer des portes ouvertes)
  - BN.csv : fichier de point permettant de broder les lettres "BN" grace au logiciel. Ce fichier doit etre dans un dossier "dossierDepot" lui meme enregistré dans le meme dossier que logicielPython.py (au besoin modifiez dans le programme python la variable "repertoire")

Explication de la communication globale : 
  le logiciel python ouvre un fichier CSV, le lit, le redimenssionne, lui fait tout plein de bisous. Apres cela il FC à l'arduino la commande "-150 -150" pour lui demander de faire une initialisation des axes. Puis il envoit les points un à un à l'arduino, il attend de recevoir "OK" avant de passer au pt suivant.
  Toutes les commandes FC à l'arduin sont dans des structures de 2 floats
  Les points envoyées à l'arduino sont des coordonnées en mm toutes positives. Le logiciel verifie les dépassements, l'arduino bloque le deplacement si la butée est touchée.


  Pour toutes questions pas trop pressées, contactez romain.peterlongo@laposte.net (alhuïn 172 Cl224)
