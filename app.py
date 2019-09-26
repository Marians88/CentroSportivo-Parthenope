from flask import Flask, render_template, url_for, session, request, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os.path
import bcrypt
import struct
TEMPLATE_DIR = os.path.abspath('/home/mariano/myproject/templates')
STATIC_DIR = os.path.abspath('/home/mariano/myproject/static')

app = Flask(__name__ ,template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)


@app.route('/')
def index():
      if 'username' in session:
        return redirect(url_for('home'))
      else:
        return render_template('login.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/info')
def info():
	return render_template('info.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.utenti
        existing_user = users.find_one({'user' : request.form['username']} ,)

        if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['pw'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'user' : request.form['username'], 'password' : hashpass})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
     	else:
             flash("Esiste gia un utente con questo username!")
             return redirect(url_for('register'))

    return render_template('registrazione.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.utenti
    login_user = users.find_one({'user' : request.form['username'] , })
    
    if login_user:
        if bcrypt.checkpw( request.form['pw'].encode('utf-8'), login_user['password'].encode('utf-8')):
	    	session['username'] = request.form['username']
            	return redirect(url_for('home'))
        else:
		flash("Username o password errati")
        	return redirect(url_for('index'))
    else:
	flash("Username o password errati")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/agenda')
def agenda():
    if 'username' in session:
	session.database = mongo.db
        return render_template('agenda.html')

@app.route('/prenota/', methods=['POST','GET'] )
def prenota():
	if request.method == 'POST':
		mongo.db.prenotazione.insert( {'user':session['username'],'campo':campo,'giorno':giorno,'mese':mese,'ora':ora,
		'nome':request.form['nome'] ,'cognome':request.form['cognome'],'indirizzo':request.form['indirizzo'],
		'telefono':request.form['telefono'],'email':request.form['email'] })	
		flash("Prenotazione completata con successo")	
        return render_template('prenota.html')

@app.route('/richiesta', methods=['POST','GET'])
def richiesta():
	data = mongo.db.prenotazione
	global campo
	campo=request.form.get('campo')
	global giorno
	giorno=request.form.get('giorno')
	global mese
	mese=request.form.get('mese')
	global ora
	ora=request.form.get('orario')
	if request.method == 'POST':
		data_user= data.find_one( {'$and':[{ 'campo': request.form.get('campo')},{'giorno':request.form.get('giorno')},
					  {'mese': request.form.get('mese')},{'ora':request.form.get('orario')} ] }
					 )
		if data_user is None:
			return redirect(url_for('prenota'))
		else:
		   flash("Siamo spiacenti ma la data selezionata non risulta disponibile")
        	   return render_template('richiesta_campo.html')
	return render_template('richiesta_campo.html')

@app.route('/elimina',methods=['POST'] )
def elimina():
	codice=request.form.get('bottone')
	
	mongo.db.prenotazione.remove({'_id': ObjectId(codice)})		
        return redirect(url_for('agenda'))

@app.route('/galleria_calcio')
def galleria_calcio():		
        return render_template('galleria.html')

app.secret_key = 'super secret key'

