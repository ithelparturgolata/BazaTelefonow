from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from flaskext.mysql import MySQL
import pymysql
from flask_login import login_required, current_user
from datetime import timedelta
from smsapi.client import SmsApiPlClient
from smsapi.exception import SmsApiException
from werkzeug.utils import secure_filename
import os
import urllib.request
from datetime import datetime
from views.index import index_blueprint
from centrala_management import centrala_manager_blueprint
from werkzeug.utils import secure_filename
from flask import send_from_directory
from PyPDF2 import PdfFileWriter, PdfFileReader
import pdfsplitter
import requests
import configparser
import base64

connection = mysql.connector.connect(host="localhost", port="3306",
                                     database="bazasm", user="root", password="Savakiran03")
cursor = connection.cursor()


app = Flask(__name__)
app.register_blueprint(index_blueprint)
app.register_blueprint(centrala_manager_blueprint)

app.permanent_session_lifetime = timedelta(minutes=100)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Savakiran03'
app.config['MYSQL_DATABASE_DB'] = 'bazasm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.secret_key = "super secret key"

# @app.route('/')
# def index():  # put application's code here
#     return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        message = "Błędny login"
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM uzytkownicy WHERE "
                       "username = %s AND password = %s", (username, password))
        record = cursor.fetchone()
        if record:
            session["loggedin"] = True
            session["username"] = record[1]
            return redirect(url_for("menu"))
        else:
            return redirect(url_for('index'))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/menu')
def menu():
    if "username" in session:
        username = session['username']
        return render_template("menu.html")
    else:
        return render_template("index.html")

############ Moduł Baza Telefonów ############
### Route indeks_paneltelefony ###
@app.route('/paneltelefony_menu')
def paneltelefony_menu():
    if "username" in session:
        username = session['username']
        return render_template("baza_telefonow_menu/index_paneltelefony.html")
    else:
        return render_template("index.html")

### Route telefony Administracja NW ###
@app.route('/nw')
def nw():
    if "username" in session:
        username = session['username']
        return render_template("baza_telefonow_menu/index_nw.html")
    else:
        return render_template("index.html")

### Route telefony Administracja NS ###
@app.route('/ns')
def ns():
    if "username" in session:
        username = session['username']
        return render_template("baza_telefonow_menu/index_ns.html")
    else:
        return render_template("index.html")

### Route telefony Administracja CE ###
@app.route('/ce')
def ce():
    if "username" in session:
        username = session['username']
        return render_template("baza_telefonow_menu/index_ce.html")
    else:
        return render_template("index.html")

