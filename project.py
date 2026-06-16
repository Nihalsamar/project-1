"""
=============================================================================
Payment Integration & QR Code Generator
=============================================================================
This Python application demonstrates:
1. Payment gateway integration (simulated) with proper transaction handling
2. Dynamic QR code generation for payment links
3. Best practices for transaction security and data integrity

How it works:
- A payment request is created with amount, currency, and description
- The system generates a unique transaction ID and a secure payment token
- A payment URL is constructed (simulating a gateway like Razorpay/Stripe)
- A QR code is generated from the payment URL so users can scan & pay
- Transaction logs are maintained with timestamps and status tracking

Dependencies:
    pip install qrcode[pil] hashlib

Note: hashlib is part of Python's standard library, no install needed.
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import qrcode                   # Library to generate QR codes
import hashlib                  # For creating secure hashes (transaction tokens)
import uuid                     # For generating unique transaction IDs
import json                     # For structured data handling
import os                       # For file system operations
from datetime import datetime   # For timestamping transactions


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# In a real application, these would come from environment variables
# NEVER hardcode real API keys in source code
PAYMENT_GATEWAY_BASE_URL = "https://pay.example.com/checkout"
MERCHANT_ID = "MERCHANT_12345"
SECRET_KEY = "sk_test_demo_key_not_real"  # Simulated secret key


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT TRANSACTION CLASS
# ─────────────────────────────────────────────────────────────────────────────

class PaymentTransaction:
    """
    Represents a single payment transaction.

    This class encapsulates all the data and logic for one payment:
    - Generating a unique transaction ID
    - Creating a secure payment token (hash-based)
    - Building the payment URL
    - Tracking transaction status

    Attributes:
        transaction_id (str): Unique identifier for this transaction
        amount (float): Payment amount
        currency (str): Currency code (e.g., "INR", "USD")
        description (str): What the payment is for
        status (str): Current status - "pending", "completed", or "failed"
        created_at (str): ISO timestamp of when transaction was created
        payment_token (str): Secure hash token for verifying the transaction
    """

    def __init__(self, amount, currency="INR", description="Payment"):
        """
        Initialize a new payment transaction.

        Args:
            amount (float): The amount to charge
            currency (str): Currency code (default: INR)
            description (str): Description of the payment

        How it works:
            1. Generates a unique transaction ID using UUID4 (random-based)
            2. Stores payment details
            3. Sets initial status to "pending"
            4. Records creation timestamp
            5. Generates a secure payment token using SHA-256 hashing
        """
        # UUID4 generates a random unique ID - virtually impossible to collide
        self.transaction_id = str(uuid.uuid4())

        # Store payment details
        self.amount = amount
        self.currency = currency
        self.description = description

        # Transaction starts as "pending" until payment is confirmed
        self.status = "pending"

        # Record when this transaction was created (ISO format for consistency)
        self.created_at = datetime.now().isoformat()

        # Generate a secure token that proves this transaction is authentic
        # This prevents tampering - if anyone changes the amount, the token won't match
        self.payment_token = self._generate_secure_token()

    def _generate_secure_token(self):
        """
        Generate a SHA-256 hash token for transaction verification.

        How it works:
            - Combines transaction_id + amount + secret_key into one string
            - Feeds that string into SHA-256 hash algorithm
            - The resulting hash is unique to this exact combination
            - If ANY part changes (amount tampered, etc.), the hash will differ
            - This is how payment gateways verify data integrity

        Why SHA-256?
            - It's a one-way function (can't reverse to find the secret key)
            - Even a tiny change in input produces a completely different hash
            - It's computationally infeasible to find two inputs with the same hash

        Returns:
            str: A 64-character hexadecimal hash string
        """
        # Concatenate sensitive data with the secret key
        # The secret key ensures only WE can generate valid tokens
        raw_string = f"{self.transaction_id}{self.amount}{SECRET_KEY}"

        # Encode to bytes (hashlib requires bytes, not string)
        # Then compute SHA-256 hash and return as hex string
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def get_payment_url(self):
        """
        Construct the payment gateway URL with all required parameters.

        How it works:
            - Builds a URL that the payment gateway would recognize
            - Includes transaction ID, amount, currency, merchant ID, and token
            - In production, the gateway validates the token server-side
            - The user is redirected to this URL to complete payment

        Returns:
            str: Complete payment URL ready for QR code generation
        """
        # Construct URL with query parameters
        # Each parameter serves a purpose:
        #   txn_id  - identifies this specific transaction
        #   amount  - how much to charge
        #   currency - what currency (INR, USD, etc.)
        #   merchant - identifies our business account
        #   token   - proves the request is authentic and untampered
        payment_url = (
            f"{PAYMENT_GATEWAY_BASE_URL}"
            f"?txn_id={self.transaction_id}"
            f"&amount={self.amount}"
            f"&currency={self.currency}"
            f"&merchant={MERCHANT_ID}"
            f"&token={self.payment_token}"
        )
        return payment_url

    def to_dict(self):
        """
        Convert transaction to a dictionary for logging/storage.

        Returns:
            dict: All transaction details in a serializable format
        """
        return {
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "payment_token": self.payment_token
        }


# ─────────────────────────────────────────────────────────────────────────────
# QR CODE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_qr_code(data, filename="payment_qr.png"):
    """
    Generate a QR code image from the given data (payment URL).

    How QR codes work in payments:
        - The payment URL is encoded into a 2D barcode (QR code)
        - When a user scans it with their phone camera or UPI app,
          it opens the payment URL directly
        - This eliminates manual entry of payment details
        - QR codes have built-in error correction (can be read even if damaged)

    Args:
        data (str): The data to encode (typically the payment URL)
        filename (str): Output filename for the QR code image

    Returns:
        str: Path to the saved QR code image file

    QR Code Parameters Explained:
        version: Controls size (1 = 21x21 modules, higher = larger)
        error_correction: How much damage the code can sustain and still work
            - L (Low): ~7% damage tolerance
            - M (Medium): ~15% damage tolerance
            - Q (Quartile): ~25% damage tolerance
            - H (High): ~30% damage tolerance
        box_size: Size of each individual module (pixel) in the QR code
        border: White space around the QR code (minimum 4 per QR spec)
    """
    # Create QR code instance with specific settings
    qr = qrcode.QRCode(
        version=1,                                    # Smallest size that fits the data
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (30%)
        box_size=10,                                  # Each "pixel" of QR is 10x10 actual pixels
        border=4,                                     # 4-module white border (QR standard minimum)
    )

    # Add the payment URL data to the QR code
    qr.add_data(data)

    # make(fit=True) automatically determines the best version (size)
    # for the amount of data we're encoding
    qr.make(fit=True)

    # Create the actual image
    # fill_color: color of the QR modules (the dark squares)
    # back_color: background color
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to disk
    img.save(filename)

    return filename


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION LOGGER
# ─────────────────────────────────────────────────────────────────────────────

def log_transaction(transaction, log_file="transaction_log.json"):
    """
    Log a transaction to a JSON file for record-keeping.

    How it works:
        - Reads existing log file (or starts fresh if none exists)
        - Appends the new transaction to the list
        - Writes back to disk in formatted JSON
        - This provides an audit trail of all transactions

    Why JSON?
        - Human-readable format
        - Easy to parse programmatically
        - Can be imported into databases or analytics tools
        - Supports nested data structures

    Args:
        transaction (PaymentTransaction): The transaction to log
        log_file (str): Path to the JSON log file
    """
    # Try to load existing transactions from the log file
    # If file doesn't exist, start with an empty list
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            transactions = json.load(f)
    else:
        transactions = []

    # Append the new transaction (converted to dictionary)
    transactions.append(transaction.to_dict())

    # Write the updated list back to the file
    # indent=4 makes it human-readable (pretty-printed)
    with open(log_file, 'w') as f:
        json.dump(transactions, f, indent=4)

    print(f"[LOG] Transaction {transaction.transaction_id} logged successfully.")


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT VERIFICATION (Simulated)
# ─────────────────────────────────────────────────────────────────────────────

def verify_payment_token(transaction):
    """
    Verify that a transaction's token is valid (hasn't been tampered with).

    How verification works:
        1. Recompute the expected token using the same formula
        2. Compare it with the token stored in the transaction
        3. If they match → data is intact, transaction is authentic
        4. If they don't match → someone tampered with the data

    This is the same principle used by real payment gateways:
        - Gateway receives a request with amount and token
        - Gateway recomputes token using its copy of the secret key
        - If tokens match, the request is legitimate

    Args:
        transaction (PaymentTransaction): Transaction to verify

    Returns:
        bool: True if token is valid, False if data was tampered
    """
    # Recompute what the token SHOULD be
    expected_token = hashlib.sha256(
        f"{transaction.transaction_id}{transaction.amount}{SECRET_KEY}".encode('utf-8')
    ).hexdigest()

    # Compare with the stored token
    # If someone changed the amount after token generation, these won't match
    is_valid = expected_token == transaction.payment_token

    if is_valid:
        print("[SECURITY] ✓ Token verification PASSED - transaction is authentic.")
    else:
        print("[SECURITY] ✗ Token verification FAILED - possible tampering detected!")

    return is_valid


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """
    Main function demonstrating the complete payment + QR code workflow.

    Flow:
        1. Create a payment transaction with amount and details
        2. Verify the transaction token (security check)
        3. Generate the payment URL
        4. Create a QR code from the payment URL
        5. Log the transaction for record-keeping
        6. Display summary to the user
    """
    print("=" * 60)
    print("   PAYMENT INTEGRATION & QR CODE GENERATOR")
    print("=" * 60)
    print()

    # ─── Step 1: Create a new payment transaction ───────────────────────
    # In a real app, these values would come from user input or an order system
    print("[Step 1] Creating payment transaction...")
    transaction = PaymentTransaction(
        amount=499.99,              # Amount in the specified currency
        currency="INR",             # Indian Rupees
        description="Online Course Subscription"  # What user is paying for
    )
    print(f"   Transaction ID: {transaction.transaction_id}")
    print(f"   Amount: ₹{transaction.amount}")
    print(f"   Status: {transaction.status}")
    print()

    # ─── Step 2: Verify transaction integrity ───────────────────────────
    # This simulates the server-side verification that happens at the gateway
    print("[Step 2] Verifying transaction security token...")
    is_valid = verify_payment_token(transaction)
    if not is_valid:
        print("   ERROR: Transaction failed security check. Aborting.")
        return
    print()

    # ─── Step 3: Generate payment URL ───────────────────────────────────
    # This URL is what the user would visit (or scan via QR) to pay
    print("[Step 3] Generating payment URL...")
    payment_url = transaction.get_payment_url()
    print(f"   Payment URL: {payment_url[:80]}...")  # Truncated for display
    print()

    # ─── Step 4: Generate QR Code ───────────────────────────────────────
    # The QR code encodes the payment URL - scanning it opens the payment page
    print("[Step 4] Generating QR code...")
    qr_filename = f"payment_qr_{transaction.transaction_id[:8]}.png"
    qr_path = generate_qr_code(payment_url, qr_filename)
    print(f"   QR Code saved to: {qr_path}")
    print("   (User scans this QR code with their phone to pay)")
    print()

    # ─── Step 5: Log the transaction ────────────────────────────────────
    # Maintain an audit trail of all transactions
    print("[Step 5] Logging transaction...")
    log_transaction(transaction)
    print()

    # ─── Step 6: Display summary ────────────────────────────────────────
    print("=" * 60)
    print("   TRANSACTION SUMMARY")
    print("=" * 60)
    print(f"   Transaction ID : {transaction.transaction_id}")
    print(f"   Amount         : ₹{transaction.amount} {transaction.currency}")
    print(f"   Description    : {transaction.description}")
    print(f"   Status         : {transaction.status}")
    print(f"   Created At     : {transaction.created_at}")
    print(f"   QR Code File   : {qr_filename}")
    print(f"   Token (first 16): {transaction.payment_token[:16]}...")
    print("=" * 60)
    print()
    print("   Payment flow complete! Share the QR code with the customer.")
    print("   They scan it → redirected to payment page → transaction completes.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

# This block ensures main() only runs when the script is executed directly,
# NOT when it's imported as a module by another script.
# This is a Python best practice for reusable code.
if __name__ == "__main__":
    main()
