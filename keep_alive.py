from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot Tuglar đang sống nhăn răng trên Render!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()