### AJAX file main ###
@app.route("/ajaxfile", methods=["POST", "GET"])
def ajaxfile():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM mieszkaniec "
                               "ORDER BY indeks asc limit %s, %s;", (row, rowperpage))
                mieszkanieclist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM mieszkaniec WHERE indeks "
                    "LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                mieszkanieclist = cursor.fetchall()

            data = []
            for row in mieszkanieclist:
                data.append({
                    'indeks': row['indeks'],
                    'nazwakarty': row['nazwaKarty'],
                    'adresKarty': row['adresKarty'],
                    'klatkaSchodowa': row['klatkaSchodowa'],
                    'telefon': row['telefon'],
                    'administracja': row['administracja'],
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

### AJAX file NW telefony ###
@app.route("/ajaxfilenw", methods=["POST", "GET"])
def ajaxfilenw():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM mieszkaniec WHERE administracja='NW'"
                               "ORDER BY indeks asc limit %s, %s;", (row, rowperpage))
                mieszkanieclist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM mieszkaniec WHERE indeks "
                    "LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                mieszkanieclist = cursor.fetchall()

            data = []
            for row in mieszkanieclist:
                data.append({
                    'indeks': row['indeks'],
                    'nazwakarty': row['nazwaKarty'],
                    'adresKarty': row['adresKarty'],
                    'klatkaSchodowa': row['klatkaSchodowa'],
                    'telefon': row['telefon'],
                    'administracja': row['administracja'],
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

### AJAX file NS telefony ###
@app.route("/ajaxfilens", methods=["POST", "GET"])
def ajaxfilens():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

            if searchValue == '':
                cursor.execute("SELECT * FROM mieszkaniec WHERE administracja='NS'"
                               "ORDER BY indeks asc limit %s, %s;", (row, rowperpage))
                mieszkanieclist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM mieszkaniec WHERE indeks "
                    "LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                mieszkanieclist = cursor.fetchall()

            data = []
            for row in mieszkanieclist:
                data.append({
                    'indeks': row['indeks'],
                    'nazwakarty': row['nazwaKarty'],
                    'adresKarty': row['adresKarty'],
                    'klatkaSchodowa': row['klatkaSchodowa'],
                    'telefon': row['telefon'],
                    'administracja': row['administracja'],
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

### AJAX file CE telefony ###
@app.route("/ajaxfilece", methods=["POST", "GET"])
def ajaxfilece():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM mieszkaniec WHERE administracja='CE'"
                               "ORDER BY indeks asc limit %s, %s;", (row, rowperpage))
                mieszkanieclist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM mieszkaniec WHERE indeks "
                    "LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                mieszkanieclist = cursor.fetchall()

            data = []
            for row in mieszkanieclist:
                data.append({
                    'indeks': row['indeks'],
                    'nazwakarty': row['nazwaKarty'],
                    'adresKarty': row['adresKarty'],
                    'klatkaSchodowa': row['klatkaSchodowa'],
                    'telefon': row['telefon'],
                    'administracja': row['administracja'],
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


############ Moduł Panel SMS############
### Route indeks_panelsms ###
@app.route('/panelsms_menu')
def panelsms_menu():  # put application's code here
    if "username" in session:
        username = session['username']
        return render_template("index_panelsms.html")
    else:
        return render_template("index.html")

### Route panel kontrahent ###
@app.route('/panelsms_kontrahent')
def panelsms_kontrahent():  # put application's code here
    if "username" in session:
        username = session['username']
        return render_template("panelsms_kontrahent.html")
    else:
        return render_template("index.html")

### Route panel budynek ###
@app.route('/panelsms_budynek')
def panelsms_budynek():  # put application's code here
    if "username" in session:
        username = session['username']
        return render_template("panelsms_budynek.html")
    else:
        return render_template("index.html")

@app.route("/sendsms_budynek", methods=['POST'])
def sendsms_budynek():
    if "username" in session:
        username = session['username']
        if request.method=="POST":
            phone = request.form['phone']
            content = request.form['content']
            token = "rM5DsJlOvDkbGnYnHAn9f9GmpphT0ovOywqPaiLL"
            client = SmsApiPlClient(access_token=token)
            send_results = client.sms.send(to=phone, message=content, from_="SMBUDOWLANI")
            return redirect(url_for('panelsms_budynek'))
    else:
        return render_template("index.html")

@app.route("/sendsms_kontrahent", methods=['POST'])
def sendsms_kontrahent():
    if "username" in session:
        username = session['username']
        if request.method=="POST":
            phone = request.form['phone']
            content = request.form['content']
            token = "rM5DsJlOvDkbGnYnHAn9f9GmpphT0ovOywqPaiLL"
            client = SmsApiPlClient(access_token=token)
            send_results = client.sms.send(to=phone, message=content, from_="SMBUDOWLANI")
            return redirect(url_for('panelsms_kontrahent'))
    else:
        return render_template("index.html")

### AJAX file SMS budynek ###
@app.route("/ajaxfilepanelsms_budynek", methods=["POST", "GET"])
def ajaxfilepanelsms_budynek():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from blok")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from blok "
                           "WHERE idBudynek LIKE %s OR SymbolBudynku LIKE %s OR Ulica LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM blok "
                               "ORDER BY idBudynek asc limit %s, %s;", (row, rowperpage))
                bloklist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM blok WHERE idBudynek "
                    "LIKE %s OR SymbolBudynku LIKE %s OR Ulica LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                bloklist = cursor.fetchall()

            data = []
            for row in bloklist:
                data.append({
                    'test': row['test'],
                    'idBudynek': row['idBudynek'],
                    'SymbolBudynku': row['SymbolBudynku'],
                    'SymbolOsiedla': row['SymbolOsiedla'],
                    'Ulica': row['Ulica'],
                    'SymbolNieruchomosci': row['SymbolNieruchomosci'],
                    'Numery': row['Numery']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

### AJAX file SMS kontrahent ###
@app.route("/ajaxfilepanelsms_kontrahent", methods=["POST", "GET"])
def ajaxfilepanelsms_kontrahent():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE id LIKE %s OR nazwaKarty LIKE %s OR indeks LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM mieszkaniec "
                               "ORDER BY id asc limit %s, %s;", (row, rowperpage))
                bloklist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM mieszkaniec WHERE id "
                    "LIKE %s OR nazwaKarty LIKE %s OR indeks LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                bloklist = cursor.fetchall()

            data = []
            for row in bloklist:
                data.append({
                    'test': row['test'],
                    'id': row['id'],
                    'indeks': row['indeks'],
                    'nazwaKarty': row['nazwaKarty'],
                    'adresKarty': row['adresKarty'],
                    'klatkaSchodowa': row['klatkaSchodowa'],
                    'telefon': row['telefon']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



















@app.route("/ajaxfilepanelmieszkanca", methods=["POST", "GET"])
def ajaxfilepanelmieszkanca():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from budynek")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from budynek "
                           "WHERE indeksBudynek LIKE %s OR ulicaBudynek LIKE %s ",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM budynek "
                               "ORDER BY idBudynek asc limit %s, %s;", (row, rowperpage))
                bloklist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM budynek WHERE idBudynek "
                    "LIKE %s OR indeksBudynek LIKE %s OR ulicaBudynek LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                bloklist = cursor.fetchall()

            data = []
            for row in bloklist:
                data.append({
                    'idBudynek': row['idBudynek'],
                    'indeksBudynek': row['indeksBudynek'],
                    'ulicaBudynek': row['ulicaBudynek'],
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()




# @app.route('/insert', methods = ['POST'])
# def insert():
#     if request.method == "POST":
#         flash("Data Inserted Successfully")
#         indeks_budynek = request.form['indeks_budynek']
#         ulica = request.form['ulica']
#         symbol_osiedla = request.form['symbol_osiedla']
#         connection = mysql.connect()
#         cursor = connection.cursor()
#         cursor.execute("INSERT INTO dokumenty (indeks_budynek, ulica, symbol_osiedla) VALUES (%s, %s, %s)", (indeks_budynek, ulica, symbol_osiedla))
#         connection.commit()
#         return redirect(url_for('dokumenty'))

############ Moduł Panel Mieszkańca ############
### Route panel menu ###
@app.route('/panelmieszkanca_menu')
def panelmieszkanca_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM budynek")
        data = cursor.fetchall()
        cursor.close()
        return render_template('index_panelmieszkanca.html', budynek=data)
    else:
        return render_template("index.html")

############ Moduł Panel Mieszkańca ############
### Panel Mieszkanaca moduły UPDATE ###
@app.route('/update_panelmieszkanca_remonty',methods=['POST','GET'])
def update_panelmieszkanca_remonty():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        # indeksBudynek = request.form['indeksBudynek']
        pracaRemonty = "{}".format(request.form['pracaRemonty'])
        wykonawcaRemonty = "{}".format(request.form['wykonawcaRemonty'])
        startRemonty = request.form['startRemonty']
        koniecRemonty = request.form['koniecRemonty']
        uwagiRemonty = "{}".format(request.form['uwagiRemonty'])
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET pracaRemonty=%s, wykonawcaRemonty=%s, startRemonty=%s, koniecRemonty=%s, uwagiRemonty=%s WHERE idBudynek=%s ", (pracaRemonty, wykonawcaRemonty, startRemonty, koniecRemonty, uwagiRemonty, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca_fundusz',methods=['POST','GET'])
def update_panelmieszkanca_fundusz():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        # indeksBudynek = request.form['indeksBudynek']
        zadluzenieBudynek = request.form['zadluzenieBudynek']
        funduszBudynek = request.form['funduszBudynek']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET zadluzenieBudynek=%s, funduszBudynek=%s WHERE idBudynek=%s ", (zadluzenieBudynek, funduszBudynek, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca_energetyka',methods=['POST','GET'])
def update_panelmieszkanca_energetyka():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        # indeksBudynek = request.form['indeksBudynek']
        terminPodzielniki = "{}".format(request.form['terminPodzielniki'])
        terminLegalizacja = "{}".format(request.form['terminLegalizacja'])
        uwagiLegalizacja = "{}".format(request.form['uwagiLegalizacja'])
        wymianaBaterii = "{}".format(request.form['wymianaBaterii'])
        uwagiWymianaBaterii = "{}".format(request.form['uwagiWymianaBaterii'])
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET terminPodzielniki=%s, terminLegalizacja=%s, uwagiLegalizacja=%s, wymianaBaterii=%s, uwagiWymianaBaterii=%s WHERE idBudynek=%s ", (terminPodzielniki, terminLegalizacja, uwagiLegalizacja, wymianaBaterii, uwagiWymianaBaterii, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca_przeglady',methods=['POST','GET'])
def update_panelmieszkanca_przeglady():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        # indeksBudynek = request.form['indeksBudynek']
        pkominyPrzeglady = request.form['pkominyPrzeglady']
        pgazPrzeglady = request.form['pgazPrzeglady']
        ptechnicznyPrzeglady = request.form['ptechnicznyPrzeglady']
        pelektrykaPrzeglady = request.form['pelektrykaPrzeglady']
        pogolnyPrzeglady = request.form['pogolnyPrzeglady']
        akominyPrzeglady = request.form['akominyPrzeglady']
        agazPrzeglady = request.form['agazPrzeglady']
        atechnicznyPrzeglady = request.form['atechnicznyPrzeglady']
        aelektrykaPrzeglady = request.form['aelektrykaPrzeglady']
        aogolnyPrzeglady = request.form['aogolnyPrzeglady']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET pkominyPrzeglady=%s, pgazPrzeglady=%s, ptechnicznyPrzeglady=%s, pelektrykaPrzeglady=%s, pogolnyPrzeglady=%s, akominyPrzeglady=%s, agazPrzeglady=%s, atechnicznyPrzeglady=%s, aelektrykaPrzeglady=%s, aogolnyPrzeglady=%s WHERE idBudynek=%s ", (pkominyPrzeglady, pgazPrzeglady, ptechnicznyPrzeglady, pelektrykaPrzeglady, pogolnyPrzeglady, akominyPrzeglady, agazPrzeglady, atechnicznyPrzeglady, aelektrykaPrzeglady, aogolnyPrzeglady, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca_infoogolne',methods=['POST','GET'])
def update_panelmieszkanca_infoogolne():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        # indeksBudynek = request.form['indeksBudynek']
        infoOgolne = "{}".format(request.form['infoOgolne'])
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET infoOgolne=%s WHERE idBudynek=%s ", (infoOgolne, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

############ Moduł DK Modraczek ############
### Route indeks_panelmodraczek ###
@app.route('/panelmodraczek_menu')
def panelmodraczek_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen")
        data = cursor.fetchall()
        cursor.close()
        return render_template('index_panelmodraczek.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/klubmalucha_menu')
def klubmalucha_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='KlubMalucha'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='KlubMalucha'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"
        cursor.close()
        return render_template('index_klubmalucha.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")


@app.route('/zajecia_menu')
def zajecia_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Zajecia'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='Zajecia'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"
        cursor.close()
        return render_template('index_zajecia.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/rytmika_menu')
def rytmika_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Rytmika'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='Rytmika'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_rytmika.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/pianino_menu')
def pianino_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Pianino'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='Pianino'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_pianino.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/cyrkowe_menu')
def cyrkowe_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='WarsztatyCyrkowe'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='WarsztatyCyrkowe'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_cyrkowe.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/sowka_menu')
def sowka_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='MadraSowka'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='MadraSowka'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_sowka.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/plastyka_menu')
def plastyka_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Plastyka'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='Plastyka'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_plastyka.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/angielski_menu')
def angielski_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='JezykAngielski'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='JezykAngielski'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_angielski.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/niemiecki_menu')
def niemiecki_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='JezykNiemiecki'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='JezykNiemiecki'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_niemiecki.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/kurs8klangielski_menu')
def kurs8klangielski_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='kurs8klangielski'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='kurs8klangielski'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_8klangielski.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/kurs8klpolski_menu')
def kurs8klpolski_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='kurs8klpolski'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='kurs8klpolski'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_8klpolski.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

@app.route('/kurs8klmatematyka_menu')
def kurs8klmatematyka_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='kurs8klmatematyka'")
        data = cursor.fetchall()
        cursor.execute("SELECT TelefonMatka, TelefonOjciec FROM uczen WHERE GrupaUczen='kurs8klmatematyka'")
        dataPhone = cursor.fetchall()
        phone = ""
        for i in dataPhone:
            if (i[0] != ""):
                phone += f"{i[0]},"
            if (i[1] != ""):
                phone += f"{i[1]},"

        cursor.close()
        return render_template('index_8klmatematyka.html', uczen=data, dataPhone=phone[:-1])
    else:
        return render_template("index.html")

############ Moduł DK Modraczek ############
### Poszczególne SELECT do modułów ###
@app.route('/select_klubmalucha',methods=['POST','GET'])
def select_klubmalucha():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Klub Malucha'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('klubmalucha_menu'))
    else:
        return render_template("index.html")

@app.route('/select_zajecia',methods=['POST','GET'])
def select_zajecia():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Zajecia'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('zajecia_menu'))
    else:
        return render_template("index.html")

@app.route('/select_rytmika',methods=['POST','GET'])
def select_rytmika():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Rytmika'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('rytmika_menu'))
    else:
        return render_template("index.html")

@app.route('/select_pianino',methods=['POST','GET'])
def select_pianino():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Pianino'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('pianino_menu'))
    else:
        return render_template("index.html")

@app.route('/select_cyrkowe',methods=['POST','GET'])
def select_cyrkowe():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='WarsztatyCyrkowe'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('cyrkowe_menu'))
    else:
        return render_template("index.html")

@app.route('/select_sowka',methods=['POST','GET'])
def select_sowka():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='MadraSowka'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('sowka_menu'))
    else:
        return render_template("index.html")

@app.route('/select_plastyka',methods=['POST','GET'])
def select_plastyka():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Plastyka'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('plastyka_menu'))
    else:
        return render_template("index.html")

@app.route('/select_angielski',methods=['POST','GET'])
def select_angielski():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='JezykAngielski'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('angielski_menu'))
    else:
        return render_template("index.html")

@app.route('/select_niemiecki',methods=['POST','GET'])
def select_niemiecki():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='JezykNiemiecki'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('niemiecki_menu'))
    else:
        return render_template("index.html")

@app.route('/select_8klangielski',methods=['POST','GET'])
def select_8klangielski():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Kurs8klangielski'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('kurs8klangielski_menu'))
    else:
        return render_template("index.html")

@app.route('/select_8klpolski',methods=['POST','GET'])
def select_8klpolski():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Kurs8klpolski'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('kurs8klpolski_menu'))
    else:
        return render_template("index.html")

@app.route('/select_8klmatematyka',methods=['POST','GET'])
def select_8klmatematyka():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uczen WHERE GrupaUczen='Kurs8klmatematyka'")
        data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('kurs8klmatematyka_menu'))
    else:
        return render_template("index.html")

############ Moduł DK Modraczek ############
### Poszczególne UPDATE do modułów ###
@app.route('/update_klubmalucha',methods=['POST','GET'])
def update_klubmalucha():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('klubmalucha_menu'))
    else:
        return render_template("index.html")

@app.route('/update_zajecia',methods=['POST','GET'])
def update_zajecia():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('zajecia_menu'))
    else:
        return render_template("index.html")

