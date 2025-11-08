# api.py
from flask import Blueprint, request, jsonify
from models import User  # Adjust import according to your project structure
from your_database_module import db  # Import db from your app's db setup

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user = User(username=data["username"], password=data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201


