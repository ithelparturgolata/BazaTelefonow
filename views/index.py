from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint, json

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
def index():  # put application's code here
    return render_template("index.html")