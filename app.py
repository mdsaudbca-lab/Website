from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'warp-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# rooms = { room_id: [creator_sid, joiner_sid] }
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('index.html')

# ── Socket events ──────────────────────────────────────────

@socketio.on('create_room')
def on_create_room():
    sid = request.sid
    room_id = str(uuid.uuid4())[:8].upper()
    rooms[room_id] = [sid]          # creator ka sid save karo
    join_room(room_id)              # creator bhi room mein add
    emit('room_created', {'room_id': room_id})

@socketio.on('join_room')
def on_join_room(data):
    sid = request.sid
    room_id = data.get('room_id', '').upper().strip()

    if room_id not in rooms:
        emit('error', {'message': 'Room not found. Check your code.'})
        return
    if len(rooms[room_id]) >= 2:
        emit('error', {'message': 'Room is full (max 2 peers).'})
        return

    join_room(room_id)
    rooms[room_id].append(sid)      # joiner ka sid save karo

    # Joiner ko confirm karo
    emit('joined_room', {'room_id': room_id})

    # Creator ko batao ki peer aa gaya — WebRTC offer shuru kare
    creator_sid = rooms[room_id][0]
    socketio.emit('peer_joined', {}, to=creator_sid)

@socketio.on('webrtc_offer')
def on_offer(data):
    sid = request.sid
    room_id = data.get('room_id')
    if not room_id or room_id not in rooms:
        return
    for peer_sid in rooms[room_id]:
        if peer_sid != sid:
            socketio.emit('webrtc_offer', {'sdp': data['sdp']}, to=peer_sid)

@socketio.on('webrtc_answer')
def on_answer(data):
    sid = request.sid
    room_id = data.get('room_id')
    if not room_id or room_id not in rooms:
        return
    for peer_sid in rooms[room_id]:
        if peer_sid != sid:
            socketio.emit('webrtc_answer', {'sdp': data['sdp']}, to=peer_sid)

@socketio.on('ice_candidate')
def on_ice(data):
    sid = request.sid
    room_id = data.get('room_id')
    if not room_id or room_id not in rooms:
        return
    for peer_sid in rooms[room_id]:
        if peer_sid != sid:
            socketio.emit('ice_candidate', {'candidate': data['candidate']}, to=peer_sid)

@socketio.on('chat_message')
def on_chat(data):
    sid = request.sid
    room_id = data.get('room_id')
    if not room_id or room_id not in rooms:
        return
    for peer_sid in rooms[room_id]:
        if peer_sid != sid:
            socketio.emit('chat_message', {'message': data['message']}, to=peer_sid)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for room_id, sids in list(rooms.items()):
        if sid in sids:
            sids.remove(sid)
            for peer_sid in sids:
                socketio.emit('peer_left', {}, to=peer_sid)
            if len(sids) == 0:
                del rooms[room_id]
            break

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)