import os
import base64
import re
from flask import Flask, request, jsonify, render_template
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

PAYHERO_API_URL = "https://backend.payhero.co.ke/api/v2/payments"
PAYHERO_USERNAME = os.getenv('PAYHERO_API_USERNAME')
PAYHERO_PASSWORD = os.getenv('PAYHERO_API_PASSWORD')
PAYHERO_CHANNEL_ID = os.getenv('PAYHERO_CHANNEL_ID')

# ✅ Store payment status in memory
payment_status = {}

def get_basic_auth_token():
    credentials = f"{PAYHERO_USERNAME}:{PAYHERO_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initiate-stk-push', methods=['POST'])
def initiate_stk_push():
    try:
        data = request.get_json()

        phone_number = data.get('phone_number', '').strip()
        amount = data.get('amount', '').strip() if isinstance(data.get('amount'), str) else data.get('amount')
        external_reference = data.get('external_reference', '').strip()
        customer_name = data.get('customer_name', '').strip()

        # ✅ Set callback URL automatically
        callback_url = f"https://{os.getenv('PYTHONANYWHERE_USERNAME')}.pythonanywhere.com/callback"

        if not phone_number or not amount:
            return jsonify({'success': False, 'error': 'Phone number and amount are required'}), 400

        phone_number = re.sub(r'\s+', '', phone_number)

        if not re.match(r'^[\+]?[0-9]+$', phone_number):
            return jsonify({'success': False, 'error': 'Phone number must contain only digits'}), 400

        if not phone_number.startswith('254'):
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif phone_number.startswith('7') or phone_number.startswith('1'):
                phone_number = '254' + phone_number

        if not re.match(r'^254\d{9}$', phone_number):
            return jsonify({'success': False, 'error': 'Invalid phone number format. Must be a valid Kenyan phone number'}), 400

        try:
            amount_int = int(amount)
            if amount_int <= 0:
                return jsonify({'success': False, 'error': 'Amount must be a positive number'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Amount must be a valid number'}), 400

        payload = {
            "amount": amount_int,
            "phone_number": phone_number,
            "channel_id": int(PAYHERO_CHANNEL_ID),
            "provider": "m-pesa",
            "external_reference": external_reference,
            "customer_name": customer_name,
            "callback_url": callback_url
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': get_basic_auth_token()
        }

        response = requests.post(PAYHERO_API_URL, json=payload, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            # ✅ Reset status to pending
            payment_status[phone_number] = 'pending'
            return jsonify({'success': True, 'data': response.json()}), 200
        else:
            return jsonify({'success': False, 'error': response.text, 'status_code': response.status_code}), response.status_code

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/callback', methods=['POST'])
def payment_callback():
    callback_data = request.get_json()
    print("📥 Payment Callback Received:", callback_data)

    phone = callback_data.get('phone_number')
    status = callback_data.get('status')

    if phone:
        payment_status[phone] = status
        if status == 'success':
            print(f"✅ Payment confirmed for {phone}")

    return jsonify({'success': True}), 200

# ✅ Route for frontend to check payment status
@app.route('/check-payment-status', methods=['POST'])
def check_payment_status():
    data = request.get_json()
    phone = data.get('phone_number')
    status = payment_status.get(phone, 'pending')
    return jsonify({'status': status})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