@app.route('/update_rytmika',methods=['POST','GET'])
def update_rytmika():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('rytmika_menu'))
    else:
        return render_template("index.html")

@app.route('/update_pianino',methods=['POST','GET'])
def update_pianino():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('pianino_menu'))
    else:
        return render_template("index.html")

@app.route('/update_cyrkowe',methods=['POST','GET'])
def update_cyrkowe():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('cyrkowe_menu'))
    else:
        return render_template("index.html")

@app.route('/update_sowka',methods=['POST','GET'])
def update_sowka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('sowka_menu'))
    else:
        return render_template("index.html")

@app.route('/update_plastyka',methods=['POST','GET'])
def update_plastyka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('plastyka_menu'))
    else:
        return render_template("index.html")

@app.route('/update_angielski',methods=['POST','GET'])
def update_angielski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('angielski_menu'))
    else:
        return render_template("index.html")

@app.route('/update_niemiecki',methods=['POST','GET'])
def update_niemiecki():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('niemiecki_menu'))
    else:
        return render_template("index.html")

@app.route('/update_8klangielski',methods=['POST','GET'])
def update_8klangielski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('kurs8klangielski_menu'))
    else:
        return render_template("index.html")

@app.route('/update_8klpolski',methods=['POST','GET'])
def update_8klpolski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('kurs8klpolski_menu'))
    else:
        return render_template("index.html")

