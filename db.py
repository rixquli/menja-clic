import sqlite3
import string
import random

con = sqlite3.connect("db.db", check_same_thread=False)
cur = con.cursor()

def temp():
    res = cur.execute("""
                   
                   )
                """)
    con.commit()
    print(res)
    
def login(code_barre, password):
    res = cur.execute("SELECT COUNT(*) FROM client WHERE code_barre = ? AND mot_de_passe = ?", (code_barre, password))
    acheck = res.fetchone()
    return True if int(acheck[0]) > 0 else False 

def register(nom, prenom, mail, password):
    cur.execute("""
                        INSERT INTO Client (nom, prenom, mail, mot_de_passe) VALUES
                        (?,?,?,?)
                    """, (nom, prenom, mail, password))
    con.commit()

def isAdmin(code_barre):
    res = cur.execute("SELECT is_admin FROM client WHERE code_barre = ? ", (code_barre,))
    acheck = res.fetchone()
    return False if int(acheck[0]) == 0 else True 

"""
{
    "nom": "",
    "prenom": "",
    "solde": 0
}
"""
def get_account(code_barre):
    print(code_barre)
    res = cur.execute(
        """
        SELECT nom, prenom, solde 
            FROM client
        WHERE client.code_barre = ?
        """, (code_barre,))
    res = res.fetchone()
    
    if res == None:
        return None
    format = {
        "nom": res[0],
        "prenom": res[1],
        "solde": res[2],
    }
    print(format)
    return format

def get_historique(code_barre,password):
    res = cur.execute(
        """
        SELECT Historique.id_produit , Historique.quantite , Historique.date , Historique.heure
            FROM (client JOIN solde ON client.id = solde.id_eleve )
                JOIN Historique ON Historique.id_historique = Solde.id_historique
        WHERE code_barre = ? AND mot_de_passe = ?
        """, (code_barre, password))
    res = res.fetchall()
    if res == None:
        return None
    format_list=[]
    for ligne in res:  
        format_list.append({
            "id_produit": ligne[0],
            "quantite": ligne[1],
            "date": ligne[2],
            "heure": ligne[3],
        })
    return format_list

def get_produits():
    res = cur.execute(
        """
        SELECT *
            FROM Produit JOIN Stock ON Produit.id = Stock.id
        """)
    res = res.fetchall()
    if res == None:
        return None
    format_list=[]
    for ligne in res:  
        format_list.append({
            "id_produit": ligne[0],
            "nom": ligne[1],
            "prix": ligne[2],
            "classe": ligne[3],
            "durée": ligne[4],
            "image": ligne[5],
            "quantite": ligne[7],
        })
    return format_list

def get_total_liste_produits(liste_produits):
    total = 0
    for prod in liste_produits:
        prix = float(cur.execute("Select prix From Produit Where id = ?", (prod.id_produit,)).fetchone()[0])
        total += prix * prod.quantite
    return total

def get_reservation_client(username):
    res = cur.execute(
        """
        SELECT *
            FROM Reservation JOIN Produit ON Reservation.produit = Produit.id WHERE Reservation.client = ? 
        """, (username,))
    res = res.fetchall()
    if res == None:
        return None
    format_list=[]
    for ligne in res:  
        format_list.append({
            "id_produit": ligne[2],
            "nom": ligne[6],
            "prix": ligne[7],
            "classe": ligne[8],
            "image": ligne[10],
            "quantite": ligne[3],
            "date": ligne[4]
        })
    return format_list

def get_classe():
    res = cur.execute(
        """
        SELECT DISTINCT Classe.id, Classe.nom, Classe.couleur 
            FROM Classe JOIN produit ON Classe.id = produit.classe
        """)
    res = res.fetchall()
    if res == None:
        return None
    format_list=[]
    for ligne in res:  
        format_list.append({
            "id": ligne[0],
            "nom": ligne[1],
            "couleur": ligne[2],
        })
    return format_list

"""
liste_produits = {
    id_produit: "",
    quantite: 0
}
"""
def paiement(liste_produits, code_barre, password):
    total = get_total_liste_produits(liste_produits)
    
    # Regarder solde + stock
    solde = float(cur.execute(
        """
        SELECT solde.montant 
            FROM client JOIN solde ON client.id = solde.id_eleve 
        WHERE client.code_barre = ? AND client.mot_de_passe = ?
        """, (code_barre, password)).fetchone()[0])
    if solde < total:
        return False
    
    for prod in liste_produits:
        quantite_stock = int(cur.execute("Select quantite From Stock Where id = ?", (prod.id_produit)).fetchone()[0])
        if prod.quantite > quantite_stock:
            return False
        
    # Retrait d'argent
    cur.execute("Update Solde Set montant = ? Where id_eleve = ?", (solde-total,code_barre))
    
    # Mise à jour liste réservation
    
    
    # Mise à jour historique
    
    con.commit()
    return True
    

