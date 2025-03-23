from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

USERS_FILE = "C:\\Users\\tomik\\Desktop\\public\\malgymnews\\users.json"
NOVINY_FOLDER = "C:\\Users\\tomik\\Desktop\\public\\malgymnews\\noviny"

# Načti uživatele ze souboru
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Ulož uživatele
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Načti seznam PDF
def list_newspapers():
    return [f for f in os.listdir(NOVINY_FOLDER) if f.endswith('.pdf')]

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users = load_users()
    if data['username'] in users:
        return jsonify({"msg": "Uživatel existuje"}), 400
    users[data['username']] = {
        "password": generate_password_hash(data['password']),
        "credits": 3,
        "unlocked": []
    }
    save_users(users)
    return jsonify({"msg": "Registrováno"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()
    user = users.get(data['username'])
    if user and check_password_hash(user['password'], data['password']):
        return jsonify({"msg": "OK"}), 200
    return jsonify({"msg": "Chyba"}), 401

@app.route('/noviny', methods=['GET'])
def get_noviny():
    return jsonify(list_newspapers())

@app.route('/unlocked/<username>', methods=['GET'])
def get_user_noviny(username):
    users = load_users()
    user = users.get(username)
    if user:
        return jsonify({
            "credits": user['credits'],
            "unlocked": user['unlocked']
        })
    return jsonify({"msg": "Nenalezen"}), 404

@app.route('/unlock', methods=['POST'])
def unlock():
    data = request.json
    users = load_users()
    user = users.get(data['username'])
    if user and user['credits'] > 0 and data['filename'] not in user['unlocked']:
        user['credits'] -= 1
        user['unlocked'].append(data['filename'])
        save_users(users)
        return jsonify({"msg": "Odemčeno"}), 200
    return jsonify({"msg": "Nelze odemknout"}), 400

@app.route('/noviny/<filename>')
def serve_pdf(filename):
    return send_from_directory(NOVINY_FOLDER, filename)

# Načti seznam všech uživatelů a jejich kreditů
@app.route('/admin/users', methods=['GET'])
def admin_get_users():
    users = load_users()
    stripped = {u: {"credits": data["credits"]} for u, data in users.items()}
    return jsonify(stripped)

# Přidání kreditů
@app.route('/admin/add-credit', methods=['POST'])
def admin_add_credit():
    data = request.json
    users = load_users()
    user = users.get(data["username"])
    if user:
        user["credits"] += int(data["amount"])
        save_users(users)
        return jsonify({"msg": "Kredit přidán"}), 200
    return jsonify({"msg": "Uživatel nenalezen"}), 404

# Nastavení přesného počtu kreditů
@app.route('/admin/set-credit', methods=['POST'])
def admin_set_credit():
    data = request.json
    users = load_users()
    user = users.get(data["username"])
    if user:
        user["credits"] = int(data["amount"])
        save_users(users)
        return jsonify({"msg": "Kredit nastaven"}), 200
    return jsonify({"msg": "Uživatel nenalezen"}), 404

ADMIN_PASSWORD_HASH = generate_password_hash("MGNEWS15")
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if check_password_hash(ADMIN_PASSWORD_HASH, data.get("password", "")):
        return jsonify({"msg": "OK"}), 200
    return jsonify({"msg": "Chyba"}), 401

@app.route('/')
def home():
    return "ahoj"

if __name__ == '__main__':
    os.makedirs(NOVINY_FOLDER, exist_ok=True)
    ssl_context = (
  "C:\\Users\\tomik\\0000_csr-certbot.pem",
  "C:\\Users\\tomik\\0000_key-certbot.pem"
)
    app.run(ssl_context=("fullchain.pem", "privkey.pem"), host="0.0.0.0", port=8443)
