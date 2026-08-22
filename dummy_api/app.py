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


if __name__ == '__main__':
    print("⚠️  WARNING: Starting Vulnerable Dummy API on http://localhost:5001")
    print("⚠️  DO NOT run this on a public network. Localhost testing only.")
    app.run(debug=True, port=5001)