# A VERIFIER !!!! 
# S.O.S Théo
def ajouter_sous(compte_id, montant_ajoute):

    # Vérification de l'existence du compte
    cur.execute("SELECT solde FROM client WHERE id = ?", (compte_id,))
    solde_actuel = cur.fetchone()
    
    if solde_actuel:
        # Solde trouvé, on ajoute le montant
        nouveau_solde = solde_actuel[0] + montant_ajoute
        cur.execute("UPDATE client SET solde = ? WHERE id = ?", (nouveau_solde, compte_id))
        con.commit()
        print(f"Solde mis à jour avec succès : {nouveau_solde}€")
    else:
        print("Compte introuvable.")
        
        
# Fonction pour gérer le stock dans la base de données
def gerer_stock(produit_id, quantite=0):
    # Vérification de l'existence du produit
    cur.execute("SELECT quantite FROM stock WHERE id = ?", (produit_id,))
    produit = cur.fetchone()
    
    if produit:
        # Ajouter de la quantité au stock
        nouvelle_quantite = quantite
        cur.execute("UPDATE stock SET quantite = ? WHERE id = ?", (nouvelle_quantite, produit_id))
        print(f"{quantite} unités ont été ajoutées. Nouveau stock : {nouvelle_quantite} unités.")
    else:
        print("Produit non trouvé.")
    
    # Commit 
    con.commit()
    
def get_panier(code_barre):
    with sqlite3.connect("db.db") as con:
        res = cur.execute(
            """
            SELECT *
                FROM ProduitDansPanier JOIN Produit ON ProduitDansPanier.id_produit = Produit.id WHERE ProduitDansPanier.id_client = ? 
            """, (code_barre,))
        res = res.fetchall()
        if res == None:
            return None
        format_list=[]
        for ligne in res:  
            format_list.append({
                "id_produit": ligne[2],
                "nom": ligne[5],
                "prix": ligne[6],
                "classe": ligne[7],
                "image": ligne[9],
                "quantite": ligne[3]
            })
        return format_list

def get_panier_total(code_barre):
    panier = get_panier(code_barre)
    print(panier)
    total = 0
    for produit in panier:
        total += produit["prix"]*produit["quantite"]
    return total

def ajouter_panier(code_barre, id_produit, quantite):
    existe= True if int(cur.execute("SELECT COUNT(*) FROM ProduitDansPanier JOIN Client ON ProduitDansPanier.id_client = Client.code_barre WHERE ProduitDansPanier.id_produit = ? AND Client.code_barre = ?", (id_produit, code_barre)).fetchone()[0]) > 0 else False
    
    if existe:
        cur.execute("""
            UPDATE ProduitDansPanier
            SET quantite = quantite + ?
            WHERE id_produit = ? 
            AND id_client  = ?
        """, (quantite, id_produit, code_barre))
    else:
        cur.execute("""
                        INSERT INTO ProduitDansPanier (id_client, id_produit, quantite) VALUES
                        (?,?,?)
                    """, (code_barre, id_produit, quantite))
    con.commit()
    amount = cur.execute(
        """
        SELECT quantite
            FROM ProduitDansPanier WHERE id_produit = ? AND id_client  = ? 
        """, (id_produit,code_barre,))
    amount = amount.fetchone()
    if(amount[0] <= 0):
        cur.execute("DELETE FROM ProduitDansPanier WHERE id_produit = ? AND id_client  = ? ", (id_produit,code_barre,))
        con.commit()
    
    
#temp()
classe ={
    "Chaud": 1,
    "Froid": 2,
    "Boisson": 3,
}
def ajouter_produit(nom, prix, classe, image="",quantite = 0):
    cur.execute("""
            INSERT INTO Produit (nom, prix, classe,image, quantite) VALUES
                        (?,?,?,?,?)
        """, (nom, prix, classe,image, quantite))
    con.commit()
    
def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password
    
    
def ajouter_compte(prenom, nom, code):
    mdp = generate_password(8)
    cur.execute("""
            INSERT INTO client (prenom, nom, code_barre,mot_de_passe) VALUES
                        (?,?,?,?)
        """, (prenom, nom, code,mdp))
    con.commit()
    
# ajouter_compte("Anatole", "Sabater","054575")
# ajouter_compte("Théo", "Privat","054607")
# ajouter_compte("Anthon", "Nazon","054603")
# ajouter_compte("Marilou", "Benabides","054583")
# ajouter_compte("Pauline", "Aris","054517")
# ajouter_compte("Hugo", "Deflandre","054524")
# ajouter_compte("Samson", "Godart","054559")
#ajouter_produit("?", ?, classe["?"])
# exemple : ajouter_produit("test241", 72, classe["Chaud"])