@app.route('/update_8klmatematyka',methods=['POST','GET'])
def update_8klmatematyka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE uczen SET ImieUczen=%s, NazwiskoUczen=%s, DataUrodzenia=%s, AdresUczen=%s, ImieMatka=%s, PeselMatka=%s, TelefonMatka=%s, EmailMatka=%s, ImieOjciec=%s, PeselOjciec=%s, TelefonOjciec=%s, EmailOjciec=%s, PoczatekZajec=%s, KoniecZajec=%s WHERE idUczen=%s ",
                       (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, idUczen))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('kurs8klmatematyka_menu'))
    else:
        return render_template("index.html")

############ Moduł DK Modraczek ############
### Poszczególne INSERTY do modułów ###
@app.route('/insert_klubmalucha', methods = ['POST'])
def insert_klubmalucha():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('klubmalucha_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_zajecia', methods = ['POST'])
def insert_zajecia():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('zajecia_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_rytmika', methods = ['POST'])
def insert_rytmika():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('rytmika_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_pianino', methods = ['POST'])
def insert_pianino():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('pianino_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_cyrkowe', methods = ['POST'])
def insert_cyrkowe():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('cyrkowe_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_sowka', methods = ['POST'])
def insert_sowka():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('sowka_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_plastyka', methods = ['POST'])
def insert_plastyka():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('plastyka_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_angielski', methods = ['POST'])
def insert_angielski():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('angielski_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_niemiecki', methods = ['POST'])
def insert_niemiecki():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('niemiecki_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_8klangielski', methods = ['POST'])
def insert_8klangielski():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('kurs8klangielski_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_8klmatematyka', methods = ['POST'])
def insert_8klmatematyka():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('kurs8klmatematyka_menu'))
    else:
        return render_template("index.html")

