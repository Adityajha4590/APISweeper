from flask import Flask, jsonify, request

"""
======================================================================
APISweeper Dummy Target API
======================================================================

ATTENTION TEAM:
This is a fake, deliberately vulnerable web server built using Flask.
We use this to safely test our APISweeper scanner. DO NOT test your 
modules on live public websites without permission. Always test against 
this local dummy server first!

To run this server locally:
    python dummy_api/app.py
    
It will run on port 5001 so it doesn't conflict with our UI on port 5000.
"""

app = Flask(__name__)

# --------------------------------------------------------------------
# Vulnerability 1: Missing Security Headers (Passive Scan Target)
# Assigned to: Keshav
# --------------------------------------------------------------------
@app.route('/api/v1/status', methods=['GET'])
def status():
    """
    This endpoint is missing important security headers like:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    Keshav's passive module should flag this.
    """
    return jsonify({
        "status": "API is online", 
        "version": "1.0.0",
        "message": "Welcome to the dummy API!"
    }), 200


# --------------------------------------------------------------------
# Vulnerability 2: Verbose Error Leaks (Passive Scan Target)
# Assigned to: Keshav
# --------------------------------------------------------------------
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    This endpoint simulates a badly configured server that leaks stack 
    traces and database credentials when an unhandled error occurs.
    If you request user_id 999, it throws a verbose exception.
    """
    if user_id == 999:
        # Deliberately leaking sensitive info in a 500 error response
        error_msg = "java.sql.SQLException: Access denied for user 'root'@'localhost' (using password: 'SuperSecretDBPassword123')"
        return error_msg, 500
        
    return jsonify({"id": user_id, "username": f"testuser_{user_id}"}), 200


# --------------------------------------------------------------------
# Vulnerability 3: Missing Rate Limiting (Active Scan Target)
# Assigned to: Rishab
# --------------------------------------------------------------------
@app.route('/api/v1/login', methods=['POST'])
def login():
    """
    This login endpoint DOES NOT have any rate limiting (like 429 Too Many Requests).
    Rishab's active module should spam this endpoint and report that 
    it is vulnerable to Brute-Force attacks.
    """
    data = request.get_json() or {}
    
    # Just a fake hardcoded login check
    if data.get("username") == "admin" and data.get("password") == "admin123":
        return jsonify({"token": "fake_jwt_token_here"}), 200
        
    return jsonify({"error": "Invalid credentials"}), 401


# --------------------------------------------------------------------
# Fake auth — two hardcoded test users and their tokens. FOR BOLA
# --------------------------------------------------------------------

FAKE_USERS = {
    "token_alice_123": {"user_id": 1, "username": "alice"},
    "token_bob_456": {"user_id": 2, "username": "bob"},
}


# --------------------------------------------------------------------
# Fake data — each order belongs to exactly one user (the "owner" field).
# --------------------------------------------------------------------
ORDERS = {
    101: {"item": "Laptop", "amount": "$1200", "owner": 1},   
    102: {"item": "Phone", "amount": "$800", "owner": 2},     
    103: {"item": "Headphones", "amount": "$150", "owner": 1},  
}

def get_requesting_user():
    """
    Reads the authorization header and  looks which user it belongs to Return none if token is missing or incorrect. 

    """

    auth_header = request.headers.get("Authorization","")
    token = auth_header.replace("Bearer","").strip()
    return FAKE_USERS.get(token)

# --------------------------------------------------------------------
# Vulnerability 4: Broken Object-Level Authorization (BOLA/IDOR)
# Assigned to: Pranav
# --------------------------------------------------------------------
@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Returns an order by ID.

    this checks that the request has SOME valid token
    (is the requester logged in at all?), but does not checks whether
    the order's owner field matches the requesting user's ID.

    """
    user = get_requesting_user()
    if user is None:
        return jsonify({"error": "Unauthorized - invalid or missing token"}), 401

    # As it is BOLA we are not checking if the orderid belongs to owner .

    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    
    return jsonify({
        "order_id": order_id,
        "item": order["item"],
        "amount": order["amount"],
        "owner_user_id": order["owner"],
    }), 200

if __name__ == '__main__':
    print("⚠️  WARNING: Starting Vulnerable Dummy API on http://localhost:5001")
    print("⚠️  DO NOT run this on a public network. Localhost testing only.")
    app.run(debug=True, port=5001)
