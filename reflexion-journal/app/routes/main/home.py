from . import main

@main.route('/')
def home():
    return "Hello world! Programmed to work and not to feel."