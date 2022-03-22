import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, json
from dbconnection import db
import mysql.connector
from flask_mysqldb import MySQL
from flaskext.mysql import MySQL #pip install flask-mysql
import pymysql
import os
import psycopg2
from flask_login import login_required, current_user
from datetime import timedelta
from smsapi.client import SmsApiPlClient
from smsapi.exception import SmsApiException

connection = mysql.connector.connect(host="localhost", port="3306",
                                     database="bazasm", user="root", password="Savakiran03")
cursor = connection.cursor()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=5)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Savakiran03'
app.config['MYSQL_DATABASE_DB'] = 'bazasm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.secret_key = "super secret key"


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/test')
def main():
    connection = mysql.connect()
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM blok ORDER BY idBudynek")
    blok = cursor.fetchall()
    return render_template('test.html', blok=blok)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    connection = mysql.connect()
    cursor = connection.cursor()
    if request.method == 'POST':
        for getid in request.form.getlist('mycheckbox'):
            print(getid)
            cursor.execute('SELECT * FROM blok WHERE idBudynek = {0}'.format(getid))
            # data = cursor.fetchone()
            # print(data)
            connection.commit()
        flash('Successfully Deleted!')
    return redirect('/test')

@app.route('/nw')
def nw():
    return render_template("index_nw.html")

@app.route('/ns')
def ns():
    return render_template("index_ns.html")

@app.route('/ce')
def ce():
    return render_template("index_ce.html")

@app.route('/dokumenty_menu')
def dokumenty_menu():
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dokumenty")
    data = cursor.fetchall()
    cursor.close()
    return render_template('dokumenty.html', dokumenty=data)

@app.route('/paneltelefony_menu')
def paneltelefony_menu():  # put application's code here
    return render_template("index_paneltelefony.html")

@app.route('/panelsms_menu')
def panelsms_menu():  # put application's code here
    return render_template("panelsms_menu.html")

@app.route('/panelsms_kontrahent')
def panelsms_kontrahent():  # put application's code here
    return render_template("panelsms_kontrahent.html")

@app.route('/panelsms_budynek')
def panelsms_budynek():  # put application's code here
    return render_template("panelsms_budynek.html")

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
    return render_template("menu.html")

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
            # print(draw)
            # print(row)
            # print(rowperpage)
            # print(searchValue)

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            # print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            # print(totalRecordwithFilter)

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
            # print(draw)
            # print(row)
            # print(rowperpage)
            # print(searchValue)

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            # print(totalRecordwithFilter)

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
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

            ## Fetch records
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
            # print(draw)
            # print(row)
            # print(rowperpage)
            # print(searchValue)

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mieszkaniec")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from mieszkaniec "
                           "WHERE indeks LIKE %s OR nazwaKarty LIKE %s OR adresKarty LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

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
            # print(draw)
            # print(row)
            # print(rowperpage)
            # print(searchValue)

            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from blok")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            # print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from blok "
                           "WHERE idBudynek LIKE %s OR SymbolBudynku LIKE %s OR Ulica LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            # print(totalRecordwithFilter)

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


@app.route("/sendsms", methods=['POST'])
def sendsms():
    if request.method=="POST":
        phone = request.form['phone']
        content = request.form['content']
        # token = "rM5DsJlOvDkbGnYnHAn9f9GmpphT0ovOywqPaiLL"
        # client = SmsApiPlClient(access_token=token)
        token = "rM5DsJlOvDkbGnYnHAn9f9GmpphT0ovOywqPaiLL"
        client = SmsApiPlClient(access_token=token)
        send_results = client.sms.send(to=phone, message=content, from_="SMBUDOWLANI")

        return render_template("panelsms_budynek.html")


@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        indeks_budynek = request.form['indeks_budynek']
        ulica = request.form['ulica']
        symbol_osiedla = request.form['symbol_osiedla']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO dokumenty (indeks_budynek, ulica, symbol_osiedla) VALUES (%s, %s, %s)", (indeks_budynek, ulica, symbol_osiedla))
        connection.commit()
        return redirect(url_for('dokumenty'))

