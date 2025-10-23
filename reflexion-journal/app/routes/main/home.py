from . import main
from flask import Flask, render_template

@main.route('/')
def home():
    return render_template('home.html')