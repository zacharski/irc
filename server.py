import os
import uuid
from flask import Flask, session, jsonify, request
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.debug = True

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
users = {}
rooms = ['General']

def updateRoster():
    names = []
    for user_id in  users:
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    socketio.emit('roster', names)
    
def updateRooms():
    socketio.emit('rooms', rooms)


@socketio.on('message')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    tmp = {'text':message['text'], 'room':message['room'], 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    emit('message', tmp, broadcast=True)
    
@socketio.on('identify')
def on_identify(message):
    
    if 'uuid' in session:
        users[session['uuid']]={'username':message}
        updateRoster()
    else:
        print 'sending information'
        session['uuid']=uuid.uuid1()
        session['username']='starter name'
  
    
        updateRoster()
        updateRooms()

        for message in messages:
            emit('message', message)
    
@socketio.on('disconnect')
def on_disconnect():
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()
    
@app.route('/new_room', methods=['POST'])
def new_room():
    rooms.append(request.get_json()['name'])
    print 'updating rooms'
    updateRooms()
    print 'back'

    return jsonify(success= "ok")

@app.route('/')
def hello_world():
    print 'in hello world'
    return app.send_static_file('index.html')
    return 'Hello World!'

@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
     
