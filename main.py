from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_session import Session
import db
import datetime as dt
import os
from werkzeug.utils import secure_filename

# Initialisation de l'application
app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Dossier où les images seront stockées
UPLOAD_FOLDER = 'static/produits/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', "svg", "heic","heif", "hevc"}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Assurez-vous que ce dossier existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    # Redirige vers le tableau de bord si déjà logué
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validation des identifiants
        if db.login(username, password):
            session['username'] = username
            flash(f"Bienvenue, {username}!", "success")
            if db.isAdmin(username):
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('client'))
        else:
            flash("Identifiant ou mot de passe incorrect", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        mail = request.form['mail']
        password = request.form['password']
        passwordConfirm = request.form['password-confirm']
        if password != passwordConfirm:
            flash("Identifiant ou mot de passe incorrect", "danger")
            return render_template('register.html')
        # Validation des identifiants
        if db.register(nom, prenom, mail, password):
            flash(f"Bienvenue, {nom}!", "success")
            return render_template('register.html', message = "Votre mot de passe n'est pas validé")
            # if db.isAdmin(username):
            #     return redirect(url_for('dashboard'))
            # else:
            #     return redirect(url_for('client'))
        else:
            flash("Identifiant ou mot de passe incorrect", "danger")
    return render_template('register.html')

@app.route("/client")
def client():
    if 'username' in session:
        if db.isAdmin(session['username']):
            return redirect(url_for('dashboard'))
        produits = db.get_produits()
        user = db.get_account(session["username"])
        panier = db.get_panier(session['username'])
        panier_total= db.get_panier_total(session['username'])
        classe = db.get_classe()
        return render_template('client/index.html', produits = produits, user = user,panier = panier, panier_total = panier_total, classes = classe)
    return redirect(url_for('login'))

@app.route("/client/listereservation")
def client_reservation():
    if 'username' in session:
        if db.isAdmin(session['username']):
            return redirect(url_for('dashboard'))
        liste_reservation = db.get_reservation_client(session["username"])
        user = db.get_account(session["username"])
        panier = db.get_panier(session['username'])
        panier_total= db.get_panier_total(session['username'])
        return render_template('client/listereservation.html', liste_reservation = liste_reservation, user = user,panier = panier, panier_total = panier_total)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    classe = db.get_classe()
    produits = db.get_produits()
    if not db.isAdmin(session['username']):
        return redirect(url_for('client'))
    liste_reservation = db.get_reservations()
    return render_template('dashboard/listereservation.html', username=session['username'], produits = produits, classes = classe, liste_reservation=liste_reservation)

@app.route('/dashboard/stock')
def dashboardStockage():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
            return redirect(url_for('client'))
    produits= db.get_produits(False)
    classe = db.get_classe(True)
    return render_template('dashboard/stock.html', username=session['username'], produits=produits, classes=classe)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('login'))

@app.route('/api/changerstock', methods=['POST'])
def changer_stock():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
            return redirect(url_for('client'))
    id = request.json["id"]
    quantite = request.json["quantite"]
    db.gerer_stock(id, quantite)
    return "200"

@app.route('/api/getpanier', methods=['GET'])
def get_panier():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    # if db.isAdmin(session['username']):
            # return redirect(url_for('dashboard'))
    panier = db.get_panier(session['username'])
    panier_total= db.get_panier_total(session['username'])
    return {"panier": panier, "panier_total": panier_total}

@app.route('/api/ajouterpanier', methods=['POST'])
def ajouter_panier():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if db.isAdmin(session['username']):
            return redirect(url_for('dashboard'))
    id_produit = request.json["id"]
    print(request.json)
    quantite = request.json["quantite"]
    id_client = session["username"]
    db.ajouter_panier(id_client, id_produit, quantite)
    return "200"

@app.route('/api/validerpanier', methods=['POST'])
def valider_panier():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if db.isAdmin(session['username']):
            return redirect(url_for('dashboard'))
    id_client = session["username"]
    date = dt.datetime.now()
    return {"response":db.valider_panier(id_client, date)}

@app.route('/api/retirerreservation', methods=['POST'])
def retirer_reservation():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if db.isAdmin(session['username']):
            return redirect(url_for('dashboard'))
    id_resevation = request.json["id_reservation"]
    id_client = session["username"]
    return {"response":db.retirer_reservation(id_resevation, id_client)}

@app.route('/api/ajouterproduit', methods=['POST'])
def ajouter_produit():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
            return redirect(url_for('client'))
    nom = request.form["name"]
    prix = request.form["price"]
    category = request.form["category"]
    
    id = db.ajouter_produit(nom,prix,category, "")
    
    # Récupérer l'image envoyée avec le formulaire
    image = request.files.get('image')

    # Définir le chemin où l'image sera sauvegardée
    image_filename = None
    if image and allowed_file(image.filename):
        # Sécuriser le nom du fichier et récupérer son extension
        filename = secure_filename(image.filename)
        extension = filename.rsplit('.', 1)[1].lower()

        # Créer le chemin d'enregistrement de l'image (avec ID et extension)
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{id}.{extension}")
        
        # Sauvegarder l'image sur le serveur
        image.save(image_filename)
    
        db.set_produit_image(id,extension)
    
    return redirect(url_for('dashboardStockage'))

@app.route('/api/supprimerproduit', methods=['POST'])
def supprimer_produit():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
            return redirect(url_for('client'))
    print(request.json)
    id = request.json["id"]
    db.supprimer_produit(id)
    return "ok"

@app.route('/api/modifierproduit', methods=['POST'])
def modifier_produit():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
        return redirect(url_for('client'))

    # Récupération des données du produit
    id = request.form["id"]
    nom = request.form["nom"]
    prix = request.form["prix"]
    classe = request.form["classe"]

    # Récupérer l'image envoyée avec le formulaire
    image = request.files.get('image')

    # Définir le chemin où l'image sera sauvegardée
    image_filename = None
    if image and allowed_file(image.filename):
        # Sécuriser le nom du fichier et récupérer son extension
        filename = secure_filename(image.filename)
        extension = filename.rsplit('.', 1)[1].lower()

        # Créer le chemin d'enregistrement de l'image (avec ID et extension)
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{id}.{extension}")
        
        # Sauvegarder l'image sur le serveur
        image.save(image_filename)

    # Mettre à jour la base de données
    # Si une image a été téléchargée, on enregistre le chemin vers l'image
    if image_filename:
        db.modfifier_produit(id, nom, prix, classe, f"/static/produits/{id}.{extension}")
    else:
        db.modfifier_produit(id, nom, prix, classe, None)  
    return "ok"

    

if __name__ == '__main__':
    app.run(debug=True)