# @app.route('/delete/<string:id_data>', methods = ['GET'])
# def delete(id_data):
#     flash("Rekord skasowany")
#     connection = mysql.connect()
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM dokumenty WHERE id_data=%s", (id_data,))
#     connection.commit()
#     return redirect(url_for('dokumenty'))

@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id_data']
        indeks_budynek = request.form['indeks_budynek']
        ulica = request.form['ulica']
        symbol_osielda = request.form['symbol_osiedla']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE dokumenty SET indeks_budynek=%s, ulica=%s, symbol_osiedla=%s WHERE id_data=%s ", (indeks_budynek, ulica, symbol_osielda, id_data))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('dokumenty'))


@app.route('/panelmieszkanca_menu')
def panelmieszkanca_menu():
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM budynek")
    data = cursor.fetchall()
    cursor.close()
    return render_template('index_panelmieszkanca.html', budynek=data)


@app.route('/insert_panelmieszkanca', methods = ['POST'])
def insert_panelmieszkanca():
    if request.method == "POST":
        flash("Dodano pomyślnie")
        indeksBudynek = request.form['indeksBudynek']
        ulicaBudynek = request.form['ulicaBudynek']
        kodBudynek = request.form['kodBudynek']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO budynek (indeksBudynek, ulicaBudynek, kodBudynek) VALUES (%s, %s, %s)", (indeksBudynek, ulicaBudynek, kodBudynek))
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca',methods=['POST','GET'])
def update_panelmieszkanca():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        indeksBudynek = request.form['indeksBudynek']
        ulicaBudynek = request.form['ulicaBudynek']
        kodBudynek = request.form['kodBudynek']
        nazwaOsiedla = request.form['nazwaOsiedla']
        adresOsiedla = request.form['adresOsiedla']
        telefonOsiedla = request.form['telefonOsiedla']
        kierownikOsiedla = request.form['kierownikOsiedla']
        zastepcaOsiedla = request.form['zastepcaOsiedla']
        nazwiskoAdministrator = request.form['nazwiskoAdministrator']
        telefonAdministrator = request.form['telefonAdministrator']
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET indeksBudynek=%s, ulicaBudynek=%s, kodBudynek=%s, nazwaOsiedla=%s, adresOsiedla=%s,"
                       "telefonOsiedla=%s, kierownikOsiedla=%s, zastepcaOsiedla=%s, nazwiskoAdministrator=%s, telefonAdministrator=%s "
                       "WHERE idBudynek=%s ", (indeksBudynek, ulicaBudynek, kodBudynek, nazwaOsiedla, adresOsiedla, telefonOsiedla, kierownikOsiedla,
                                               zastepcaOsiedla, nazwiskoAdministrator, telefonAdministrator, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))

@app.route('/update_panelmieszkanca1',methods=['POST','GET'])
def update_panelmieszkanca1():
    if request.method == 'POST':
        idBudynek = request.form['idBudynek']
        pkominyPrzeglady = request.form['pkominyPrzeglady']
        pgazPrzeglady = request.form['pgazPrzeglady']
        ptechnicznyPrzeglady = request.form['ptechnicznyPrzeglady']
        pelektrykaPrzeglady = request.form['pelektrykaPrzeglady']
        pogolnyPrzeglady = request.form['pogolnyPrzeglady']

        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(" UPDATE budynek SET pkominyPrzeglady=%s,  pgazPrzeglady=%s,  ptechnicznyPrzeglady=%s,  pelektryka=%s,  "
                       "pogolnyPrzeglady=%s  "
                       "WHERE idBudynek=%s ", (pkominyPrzeglady, pgazPrzeglady, ptechnicznyPrzeglady, pelektrykaPrzeglady, pogolnyPrzeglady, idBudynek))
        flash("Aktualizacja przebiegła pomyślnie")
        connection.commit()
        return redirect(url_for('panelmieszkanca_menu'))


if __name__ == '__main__':
    app.run(debug=True)