from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, json
import mysql.connector

connection = mysql.connector.connect(host="localhost", port="3306",
                                     database="bazasm", user="root", password="Savakiran03")
cursor = connection.cursor()

menu_blueprint = Blueprint('menu', __name__)

# @menu_blueprint.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
#         message = "Błędny login"
#         username = request.form["username"]
#         password = request.form["password"]
#         cursor.execute("SELECT * FROM uzytkownicy WHERE "
#                        "username = %s AND password = %s", (username, password))
#         record = cursor.fetchone()
#         if record:
#             session["loggedin"] = True
#             session["username"] = record[1]
#             return redirect(url_for("menu"))
#         else:
#             return redirect(url_for('index'))
#     return render_template("index.html")
#
# @menu_blueprint.route("/logout")
# def logout():
#     session.pop("loggedin", None)
#     session.pop("username", None)
#     return redirect(url_for("login"))

@menu_blueprint.route('/menu')
def menu():
    if "username" in session:
        username = session['username']
        return render_template("menu.html")
    else:
        return render_template("index.html")