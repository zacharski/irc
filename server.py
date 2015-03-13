#server.py

import psycopg2
import psycopg2.extras

import os
import uuid
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

def connectToDB():
#changed the database name here from irc_db to irc  -- we called it irc.sql right?
  connectionString = 'dbname=irc user=postgres password=pg host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")


messages = [{'text':'test', 'name':'testName'}]
users = {}

#WHat the actual is this thing doing.
def updateRoster():
    names = []
    #need to check in database here?
    for user_id in users:
        print users[user_id]['username']
        #if there is no chars in the username
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
#This broadcasting names thing happens a lot. seems each time you call identify and login
    print 'broadcasting names'
    #I don't know what broadcast does?. changed it to false nothing seemed to change
    emit('roster', names, broadcast=True)

#CONNECT    
#I think this is where we wire in the database?
@socketio.on('connect', namespace='/chat') #handles the connect event
def test_connect():
    #right now it is using sessions, I think, and it should be checking against the db?
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'

    #new user is called when the database runs?    
    users[session['uuid']]={'username':'New User'}
    #updateRoster is called here. duh. it goes to...
    updateRoster()

    
    for message in messages:
        emit('message', message)

#MESSAGE
#THIS IS ON LINE 55 IN INDEX.HTML $scope.send - emits message and text
@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    emit('message', tmp, broadcast=True)

#IDENTIFY    
#LINE 76ish in index.html? $scope.setName - emits identify scope.name
# $scope.setName2 also emits identify, $scope.name2
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'identify' + message
    #the message here is where we need to connect to check against the database??
    #message is the username here.
    users[session['uuid']]={'username':message}
    updateRoster()

#LOGIN
#around line 85 index.html $scope.processLogin - emits login, $scope.password
@socketio.on('login', namespace='/chat')
def on_login(pw):
    #pw is whatever was typed into the password box
    print 'login '  + pw
    #users[session['uuid']]={'username':message}
    #updateRoster()
    #merge test
    
#DISCONNECT
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    #disconnect happens when you close the thing!
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()


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
     