@app.route('/insert_8klpolski', methods = ['POST'])
def insert_8klpolski():
    if request.method == "POST":
        ImieUczen = request.form['ImieUczen']
        NazwiskoUczen = request.form['NazwiskoUczen']
        DataUrodzenia = request.form['DataUrodzenia']
        AdresUczen = request.form['AdresUczen']
        ImieMatka = request.form['ImieMatka']
        PeselMatka = request.form['PeselMatka']
        TelefonMatka = request.form['TelefonMatka']
        EmailMatka = request.form['EmailMatka']
        ImieOjciec = request.form['ImieOjciec']
        PeselOjciec = request.form['PeselOjciec']
        TelefonOjciec = request.form['TelefonOjciec']
        EmailOjciec = request.form['EmailOjciec']
        PoczatekZajec = request.form['PoczatekZajec']
        KoniecZajec = request.form['KoniecZajec']
        GrupaUczen = request.form['GrupaUczen']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uczen (ImieUczen, NazwiskoUczen, DataUrodzenia, AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka, ImieOjciec, PeselOjciec, TelefonOjciec, "
                       "EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ImieUczen, NazwiskoUczen, DataUrodzenia,
                                                                                                                                    AdresUczen, ImieMatka, PeselMatka, TelefonMatka, EmailMatka,
                                                                                                                                    ImieOjciec, PeselOjciec, TelefonOjciec, EmailOjciec, PoczatekZajec, KoniecZajec, GrupaUczen))
        connection.commit()
        return redirect(url_for('kurs8klpolski_menu'))
    else:
        return render_template("index.html")

