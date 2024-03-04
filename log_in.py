from flask import app, jsonify, request
from app import name


@app.route('/log_in', methods=['POST'])
def login():
    
    email = request.json['email']
    password = request.json['password']

    new_name = name(email=email, password=password)

    return jsonify({'message': 'created successfully.'})
