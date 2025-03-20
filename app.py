from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_session import Session
import db

# Initialisation de l'application
app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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
    if not db.isAdmin(session['username']):
        return redirect(url_for('client'))
    return render_template('dashboard/index.html', username=session['username'])

@app.route('/dashboard/listereservation')
def dashboardReservation():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    classe = db.get_classe()
    produits = db.get_produits()
    if not db.isAdmin(session['username']):
        return redirect(url_for('client'))
    return render_template('dashboard/listereservation.html', username=session['username'], produits = produits, classes = classe)

@app.route('/dashboard/stock')
def dashboardStockage():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if not db.isAdmin(session['username']):
            return redirect(url_for('client'))
    produits= db.get_produits()
    return render_template('dashboard/stock.html', username=session['username'], produits=produits)

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
            # return redirect(url_for('dahsboard'))
    panier = db.get_panier(session['username'])
    panier_total= db.get_panier_total(session['username'])
    return {"panier": panier, "panier_total": panier_total}

@app.route('/api/ajouterpanier', methods=['POST'])
def ajouter_panier():
    if 'username' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))
    if db.isAdmin(session['username']):
            return redirect(url_for('dahsboard'))
    id_produit = request.json["id"]
    print(request.json)
    quantite = request.json["quantite"]
    id_client = session["username"]
    db.ajouter_panier(id_client, id_produit, quantite)
    return "200"
    

if __name__ == '__main__':
    app.run(debug=True)