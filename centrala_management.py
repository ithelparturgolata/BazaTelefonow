from flask import Blueprint
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, json, send_file
from dbconnection import db
import mysql.connector
from flask_mysqldb import MySQL
from flaskext.mysql import MySQL #pip install flask-mysql
import pymysql


centrala_manager_blueprint = Blueprint('centrala_manager_blueprint', __name__, url_prefix="/centrala")


############ Moduł Centrala ############
@centrala_manager_blueprint.route('/centrala_menu', methods=['GET', 'POST'])
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
@centrala_manager_blueprint.route('/centrala_select', methods=['POST','GET'])
def centrala_select():
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
