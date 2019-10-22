from flask import Flask, render_template, url_for, session, request, redirect, flash, send_from_directory,make_response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import bcrypt
import os.path
import struct
TEMPLATE_DIR = os.path.abspath('/home/mariano/myproject/templates')
STATIC_DIR = os.path.abspath('/home/mariano/myproject/static')
UPLOAD_FOLDER = '/home/mariano/myproject/static/images/logo'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__ ,template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
mongo = PyMongo(app)
app.config['CACHE_TYPE'] = 'null'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "logo.jpg"))
          #  return redirect(url_for('uploaded_file',
           #                         filename=filename))
    return render_template('home.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/')
def index():
      session.database = mongo.db	
      if 'username' in session:
        return redirect(url_for('home'))
      else:
        return render_template('login.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/info')
def info():
	session.database = mongo.db
	info=mongo.db.societa.find_one({'_id': ObjectId("5d9c54beb22c95e715558dc5")})
	return render_template('info.html',tel=info['telefono'] ,mail=info['mail'], indirizzo=info['indirizzo'] ,est=info['est'], ovest=info['ovest'],immagine=info['immagine'])


@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.utenti
        existing_user = users.find_one({'user' : request.form['username']})
        if existing_user is None: 
            hashpass = bcrypt.hashpw(request.form['pw'].encode('utf-8'), bcrypt.gensalt())  
            users.insert({'user':request.form['username'],'password':hashpass,'nome':request.form['nome'],'cognome':request.form['cognome'],
	    'telefono':request.form['telefono'],'email':request.form['email']})
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
        if bcrypt.checkpw( request.form['pw'].encode('utf-8'), login_user['password']):
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

@app.route('/prenotazione/', methods=['POST','GET'] )
def prenotazione():
	session.database = mongo.db
	codice=request.form.get('bottone')
	tupla=mongo.db.campi.find_one({"_id":ObjectId(codice)})
	if request.method == 'POST':
		giorno=request.form['giorno']
		mese=request.form['mese']
		ora=request.form['orario']
	data=mongo.db.prenotazione.find_one({'id_campo':ObjectId(codice),'giorno':giorno,'mese':mese,'ora':ora})

	if data is None:
		mongo.db.prenotazione.insert({'user':session['username'],'id_campo':ObjectId(codice),
		'giorno':giorno,'mese':mese,'ora':ora})	
		flash("Prenotazione completata con successo")
		return redirect(url_for('prenota'))

	else:
          flash("Siamo spiacenti ma la data selezionata non risulta disponibile")  
          return redirect(url_for('prenota'))

@app.route('/prenota/')
def prenota():
	 session.database = mongo.db
	 if 'username' in session:
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
           #       return render_template('richiesta_campo.html')
	return render_template('richiesta_campo.html')

@app.route('/elimina',methods=['POST'] )
def elimina():
    codice=request.form.get('bottone')
    mongo.db.prenotazione.remove({'_id': ObjectId(codice)})		
    return redirect(url_for('agenda'))

@app.route('/galleria_calcio')
def galleria_calcio():		
        return render_template('galleria.html')

@app.route('/modifica')
def modifica():		
        return render_template('modifica.html')

@app.route('/aggiungi_nome',methods=['POST'])
def aggiungi_nome():	
	if request.method == 'POST':
			mongo.db.societa.update({},{'$set':{'nome':request.form['nomesoc']}})
	return 	redirect(url_for('modifica'))

@app.route('/aggiungi_indirizzo',methods=['POST'])
def aggiungi_indirizzo():	
	if request.method == 'POST':
			mongo.db.societa.update({},{'$set':{'indirizzo':request.form['indsoc']}})
	return 	redirect(url_for('modifica'))

@app.route('/aggiungi_telefono',methods=['POST'])
def aggiungi_telefono():	
	if request.method == 'POST':
			mongo.db.societa.update({},{'$set':{'telefono':request.form['telsoc']}})
	return 	redirect(url_for('modifica'))

@app.route('/aggiungi_email',methods=['POST'])
def aggiungi_email():	
	if request.method == 'POST':
			mongo.db.societa.update({},{'$set':{'mail':request.form['emailsoc']}})
	return 	redirect(url_for('modifica'))

@app.route('/modifica_campo',methods=['POST','GET'])
def modifica_campo():
	if request.method == 'POST':		 
			mongo.db.campi.insert({ 'tipo':request.form['gruppo1'],'riscaldamento':request.form['gruppo2'],
			'riflettori':request.form['gruppo3'],'irrigazione':request.form['gruppo4'],'stato':request.form['gruppo5'],'manutenzione':"false"})
			render_template('modifica_campo.html')
			flash("Modifica completata con successo")
			return redirect(url_for('modifica_campo'))	
	return 	render_template('modifica_campo.html')

@app.route('/aggiungi_logo')
def aggiungi_logo():
	return render_template('aggiungi_logo.html')

@app.route('/gestione_campi')
def gestione_campi():
    session.database = mongo.db
    return render_template('gestione_campi.html')

@app.route('/attiva_manutenzione',methods=['POST'])
def attiva_manutenzione():
    codice=request.form.get('attivo')
    mongo.db.campi.update({'_id': ObjectId(codice)} ,{ "$set":{'manutenzione':"true"}}) 		
    return redirect(url_for('gestione_campi'))

@app.route('/disattiva_manutenzione',methods=['POST'])
def disattiva_manutenzione():
    codice=request.form.get('disattivo')
    mongo.db.campi.update({'_id': ObjectId(codice)} ,{ "$set":{'manutenzione':"false"}}) 		
    return redirect(url_for('gestione_campi'))

app.secret_key = 'super secret key'

