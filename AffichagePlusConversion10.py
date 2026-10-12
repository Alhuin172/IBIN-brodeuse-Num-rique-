import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import os
import utils as u 
import serial.tools.list_ports
import struct
import threading
import os
import time as time


# --- Configuration Apparence ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

repertoire = r"C:\_Romain\Ensam\IBIN\IBIN Programmes\DossierDeDepot"
#repertoire = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "IBIN Programmes","DossierDeDepot"))
#print("Répertoire utilisé :", repertoire)

dimensionPlateauX = 95
dimensionPlateauY = 100


facteurAffichageLogiciel = 1/0.21

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BN'App - Interface de Contrôle")
        self.attributes('-fullscreen', True)
        self.state('zoomed')  # Pour forcer le plein écran sur Windows
        self.bind('<Escape>', self.miseEnGarde)

        # Variables globales internes
        self.donnees = []

        self.origineXMotif = 0
        self.origineYMotif = 0
        self.besoinDAide = False
    


        self.setup_ui()

    def setup_ui(self):
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1) # Panneau Gauche (Fichiers)
        self.grid_columnconfigure(1, weight=2) # Centre (Visualisation)
        self.grid_columnconfigure(2, weight=1) # Panneau Droit (Machine)
        self.grid_rowconfigure(0, weight=1)

        # --- PANNEAU GAUCHE (Fichiers) ---
        self.frame_left = ctk.CTkFrame(self, corner_radius=15)
        self.frame_left.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_left, text="📂 SÉLECTION MOTIF", font=("Clunsois", 18, "bold")).pack(pady=20)
        
        liste_fichiers = os.listdir(repertoire) if os.path.exists(repertoire) else ["Dossier introuvable"]
        self.combo_fichiers = ctk.CTkComboBox(self.frame_left, values=liste_fichiers, width=200, font=("Clunsois", 12))
        #self.combo_fichiers.bind("<<ComboboxSelected>>", self.creer_fleche_volante(0,100))
        self.combo_fichiers.pack(pady=10)

        ctk.CTkButton(self.frame_left, text="Valider Fichier", font=("Clunsois", 14), command=self.acceptation).pack(pady=10)
        
        self.label_dimXPourAffichage = ctk.CTkLabel(self.frame_left, text="Dim X : 0 mm", font=("Clunsois", 12))
        self.label_dimXPourAffichage.pack()
        self.label_dimYPourAffichage= ctk.CTkLabel(self.frame_left, text="Dim Y : 0 mm", font=("Clunsois", 12))
        self.label_dimYPourAffichage.pack()
        self.label_affichageDuNombreDePoints = ctk.CTkLabel(self.frame_left, text="Nombre de points : 0", font=("Clunsois", 12))
        self.label_affichageDuNombreDePoints.pack()
        self.label_affichageDistanceEntrePoints = ctk.CTkLabel(self.frame_left, text="Distance moyenne entre points : 0 mm", font=("Clunsois", 12))
        self.label_affichageDistanceEntrePoints.pack()

        ctk.CTkButton(self.frame_left, text="Simulation", fg_color="#2c3e50", font=("Clunsois", 14), command=lambda: self.simulation()).pack(pady=10)
        ctk.CTkButton(self.frame_left, text="Visualisation", fg_color="#2c3e50", font=("Clunsois", 14), command=lambda: u.afficheGraphique(self.donneesFinales)).pack(pady=10)
        
        
        #############################
        frame_redim = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        frame_redim.pack(pady=10, padx=10)

        # 2. Texte de gauche
        label_pref = ctk.CTkLabel(frame_redim, text="Redimensionnement : ", font=("Clunsois", 12))
        label_pref.pack(side="left")

        # 3. Zone remplissable (Entry)
        # On lie l'événement 'KeyRelease' pour appeler la fonction à chaque caractère tapé
        entree_redim = ctk.CTkEntry(frame_redim, width=60, placeholder_text="100")
        entree_redim.pack(side="left", padx=5)
        entree_redim.bind("<KeyRelease>", lambda event: self.miseAJour_redimensionnement(entree_redim.get()))

        # 4. Texte de droite
        label_suff = ctk.CTkLabel(frame_redim, text="% du motif original", font=("Clunsois", 12))
        label_suff.pack(side="left")

        ctk.CTkButton(self.frame_left, text="reprise de la derniere broderie", fg_color="#2c3e50", font=("Clunsois", 14), command=self.recuperationDernierTaf).pack(pady=10)
        ctk.CTkButton(self.frame_left, text="^^remonter l'aiguille^^", fg_color="#2c3e50", font=("Clunsois", 14), command=self.miniRemonterAiguille).pack(pady=10)
       
        ###########################
                
        """
        # --- ZONE CENTRALE (Canevas) ---
        # self.frame_center = ctk.CTkFrame(self, corner_radius=15)
        # self.frame_center.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_center = ctk.CTkFrame(self, corner_radius=15)
        self.frame_center.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_center, text="📍 POSITIONNEMENT PLATEAU", font=("Clunsois", 18, "bold")).pack(pady=10)
        
        self.canvas = tk.Canvas(self.frame_center, bg="#1a1a1a", width=100+dimensionPlateauX*facteurAffichageLogiciel, height=100+dimensionPlateauY*facteurAffichageLogiciel, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.rect_plateau = self.canvas.create_rectangle(50, 50, 50 + dimensionPlateauX*facteurAffichageLogiciel, 50 + dimensionPlateauY*facteurAffichageLogiciel, fill="#FFFFFF", outline="white")
        self.rect_motif = self.canvas.create_rectangle(50, 50, 150, 60, fill="red", state="hidden")

        self.slider_x = ctk.CTkSlider(self.frame_center, from_=0, to=100, command=self.miseAJour_x)
        self.slider_x.pack(fill="x", padx=50, pady=5)
        ctk.CTkLabel(self.frame_center, text="Axe X", font=("Clunsois", 11)).pack()

        # self.slider_y = ctk.CTkSlider(self.frame_center, from_=0, to=100, command=self.miseAJour_y)
        self.slider_y = ctk.CTkSlider(self.frame_slider_y_container, from_=100, to=0, orientation="vertical", command=self.miseAJour_y)
        self.slider_y.pack(fill="x", padx=50, pady=5)
        ctk.CTkLabel(self.frame_center, text="Axe Y", font=("Clunsois", 11)).pack()"""

        # --- ZONE CENTRALE (Canevas + Sliders) ---
        self.frame_center = ctk.CTkFrame(self, corner_radius=15)
        self.frame_center.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_center, text="📍 POSITIONNEMENT PLATEAU", font=("Clunsois", 18, "bold")).pack(pady=10)

        # Cadre horizontal utilisant la grille interne pour aligner Canvas et Slider Y
        self.frame_canvas_et_slider_y = ctk.CTkFrame(self.frame_center, fg_color="transparent")
        self.frame_canvas_et_slider_y.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_canvas_et_slider_y.grid_columnconfigure(0, weight=1) # Espace pour le Canvas
        self.frame_canvas_et_slider_y.grid_columnconfigure(1, weight=0) # Largeur fixe pour le Slider

        canvas_w = int(100 + dimensionPlateauX * facteurAffichageLogiciel)
        canvas_h = int(100 + dimensionPlateauY * facteurAffichageLogiciel)

        # Le canvas va dans la colonne 0 (à gauche)
        self.canvas = tk.Canvas(self.frame_canvas_et_slider_y, bg="#1a1a1a", width=canvas_w, height=canvas_h, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=(20, 0), sticky="nsew")

        self.rect_plateau = self.canvas.create_rectangle(50, 50, 50 + dimensionPlateauX*facteurAffichageLogiciel, 50 + dimensionPlateauY*facteurAffichageLogiciel, fill="#FFFFFF", outline="white")
        self.rect_motif = self.canvas.create_rectangle(50, 50, 150, 60, fill="red", state="hidden")

        self.slider_x = ctk.CTkSlider(self.frame_center, from_=0, to=100, command=self.miseAJour_x)
        self.slider_x.pack(fill="x", padx=50, pady=5)
        ctk.CTkLabel(self.frame_center, text="Axe X", font=("Clunsois", 11)).pack()

        # Le conteneur du Slider Y va dans la colonne 1 (à droite)
        self.frame_slider_y_container = ctk.CTkFrame(self.frame_canvas_et_slider_y, fg_color="transparent")
        self.frame_slider_y_container.grid(row=0, column=1, padx=20, sticky="ns")

        self.slider_y = ctk.CTkSlider(self.frame_slider_y_container, from_=0, to=100, orientation="vertical", command=self.miseAJour_y)
        self.slider_y.pack(fill="y", expand=True, pady=5)
        ctk.CTkLabel(self.frame_slider_y_container, text="Axe Y", font=("Clunsois", 11)).pack()

        ###############################################""

        # self.btnVisualiserMotif = ctk.CTkButton(self.frame_center, text="Visualiser Motif", fg_color="#2c3e50", font=("Clunsois", 14), command=self.dessineSurLogiciel)
        # self.btnVisualiserMotif.pack(pady=20)

        # --- PANNEAU DROIT (Contrôle) ---
        self.frame_right = ctk.CTkFrame(self, corner_radius=15)
        self.frame_right.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_right, text="🔌 MACHINE", font=("Clunsois", 18, "bold")).pack(pady=20)

        
        ports = u.lister_les_ports()
        self.combo_ports = ctk.CTkComboBox(self.frame_right, values=ports)
        self.combo_ports.pack(pady=10)

        self.btnLancerBroderie =ctk.CTkButton(self.frame_right, text="Lancer Broderie", fg_color="#27ae60", hover_color="#2ecc71", font=("Clunsois", 14), 
                      command=lambda: self.miniLancementBroderie(self.donneesFinales, self.combo_ports.get(),repertoire))
        self.btnLancerBroderie.pack(pady=20)

        

        # Pied de page
        #############################################################self.btn_aide = ctk.CTkButton(self.frame_right, text="Tutoriel Aide", command=self.ouvertureAide, font=("Clunsois", 12))
        ##############################################################self.btn_aide.pack(side="bottom", pady=10)
        ctk.CTkButton(self.frame_right, text="Crédits", command=self.ouvertureCredit, font=("Clunsois", 12), fg_color="transparent", border_width=1).pack(side="bottom", pady=5)
    
    def miniRemonterAiguille(self):
        try:
            u.remonterAiguille(self.combo_ports.get())
            messagebox.showinfo("Succès", "L'aiguille a été levée avec succès !")
        except Exception as e:
            print(f"Erreur lors du remontage de l'aiguille : {e}")
            messagebox.showerror("Erreur", f"Problème machine : {e}\nUn probleme probable est que vous n'avez pas selectionné de port dans le menu de droite.")
    
    def miniLancementBroderie(self, donnees, numeroPort, repertoire):
        # Sécurité : si le bouton est déjà désactivé, on ne fait rien
        if self.btnLancerBroderie.cget("state") == "disabled":
            return

        # On désactive immédiatement le bouton pour éviter le multi-clic
        self.btnLancerBroderie.configure(state="disabled", text="Broderie en cours...")

        # Affiche le nuage de points sur le canevas logiciel
        self.dessineSurLogiciel()

        # On définit une fonction interne qui sera exécutée par le Thread
        def run():
            try:
                # Appel de votre fonction de broderie (bloquante)
                
                u.lancementBroderie(donnees, numeroPort, repertoire, canvas=self.canvas, facteur_affichage=facteurAffichageLogiciel, dimension_plateau_x=dimensionPlateauX, dictionnaireDesCouleurs=self.dictionnaireDesCouleurs)
            except Exception as e:
                print(f"Erreur lors du lancement de la broderie : {e}")
                messagebox.showerror("Erreur", f"Problème machine : {e}")
            finally:
                # Une fois fini, on réactive le bouton via 'after' pour rester thread-safe avec Tkinter
                self.after(0, lambda: self.btnLancerBroderie.configure(state="normal", text="Lancer Broderie"))
                print("Broderie terminée.")

        # On lance la broderie en arrière-plan
        thread_broderie = threading.Thread(target=run, daemon=True)
        thread_broderie.start()


    def dessineSurLogiciel(self):
        # Efface les anciens points dessinés (sauf le plateau et le rectangle motif)
        items = self.canvas.find_all()
        self.canvas.itemconfigure(self.rect_motif, state="hidden")  # On cache le rectangle du motif pendant le dessin
        for item in items:
            if item not in [self.rect_plateau, self.rect_motif]:
                self.canvas.delete(item)

        # Dessine chaque point de donneesFinales
        if hasattr(self, 'donneesFinales') and self.donneesFinales:
            couleurPoint=self.dictionnaireDesCouleurs[0]
            for pt in self.donneesFinales:
                #print("pt", pt)
                if pt[2]!=0 and self.dictionnaireDesCouleurs.get(pt[2])[0]=="#":
                    couleurPoint=self.dictionnaireDesCouleurs[pt[2]]
                x = 50 + pt[0] * facteurAffichageLogiciel
                y = 100 + dimensionPlateauX * facteurAffichageLogiciel - pt[1] * facteurAffichageLogiciel
                r = 2  # rayon du point
                # if pt[2]!=0 and self.dictionnaireDesCouleurs.get(pt[2])=="JUMP":
                #     r=4
                #     print("saut")
                #     self.canvas.create_rectangle(x - r, y - r, x + r, y + r, fill="green", outline="")
                # else :
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=couleurPoint, outline="")
    
    """def modifieDessin(self,coordonneesDuDernierPoint):
        x = 50 + coordonneesDuDernierPoint[0] * facteurAffichageLogiciel
        y = 50 + dimensionPlateauX * facteurAffichageLogiciel - coordonneesDuDernierPoint[1] * facteurAffichageLogiciel
        r = 1  # rayon du point
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="")
        self.canvas.update()  # Force la mise à jour du canevas pour voir le changement
"""

    def recuperationDernierTaf(self):
        self.donneesFinales=u.lectureDerniereBroderie(repertoire)
        u.afficheGraphique(self.donneesFinales)
        questionRecuperation = messagebox.askyesno("Récupération", "Voulez-vous vraiment reprendre depuis ici ? \nAssurez-vous qu'un port série est sélectionné et que la machine est prête !")
        if questionRecuperation: self.miniLancementBroderie(self.donneesFinales, self.combo_ports.get(),repertoire)



    # --- Fonctions Logiques ---
    def acceptation(self):
        if self.besoinDAide:
            self.creer_fleche_volante(0, 100)
        nomfichier = self.combo_fichiers.get()
        self.donneesBrutes, self.dictionnaireDesCouleurs = u.lectureCSV(repertoire, nomfichier)
        
        min_x = min([c[0] for c in self.donneesBrutes])
        min_y = min([c[1] for c in self.donneesBrutes])
        max_y = max([c[1] for c in self.donneesBrutes])
        #print("min_x", min_x, "min_y", min_y, "max_y", max_y)
        
        self.donneesZero = [((c[0] - min_x)/10, (-c[1]+ max_y)/10, c[2]) for c in self.donneesBrutes]#on divise par 10 parce que inkscape est bourré
        self.donneesZoomees = self.donneesZero.copy()
        self.donneesFinales = self.donneesZero.copy()
        self.tailleMotifX = max([c[0] for c in self.donneesZero])-min([c[0] for c in self.donneesZero])
        self.tailleMotifY = max([c[1] for c in self.donneesZero])-min([c[1] for c in self.donneesZero])
        #print("self.tailleMotifX", self.tailleMotifX, "max_y", max_y)

        #self.donneesZero = [(c[0], max_y-c[1]) for c in self.donneesZero]#on fait une symétrie verticale pour que le motif soit dans le bon sens
       
        
        # print("verif")
        # print(self.tailleMotifX, max_y, dimensionPlateauX, dimensionPlateauY)
        if self.tailleMotifX<dimensionPlateauX and self.tailleMotifY<dimensionPlateauY:
            couleur="#27ae60"
        else:
            couleur="#e74c3c"
            fenetreWarning = tk.Tk()
            fenetreWarning.title("Attention dimensions")
            labelWarning= tk.Label(fenetreWarning, text="Attention, le motif dépasse les dimensions du plateau !\n Votre motif sera réduit pour s'adapter.", font=("Clunsois", 14))
            labelWarning.pack(pady=20)
            self.miseAJour_redimensionnement(90*min(dimensionPlateauX/self.tailleMotifX, dimensionPlateauY/self.tailleMotifY))
            self.label_affichageDuNombreDePoints.configure(text=f"Nombre de points : {len(self.donneesFinales)}", text_color=couleur)
            fenetreWarning.mainloop()
        #self.label_affichageDuNombreDePoints.configure(text=f"Nombre de points : {len(self.donneesFinales)}", text_color=couleur)
        self.label_dimXPourAffichage.configure(text=f"Dimension X : {int(self.tailleMotifX)} mm", text_color=couleur)
        self.label_dimYPourAffichage.configure(text=f"Dimension Y : {int(self.tailleMotifY)} mm", text_color=couleur)
        self.label_affichageDuNombreDePoints.configure(text=f"Nombre de points : {len(self.donneesFinales)}", text_color=couleur)
        self.label_affichageDistanceEntrePoints.configure(text=f"Distance moyenne entre points : {round(sum([((self.donneesFinales[i][0]-self.donneesFinales[i-1][0])**2+(self.donneesFinales[i][1]-self.donneesFinales[i-1][1])**2)**0.5 for i in range(1, len(self.donneesFinales))])/len(self.donneesFinales), 2)} mm", text_color=couleur)

        self.slider_x.configure(to=dimensionPlateauX - self.tailleMotifX)
        self.slider_y.configure(to=dimensionPlateauY - self.tailleMotifY)
        #self.canvas.itemconfigure(self.rect_motif, state="normal")
        #self.miseAJour_motif()
        self.dessineSurLogiciel()


    
    def miseAJour_redimensionnement(self, val):
        print("Redimensionnement à", val, "%")
        facteurReduction = float(val) / 100.0
        self.donneesZoomees = [(c[0] * facteurReduction, c[1] * facteurReduction, c[2]) for c in self.donneesZero]
        # Repositionne à l'origine
        self.origineXMotif = 0
        self.origineYMotif = 0
        self.donneesFinales = self.donneesZoomees.copy()
        self.tailleMotifX = max([c[0] for c in self.donneesFinales])
        self.tailleMotifY = max([c[1] for c in self.donneesFinales])
        self.slider_x.set(0)
        self.slider_y.set(0)
        self.slider_x.configure(to=dimensionPlateauX - self.tailleMotifX)
        self.slider_y.configure(to=dimensionPlateauY - self.tailleMotifY)
        self.label_dimXPourAffichage.configure(text=f"Dimension X : {int(self.tailleMotifX)} mm")
        self.label_dimYPourAffichage.configure(text=f"Dimension Y : {int(self.tailleMotifY)} mm")
        self.label_affichageDistanceEntrePoints.configure(text=f"Distance moyenne entre points : {round(sum([((self.donneesFinales[i][0]-self.donneesFinales[i-1][0])**2+(self.donneesFinales[i][1]-self.donneesFinales[i-1][1])**2)**0.5 for i in range(1, len(self.donneesFinales))])/len(self.donneesFinales), 2)} mm", text_color="#27ae60")

        self.canvas.itemconfigure(self.rect_motif, state="normal")
        #self.miseAJour_motif()
        #self.dessineSurLogiciel()
        self.dessineSurLogiciel()


    def miseAJour_x(self, val):
        self.origineXMotif = float(val)
        #print("origineX", val)
        #self.miseAJour_motif()
        self.donneesFinales = self.donneesZoomees.copy()
        self.donneesFinales = [(c[0]+self.origineXMotif, c[1]+self.origineYMotif, c[2]) for c in self.donneesFinales]
        self.dessineSurLogiciel()

    def miseAJour_y(self, val):
        self.origineYMotif = float(val)
        #self.miseAJour_motif()
        self.donneesFinales = self.donneesZoomees.copy()
        self.donneesFinales = [(c[0]+self.origineXMotif, c[1]+self.origineYMotif, c[2]) for c in self.donneesFinales]
        self.dessineSurLogiciel()

    # def miseAJour_motif(self):
    #     x1, y1 = 50 + self.origineXMotif*facteurAffichageLogiciel, 50 + dimensionPlateauX*facteurAffichageLogiciel - self.origineYMotif*facteurAffichageLogiciel - self.tailleMotifY*facteurAffichageLogiciel
    #     x2, y2 = x1 + self.tailleMotifX*facteurAffichageLogiciel, y1 + self.tailleMotifY*facteurAffichageLogiciel
    #     self.canvas.coords(self.rect_motif, x1, y1, x2, y2)


    def miseEnGarde(self, event=None):
        rep = messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?")
        if rep: self.destroy()

    def ouvertureCredit(self):
        win = ctk.CTkToplevel(self)
        win.title("Crédits")
        win.geometry("300x200")
        ctk.CTkLabel(win, text="Oneiros 25\nAlhuïn 172\nBeyrouth 145\nPen(arts) 150\nAlhuïn 172\nPersonne 179", font=("Clunsois", 16)).pack(expand=True)
    
    def simulation(self):
        items = self.canvas.find_all()
        self.canvas.itemconfigure(self.rect_motif, state="hidden")  # On cache le rectangle du motif pendant le dessin
        for item in items:
            if item not in [self.rect_plateau, self.rect_motif]:
                self.canvas.delete(item)

        # Dessine chaque point de donneesFinales
        if hasattr(self, 'donneesFinales') and self.donneesFinales:
            couleurPoint=self.dictionnaireDesCouleurs[0]
            for pt in self.donneesFinales:
                #print("pt", pt)
                if pt[2]!=0 and self.dictionnaireDesCouleurs.get(pt[2])[0]=="#":
                    couleurPoint=self.dictionnaireDesCouleurs[pt[2]]
                    messagebox.showinfo("Changement de couleur", f"Arrivé a ce stade, le programme fera pause et vous demandera de changer le fil pour la couleur suivante : {couleurPoint}")
                x = 50 + pt[0] * facteurAffichageLogiciel
                y = 50 + dimensionPlateauX * facteurAffichageLogiciel - pt[1] * facteurAffichageLogiciel
                r = 2  # rayon du point
                if pt[2]!=0 and self.dictionnaireDesCouleurs.get(pt[2])=="JUMP":
                    #time.sleep(2)
                    self.canvas.create_rectangle(x - r, y - r, x + r, y + r, fill="green", outline="")
                    reponse = messagebox.askyesno("Saut", "Ici il y aura un saut et un fil ira directement au point vert. \nCela ne sera pas tres esthetique, voulez-vous que le programme fasse une pause pour que vous puissiez couper le fil ?")
                    if not reponse:
                        pass
                    if reponse:
                        self.dictionnaireDesCouleurs[pt[2]]="PAUSE"
                elif pt[2]!=0 and self.dictionnaireDesCouleurs.get(pt[2])=="PAUSE":
                    #time.sleep(2)
                    self.canvas.create_rectangle(x - r, y - r, x + r, y + r, fill="green", outline="")
                    reponse = messagebox.askyesno("Pause", "Ici il y aura un saut et un fil ira directement au point vert. \nActuellement le programme s'arretera, mais cela vous imposera d'etre présent lors de cette pause. \nVoulez vous supprimer cette pause ?")
                    if not reponse:
                        pass
                    if reponse:
                        self.dictionnaireDesCouleurs[pt[2]]="JUMP"


                    print("saut")
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=couleurPoint, outline="")
                time.sleep(0.002)  # Simule le temps de broderie entre les points   S
                self.canvas.update()  # Force la mise à jour du canevas pour voir le changement
        

    
    ''''
    def ouvertureAide(self):
        # Création de la flèche volante qui sort de la fenêtre
        self.besoinDAide = True
        self.creer_fleche_volante(0, 85)
        messagebox.showinfo("Tuto", "Suivez la flèche rouge pour les étapes !")

    def creer_fleche_volante(self, x, y):
        self.fleche_win = tk.Toplevel(self)
        self.fleche_win.overrideredirect(True)
        self.fleche_win.attributes("-topmost", True)
        
        self.fleche_win.attributes("-transparentcolor", "white")
        self.fleche_win.geometry(f"100x100+{x}+{y}")
        
        canvas_f = tk.Canvas(self.fleche_win, width=100, height=100, bg="white", highlightthickness=0)
        canvas_f.pack()
        # On dessine une flèche qui pointe le bouton valider par exemple
        canvas_f.create_line(10, 50, 80, 50, arrow=tk.LAST, width=8, fill="red")
        
        # Animation simple
        #self.animer_fleche(0)

    def animer_fleche(self, step):
        if hasattr(self, 'fleche_win'):
            offset = 10 if step % 2 == 0 else -10
            # On récupère la position actuelle et on fait osciller
            curr_pos = self.fleche_win.winfo_x()
            self.fleche_win.geometry(f"+{curr_pos + offset}+400")
            self.after(500, lambda: self.animer_fleche(step + 1))
'''
if __name__ == "__main__":
    app = App()
    app.mainloop()


#####    tache a faire :
#au lancement fenetre pas fermer
#gerer couleurs
#affichage du graph est deforme

#à l ini verifier si aiguille haute ==> oui alors rien, ==> non alors message d erreur demandant àl'utilisateur d'en lever le fil
#bouton pour lever l'aiguille
#reprise d'origine à un endroit bizarre

#pour transformer en exe :
#pip install pyinstaller
#python -m PyInstaller --noconsole --onefile --icon=mon_icone.ico --name "Brodeuse Numérique" AffichagePlusConversion7.py