#server.py
#test

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
  print 'in connectToDB'
#changed the database name here from irc_db to irc  -- we called it irc.sql right?
  connectionString = 'dbname=irc_db user=postgres password=pg host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database - in server.py")

messages = [{'text':'test', 'name':'testName'}]

#im trying to pull out all the users into this global variable
#so that the rest of the session based code will work


#USERS IS A DICTIONARY
users = {} #hopefully this can be changed from update roster




#WHat the actual is this thing doing.
def updateRoster():
    print 'in updateRoster'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    users_select_string = "SELECT users FROM users;"
    try:
        cur.execute(users_select_string);
        print 'executed users query'
        users = cur.fetchall();
        print 'fetched all the users'

        names = []
        #need to check in database here?
        for user_id in users:
            print users[user_id]['username']
            #if there is no chars in the username
            #here we should instead check if the resultset is null
            if len(users[user_id]['username'])==0:
                names.append('Anonymous')
            else:
                names.append(users[user_id]['username'])
        #This broadcasting names thing happens a lot. seems each time you call identify 
        #and login
        print 'broadcasting names'
        #I don't know what broadcast does?. changed it to false nothing seemed to change
        emit('roster', names, broadcast=True)
    except:
        print 'Could not pull user roster from db'

#CONNECT    
#I think this is where we wire in the database?
#i believe this is actually where we start connecting to the session -Savannah
#for right now at least
@socketio.on('connect', namespace='/chat') #handles the connect event
def test_connect():
    print 'in connect'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #right now it is using sessions, I think, and it should be checking against the db?
    session['uuid']=uuid.uuid1()#each time a uuid is called, a new number is returned
    session['username']='starter name'
    print 'connected'
    
    #new user is called when the database runs?    
    users[session['uuid']]={'username':'New User'}
    
    #updateRoster is called here. duh. it goes to...
    updateRoster()

    for message in messages:
        emit('message', message)
    
    try:
        #this will be the query 
        print("This will be a query")
    except:
        print ("I didn't get to do the query.")
    

#MESSAGE
#THIS IS ON LINE 55 IN INDEX.HTML $scope.send - emits message and text
@socketio.on('message', namespace='/chat')
def new_message(message):
    print 'in message'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #tmp = {'text':message, 'name':'testName'}
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    emit('message', tmp, broadcast=True)

#IDENTIFY    
#LINE 76ish in index.html? $scope.setName - emits identify scope.name
# $scope.setName2 also emits identify, $scope.name2
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'in identify'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print 'identify' + message
    #the message here is where we need to connect to check against the database??
    #message is the username here.
    users[session['uuid']]={'username':message}
    updateRoster()
    
#LOGIN
#around line 85 index.html $scope.processLogin - emits login, $scope.password
@socketio.on('login', namespace='/chat')
def on_login(loginInfo):
    print 'IN LOGIN'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #pw is whatever was typed into the password box
    print 'login user'  + loginInfo['username']
    print 'login pass'  + loginInfo['password']
    
    user_select_string = "SELECT username FROM users WHERE username = %s AND password = %s;"

    try:
        cur.execute(user_select_string,(loginInfo['username'], loginInfo['password']));
        print 'executed query'
        currentUser = cur.fetchone()
        print 'successfully fetched one value'

        session['username'] = currentUser['username']
        session['password'] = currentUser['password']

        print 'Logged on as' + session['username'] + 'with pw' + session['password']
    except:
        print 'could not execute login query!'
    #users[session['uuid']]={'username':message}
    #updateRoster()
    
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
    print 'B'
