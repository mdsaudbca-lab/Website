# ⚡ Warp — P2P File Transfer

Server-less file sharing. Files go directly browser-to-browser via WebRTC. No uploads, no storage, full speed.

## Features
- 🔗 Room codes + QR code to connect
- 📂 Drag & Drop multi-file transfer
- 📊 Real-time speed & progress
- 💬 Built-in P2P chat
- 🔒 Files never touch the server

## Local Setup
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Deploy on Render (Free)

1. Push this repo to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class eventlet -w 1 app:app`
5. Deploy!

## How it works
1. Person A clicks "Create Room" → gets a code
2. Person B enters the code (or scans QR)
3. Flask server does a WebRTC handshake (signaling)
4. After that, server is out of the picture
5. Files transfer directly P2P at full network speed
