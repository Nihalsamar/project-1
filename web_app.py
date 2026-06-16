"""
=============================================================================
Payment Integration & QR Code Generator - Web Application (Flask)
=============================================================================
This is the web version of the payment integration project.
It uses Flask to serve a web page that lets users:
1. Enter payment details (amount, currency, description)
2. Generate a secure payment transaction
3. Display a QR code on the web page that can be scanned to pay

How it works:
- Flask serves an HTML page with a form
- User submits payment details
- Server generates transaction + QR code
- QR code is returned as a base64-encoded image (no file saving needed)
- The page displays the QR code and transaction details

Run: python web_app.py
Then open: http://127.0.0.1:5000
=============================================================================
"""

from flask import Flask, render_template_string, request
import qrcode
import hashlib
import uuid
import io
import base64
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# FLASK APP INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)

# Simulated payment gateway config
PAYMENT_GATEWAY_BASE_URL = "https://pay.example.com/checkout"
MERCHANT_ID = "MERCHANT_12345"
SECRET_KEY = "sk_test_demo_key_not_real"


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT LOGIC (same as project.py but adapted for web)
# ─────────────────────────────────────────────────────────────────────────────

def create_transaction(amount, currency, description):
    """Create a payment transaction and return all details."""
    transaction_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    # Generate secure token
    raw_string = f"{transaction_id}{amount}{SECRET_KEY}"
    payment_token = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    # Build payment URL
    payment_url = (
        f"{PAYMENT_GATEWAY_BASE_URL}"
        f"?txn_id={transaction_id}"
        f"&amount={amount}"
        f"&currency={currency}"
        f"&merchant={MERCHANT_ID}"
        f"&token={payment_token}"
    )

    return {
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "description": description,
        "status": "pending",
        "created_at": created_at,
        "payment_token": payment_token,
        "payment_url": payment_url,
    }


def generate_qr_base64(data):
    """
    Generate a QR code and return it as a base64-encoded PNG string.
    This way we can embed it directly in HTML without saving a file.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save image to a bytes buffer instead of a file
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Convert to base64 so it can be embedded in an <img> tag
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64


# ─────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE (embedded for simplicity)
# ─────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Integration & QR Code Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.6rem;
        }

        .subtitle {
            text-align: center;
            color: #777;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 6px;
            color: #555;
            font-weight: 600;
            font-size: 0.9rem;
        }

        input, select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
            outline: none;
        }

        input:focus, select:focus {
            border-color: #667eea;
        }

        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        /* Result Section */
        .result {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9ff;
            border-radius: 15px;
            border: 1px solid #e8eaff;
        }

        .result h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2rem;
            text-align: center;
        }

        .qr-code {
            text-align: center;
            margin: 20px 0;
        }

        .qr-code img {
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            font-size: 0.85rem;
        }

        .detail-row:last-child {
            border-bottom: none;
        }

        .detail-label {
            color: #777;
            font-weight: 500;
        }

        .detail-value {
            color: #333;
            font-weight: 600;
            max-width: 60%;
            word-break: break-all;
            text-align: right;
        }

        .status-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            background: #fff3cd;
            color: #856404;
        }

        .security-badge {
            text-align: center;
            margin-top: 15px;
            color: #28a745;
            font-size: 0.8rem;
        }

        .security-badge::before {
            content: "🔒 ";
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💳 Payment & QR Generator</h1>
        <p class="subtitle">Generate secure payment QR codes instantly</p>

        <!-- Payment Form -->
        <form method="POST" action="/">
            <div class="form-group">
                <label for="amount">Amount</label>
                <input type="number" id="amount" name="amount" step="0.01" min="1"
                       placeholder="Enter amount (e.g., 499.99)" required
                       value="{{ amount or '' }}">
            </div>

            <div class="form-group">
                <label for="currency">Currency</label>
                <select id="currency" name="currency">
                    <option value="INR" {{ 'selected' if currency == 'INR' else '' }}>🇮🇳 INR - Indian Rupee</option>
                    <option value="USD" {{ 'selected' if currency == 'USD' else '' }}>🇺🇸 USD - US Dollar</option>
                    <option value="EUR" {{ 'selected' if currency == 'EUR' else '' }}>🇪🇺 EUR - Euro</option>
                    <option value="GBP" {{ 'selected' if currency == 'GBP' else '' }}>🇬🇧 GBP - British Pound</option>
                </select>
            </div>

            <div class="form-group">
                <label for="description">Payment Description</label>
                <input type="text" id="description" name="description"
                       placeholder="e.g., Online Course Subscription"
                       value="{{ description or '' }}" required>
            </div>

            <button type="submit">Generate Payment QR Code</button>
        </form>

        <!-- Result (shown after form submission) -->
        {% if transaction %}
        <div class="result">
            <h2>✅ Payment QR Generated</h2>

            <div class="qr-code">
                <img src="data:image/png;base64,{{ qr_image }}" alt="Payment QR Code" width="200" height="200">
            </div>

            <p style="text-align:center; color:#666; font-size:0.8rem; margin-bottom:15px;">
                Scan this QR code with any UPI/payment app to pay
            </p>

            <div class="detail-row">
                <span class="detail-label">Transaction ID</span>
                <span class="detail-value">{{ transaction.transaction_id[:8] }}...</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Amount</span>
                <span class="detail-value">{{ transaction.amount }} {{ transaction.currency }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Description</span>
                <span class="detail-value">{{ transaction.description }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status</span>
                <span class="detail-value"><span class="status-badge">{{ transaction.status }}</span></span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Created At</span>
                <span class="detail-value">{{ transaction.created_at[:19] }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Token</span>
                <span class="detail-value">{{ transaction.payment_token[:16] }}...</span>
            </div>

            <div class="security-badge">
                Secured with SHA-256 token verification
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main route - handles both displaying the form (GET) and processing it (POST).

    GET: Shows the empty payment form
    POST: Creates transaction, generates QR, shows result
    """
    transaction = None
    qr_image = None
    amount = ""
    currency = "INR"
    description = ""

    if request.method == "POST":
        # Get form data
        amount = float(request.form["amount"])
        currency = request.form["currency"]
        description = request.form["description"]

        # Create the transaction (generates ID, token, URL)
        transaction = create_transaction(amount, currency, description)

        # Generate QR code as base64 image
        qr_image = generate_qr_base64(transaction["payment_url"])

        # Convert to object-like access for template
        class TxnObj:
            pass
        txn = TxnObj()
        for k, v in transaction.items():
            setattr(txn, k, v)
        transaction = txn

    return render_template_string(
        HTML_TEMPLATE,
        transaction=transaction,
        qr_image=qr_image,
        amount=amount,
        currency=currency,
        description=description,
    )


# ─────────────────────────────────────────────────────────────────────────────
# RUN THE SERVER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Payment & QR Code Generator - Web App")
    print("  Open in browser: http://127.0.0.1:5000")
    print("=" * 50)
    # debug=True enables auto-reload on code changes during development
    app.run(debug=True, host="127.0.0.1", port=5000)