############ Moduł DK Modraczek ############
### SMSy ###
@app.route('/sms_modraczek',methods=['POST','GET'])
def sms_modraczek():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        flash("SMS wysłany")
        return redirect(url_for('panelmodraczek_menu'))
    else:
        return render_template("index.html")

@app.route('/panelsms_modraczek')
def panelsms_modraczek():
    if "username" in session:
        username = session['username']
        return render_template("panelsms_modraczek.html")
    else:
        return render_template("index.html")

############ Moduł DK Modraczek ############
### Poszczególne SMSY do modułów ###
@app.route('/sms_klubmalucha',methods=['POST','GET'])
def sms_klubmalucha():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_klubmalucha.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_zajecia',methods=['POST','GET'])
def sms_zajecia():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_zajecia.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_rytmika',methods=['POST','GET'])
def sms_rytmika():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_rytmika.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_pianino',methods=['POST','GET'])
def sms_pianino():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_pianino.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_cyrkowe',methods=['POST','GET'])
def sms_cyrkowe():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_cyrkowe.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_sowka',methods=['POST','GET'])
def sms_sowka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_sowka.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_plastyka',methods=['POST','GET'])
def sms_plastyka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_plastyka.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_angielski',methods=['POST','GET'])
def sms_angielski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_angielski.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_niemiecki',methods=['POST','GET'])
def sms_niemiecki():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_niemiecki.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_8klangielski',methods=['POST','GET'])
def sms_8klangielski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_8klangielski.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_8klpolski',methods=['POST','GET'])
def sms_8klpolski():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_8klpolski.html', uczen=data)
    else:
        return render_template("index.html")

