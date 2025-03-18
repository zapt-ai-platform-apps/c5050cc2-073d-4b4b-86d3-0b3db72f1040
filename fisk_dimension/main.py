from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Verify database connection
try:
    engine = create_engine(os.environ.get("DATABASE_URL"))
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()  # Exit if the database connection fails

# Import modules
from encryption_module import UniqueEncryptionSystem
from auth_module import token_required, generate_token
from referral_module import is_valid_referral
from sync_module import local_db_connection, cloud_db_connection, sync_data
from ai_module import analyze_for_anomalies, generate_ai_response
from multimedia_module import generate_music_video, text_to_video, speech_to_video
from voice_assistant import speak, listen_command

app = Flask(__name__)

# Initialize the encryption system
encryption_system = UniqueEncryptionSystem()

# In-memory user store (for demo purposes)
users = {}

# Registration endpoint
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    referral = data.get("referral_code")
    if not username or not password or not referral:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_referral(referral):
        return jsonify({"error": "Invalid referral code"}), 403
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    from auth_module import hash_password
    users[username] = hash_password(password)
    token = generate_token(username)
    return jsonify({"message": "User registered successfully", "token": token})

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    from auth_module import hash_password
    if users.get(username) != hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 403
    token = generate_token(username)
    return jsonify({"message": "Logged in successfully", "token": token})

# Encryption endpoint
@app.route("/encrypt", methods=["POST"])
@token_required
def encrypt_endpoint(current_user):
    data = request.json
    plaintext = data.get("plaintext")
    if not plaintext:
        return jsonify({"error": "No plaintext provided"}), 400
    encrypted = encryption_system.encrypt(plaintext)
    return jsonify({
        "rsa_encrypted_key": encrypted["rsa_encrypted_key"].hex(),
        "obfuscated_ciphertext": encrypted["obfuscated_ciphertext"].hex()
    })

# Decryption endpoint
@app.route("/decrypt", methods=["POST"])
@token_required
def decrypt_endpoint(current_user):
    data = request.json
    try:
        encrypted_data = {
            "rsa_encrypted_key": bytes.fromhex(data.get("rsa_encrypted_key")),
            "obfuscated_ciphertext": bytes.fromhex(data.get("obfuscated_ciphertext"))
        }
        plaintext = encryption_system.decrypt(encrypted_data)
        return jsonify({"plaintext": plaintext})
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

# Chat endpoint (AI engine & game logic)
@app.route("/chat", methods=["POST"])
@token_required
def chat_endpoint(current_user):
    data = request.json
    prompt = data.get("prompt")
    messages = data.get("messages", [])
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    if analyze_for_anomalies(prompt):
        return jsonify({"error": "Anomaly detected – secure mode activated"}), 403
    ai_response = generate_ai_response(prompt, messages)
    return jsonify({"response": ai_response})

# Multimedia endpoint
@app.route("/multimedia", methods=["POST"])
@token_required
def multimedia_endpoint(current_user):
    data = request.json
    mode = data.get("mode")
    input_text = data.get("input", "")
    if mode == "music_video":
        result = generate_music_video(input_text)
    elif mode == "text_to_video":
        result = text_to_video(input_text)
    elif mode == "speech_to_video":
        audio_hex = data.get("audio")
        if not audio_hex:
            return jsonify({"error": "No audio provided"}), 400
        result = speech_to_video(audio_hex)
    else:
        result = "Invalid multimedia mode selected."
    return jsonify({"result": result})

# Data synchronization endpoint
@app.route("/sync", methods=["GET"])
@token_required
def sync_endpoint(current_user):
    local_conn = local_db_connection("local.db")
    cloud_conn = cloud_db_connection(os.environ.get("DATABASE_URL"))
    msg = sync_data(local_conn, cloud_conn)
    return jsonify({"message": msg})

# Voice interface endpoint (AI assistant as your virtual speaker)
@app.route("/voice", methods=["GET"])
@token_required
def voice_interface(current_user):
    speak("Greetings, seeker of truth. Please speak your command.")
    command = listen_command()
    if command:
        response = f"Your words echo in eternity: '{command}'. I respond with the wisdom of ages."
        speak(response)
        return jsonify({"message": response})
    return jsonify({"message": "No command detected."})

if __name__ == "__main__":
    print("Fisk Dimension awakens—a canvas of art, philosophy, and technology.")
    app.run(debug=True)