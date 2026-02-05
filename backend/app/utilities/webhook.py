import hashlib
import hmac
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set a secret key (keep this secret and do not hardcode it in production)
SECRET_KEY = "your_secret_key_here"

def verify_signature(payload, received_signature):
    """Verify that the request is legitimate using HMAC SHA256."""
    computed_signature = hmac.new(
        key=SECRET_KEY.encode(), 
        msg=payload, 
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, received_signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get raw JSON payload
        payload = request.get_data()
        received_signature = request.headers.get('X-Signature')

        # Check if signature is present
        if not received_signature:
            return jsonify({"error": "Missing signature"}), 403
        
        # Verify signature
        if not verify_signature(payload, received_signature):
            return jsonify({"error": "Invalid signature"}), 403

        # Parse JSON payload
        data = json.loads(payload)
        print("Received Webhook Data:", data)

        return jsonify({"message": "Webhook received!", "received_data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # HTTP 400 Bad Request

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