@app.route('/sms_8klmatematyka',methods=['POST','GET'])
def sms_8klmatematyka():
    if request.method == 'POST':
        idUczen = request.form['idUczen']
        phone = request.form['phone']
        content = request.form['content']
        data = cursor.fetchall()
        token = "oYeJUXpAF7Iu3l0tVHoxaxL4cEGSKUAbQKedJK6q"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="DKMODRACZEK")
        cursor.close()
        return render_template('index_8klmatematyka.html', uczen=data)
    else:
        return render_template("index.html")

############ Moduł Splitter PDF ############
@app.route("/upload",methods=['POST','GET'])
def upload():
    if request.method == "POST":
        try:
            f=request.files['file']
            customFolder=request.form['customFolder']

            if customFolder[-1] != "\\":
                customFolder += "\\"

            customSplitPages = int(request.form['customSplitPages'])

            if customSplitPages == 0:
                customSplitPages = int(request.form['customSplitPagesDefined'])

            upload.file_name=f.filename
            f.save(f"{customFolder}{upload.file_name}")
            data = pdfsplitter.splitPDF(f"{customFolder}{upload.file_name}", customSplitPages)

            return render_template("file_upload.html", data=[request.method, data, customFolder, customSplitPages])
        except Exception as e:
            return render_template("file_upload.html", data=[request.method, e])
    else:
        return render_template("file_upload.html", data=[request.method])

############ Moduł Pogoda ############
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if "username" in session:
        username = session['username']
        if request.method == 'POST':
            city_name = request.form['name']

            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=pl&APPID=2213901a0c8514848e49f8c2433e97c9'
            response = requests.get(url.format(city_name)).json()

            temp = response['main']['temp']
            weather = response['weather'][0]['description']
            min_temp = response['main']['temp_min']
            max_temp = response['main']['temp_max']
            pressure = response['main']['pressure']
            humidity = response['main']['humidity']
            speed = response['wind']['speed']
            lon = response['coord']['lon']
            lat = response['coord']['lat']
            # rain = response['rain']['1h']

            icon = response['weather'][0]['icon']
            return render_template('weather_menu/weather.html', temp=temp, weather=weather, min_temp=min_temp, max_temp=max_temp,
                                   icon=icon, city_name=city_name, pressure=pressure, humidity=humidity, speed=speed, lon=lon, lat=lat)
        else:
            return render_template('weather_menu/weather.html')

########### Moduł Centrala ############
@app.route('/centrala_menu/', methods=['GET', 'POST'])
def centrala_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pracownicy")
        data = cursor.fetchall()
        cursor.close()
        return render_template('centrala_menu/index_centrala.html', pracownicy=data)
    else:
        return render_template("index.html")

############ Moduł Centrala ############
### Poszczególne SELECT do pracowników ###
@app.route('/select_centrala',methods=['POST','GET'])
def select_centrala():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pracownicy ")
        data = cursor.fetchall()
        cursor.close()
        return render_template('centrala_menu/index_centrala.html', pracownicy=data)
    else:
        return render_template("index.html")


########### Moduł Sprzet ############
@app.route('/sprzet_menu/', methods=['GET', 'POST'])
def sprzet_menu():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pracownicy")
        data = cursor.fetchall()
        cursor.close()
        return render_template('sprzet_menu/index_zasoby.html', pracownicy=data)
    else:
        return render_template("index.html")

