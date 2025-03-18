from flask import request, jsonify
import jwt, datetime, os
from functools import wraps

SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user']
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def generate_token(user):
    token = jwt.encode({
        "user": user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")
    return token

def hash_password(password):
    # Simple hash for demo purposes - in production use a secure method like bcrypt
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()