# Project 1 — Payment Integration & QR Code Generator

A Python-based application that integrates a (simulated) payment gateway with
dynamic QR code generation, enabling seamless and secure digital transactions.
It demonstrates best practices for transaction security and data integrity using
unique transaction IDs and SHA-256 token verification.

## Live Demo

**https://nihalsamar.github.io/project-1/**

The live demo is a static, browser-only build of the payment QR generator.
Enter an amount, currency, and description to generate a scannable payment QR
code along with a secure transaction token.

## What's Inside

| File | Description |
|------|-------------|
| `project.py` | Core Python app: creates transactions, generates a secure SHA-256 token, builds the payment URL, renders a QR code image, and logs transactions to JSON. |
| `web_app.py` | Flask web version of the same logic. Serves a form and returns a QR code rendered as a base64 image. |
| `docs/index.html` | Static, client-side version that powers the live GitHub Pages demo (QR + token generated entirely in the browser). |

## Running Locally

### Command-line version
```bash
pip install "qrcode[pil]"
python project.py
```
This generates a QR code image and a `transaction_log.json` record.

### Flask web version
```bash
pip install flask "qrcode[pil]"
python web_app.py
```
Then open http://127.0.0.1:5000 in your browser.

## How It Works

1. A payment request is created with an amount, currency, and description.
2. A unique transaction ID (UUID4) is generated.
3. A secure token is computed as `SHA-256(transaction_id + amount + secret_key)`.
   If any value is tampered with, the token no longer matches — this protects
   data integrity, the same principle real payment gateways use.
4. A payment URL is built with all parameters and the token.
5. A QR code is generated from the URL so users can scan and pay.

## Security Note

⚠️ **The `SECRET_KEY` in `docs/index.html` is visible in the page source.**

This is acceptable for a demo, but in a real payment system the secret key must
**never** be shipped to the browser. Token generation and verification have to
happen on a trusted server. Anyone who can read a client-side secret can forge
valid tokens. In production:

- Keep the secret key server-side only (use environment variables, never commit it).
- Generate and verify tokens on the backend.
- Use the official SDK and server-side webhooks provided by your payment
  gateway (Razorpay, Stripe, etc.) to confirm payments.

The values used here (`MERCHANT_ID`, `SECRET_KEY`, gateway URL) are dummy
placeholders for demonstration only.