############ Moduł Sprzet ############
### Poszczególne SELECT do pracowników ###
@app.route('/select_sprzet',methods=['POST','GET'])
def select_sprzet():
    if "username" in session:
        username = session['username']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pracownicy ")
        data = cursor.fetchall()
        cursor.close()
        return render_template('sprzet_menu/index_zasoby.html', pracownicy=data)
    else:
        return render_template("index.html")

@app.route('/update_sprzet',methods=['POST','GET'])
def update_sprzet():
    if request.method == 'POST':
        id = request.form['id']
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        adres_ip_pc = request.form['adres_ip_pc']
        login_windows = request.form['login_windows']
        nazwa_pc = request.form['nazwa_pc']
        office_pass = request.form['office_pass']
        adres_ip_tel = request.form['adres_ip_tel']
        f_secure = request.form['f_secure']
        gniazdo_tel = request.form['gniazdo_tel']
        gniazdo_pc = request.form['gniazdo_pc']
        tel_pass = request.form['tel_pass']
        adres_ip_sluchawka = request.form['adres_ip_sluchawka']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE pracownicy SET imie=%s, nazwisko=%s, adres_ip_pc=%s, login_windows=%s, nazwa_pc=%s, office_pass=%s, adres_ip_tel=%s, f_secure=%s, gniazdo_tel=%s, "
                       "gniazdo_pc=%s, tel_pass=%s, adres_ip_sluchawka=%s WHERE id=%s ",
                       (imie, nazwisko, adres_ip_pc, login_windows, nazwa_pc, office_pass, adres_ip_tel, f_secure, gniazdo_tel, gniazdo_pc, tel_pass, adres_ip_sluchawka, id))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('select_sprzet'))
    else:
        return render_template("index.html")



############ Moduł Fotowoltaika ############
### Poszczególne SELECT do pracowników ###
@app.route('/fotowoltaika')
def fotowoltaika():

    #print(beer)
    return render_template('index_fotowoltaika.html')










############ Moduł Wyślij email ############
### Route indeks_mail ###
@app.route('/email_menu')
def email_menu():
    if "username" in session:
        username = session['username']
        return render_template("index_email.html")
    else:
        return render_template("index.html")

### Route Wyślij email Administracja NW ###
@app.route('/email_kontrahent')
def email_kontrahent():
    if "username" in session:
        username = session['username']
        return render_template("index_email_kontrahent.html")
    else:
        return render_template("index.html")

### Route Wyślij email Administracja NS ###
@app.route('/email_budynek')
def email_budynek():
    if "username" in session:
        username = session['username']
        return render_template("index_email_budynek.html")
    else:
        return render_template("index.html")

@app.route("/ajaxfileemail_budynek", methods=["POST", "GET"])
def ajaxfileemail_budynek():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from email_blok")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from email_blok "
                           "WHERE id LIKE %s OR indeksBudynek LIKE %s OR email LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM email_blok "
                               "ORDER BY id asc limit %s, %s;", (row, rowperpage))
                emailbloklist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM email_blok WHERE id "
                    "LIKE %s OR indeksBudynek LIKE %s OR email LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                emailbloklist = cursor.fetchall()

            data = []
            for row in emailbloklist:
                data.append({
                    'test': row['test'],
                    'id': row['id'],
                    'indeksBudynek': row['indeksBudynek'],
                    'email': row['email']
                    })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route("/ajaxfileemail_kontrahent", methods=["POST", "GET"])
def ajaxfileemail_kontrahent():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from email")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from email "
                           "WHERE id LIKE %s OR indeks LIKE %s OR email LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM email "
                               "ORDER BY id asc limit %s, %s;", (row, rowperpage))
                emaillist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM email WHERE id "
                    "LIKE %s OR indeks LIKE %s OR email LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                emaillist = cursor.fetchall()

            data = []
            for row in emaillist:
                data.append({
                    'test': row['test'],
                    'id': row['id'],
                    'indeks': row['indeks'],
                    'email': row['email']
                    })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



@app.route('/dokumenty_menu')
def dokumenty_menu():
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dokumenty")
    data = cursor.fetchall()
    cursor.close()
    return render_template('dokumenty.html', dokumenty=data)


if __name__ == '__main__':
    app.run(debug=True)
