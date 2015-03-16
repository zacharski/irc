#server.py
#test

import psycopg2
import psycopg2.extras
import traceback

import os
import uuid
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

def connectToDB():
  #print 'in connectToDB'
  connectionString = 'dbname=irc_db user=postgres password=pg host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database - in server.py")
    traceback.print_exc()

messages = [{'text':'test', 'name':'testName'}]

#im trying to pull out all the users into this global variable
#so that the rest of the session based code will work


#USERS IS A DICTIONARY
users = {} #hopefully this can be changed from update roster


#WHat the actual is this thing doing.
def updateRoster():
    print 'IN UPDATEROSTER'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    users_select_string = "SELECT users FROM users;"
    try:
        cur.execute(users_select_string)
        print 'executed users query'
        users = cur.fetchall()
        print 'fetched all the users'

        #im going to try setting names equal to users
        names = users
        #need to check in database here?
        for bob_guy in users:
            print bob_guy
        
        #its getting a thing that looks like this: ['(1,SpiderBall,sb)'] and more stuff like it
        thingToPutInNames = users[0]
        print thingToPutInNames
        
        for item in names:
            print 'meow'
            print 'a thing in names is:' + item[0]
        #for user_id in users:
        #print users[user_id]['username'] #user_id is one of the users, and we are grabbing
                                                #the username for each user
        
            #if there is no chars in the username
        #    if len(users[user_id]['username'])==0:
        #        names.append('Anonymous')
        #    else:
        #        names.append(users[user_id]['username'])
        
        #This broadcasting names thing happens a lot. seems each time you call identify 
        #and login
        print 'broadcasting names'
        #I don't know what broadcast does?. changed it to false nothing seemed to change
        emit('roster', names, broadcast=True)
    except:
        print 'Could not pull user roster from db'
        traceback.print_exc()

#CONNECT    
#I think this is where we wire in the database?
#i believe this is actually where we start connecting to the session -Savannah
#for right now at least
@socketio.on('connect', namespace='/chat') #handles the connect event
def test_connect():
    print 'IN CONNECT'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    uuidVar = session['uuid']=uuid.uuid1()#each time a uuid is called, a new number is returned
    
    sessionUsername = session['username']='starter name'
    #print 'connected'
    session['uuid']=uuid.uuid1()#each time a uuid is called, a new number is returned
    session['username']='starter name'
    print 'connected'
    
    #this means that it goes to the users list thing and gets the session id (this instance of the chat
    #and makes the username field = new user
    
    users[session['uuid']]={'username':'New User'}
    
    #updateRoster is called here. duh. it goes to...
    updateRoster()
    
    for item in messages:
        emit('message', item)
    
 #   try:
        #this will be the query 
   #     print("This will be a query")
    #    cur.execute#
#    except:
     #   print ("I didn't get to do the query.")
       # traceback.print_exc()
    

#MESSAGE
#THIS IS ON LINE 55 IN INDEX.HTML $scope.send - emits message and text
@socketio.on('message', namespace='/chat')
def new_message(message):
    print 'IN MESSAGE'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print 'the message typed was:' + message
   
    messageToGoInDB = message
    originalPosterID = 78
    insertStatement = "INSERT INTO messages (original_poster_id, message_content) VALUES (%s, %s)"
    
    try: 
        cur.execute(insertStatement, (originalPosterID, messageToGoInDB));
    except:
        print "there was an error with the insert"
        traceback.print_exc()
        
    conn.commit()
    
    #take what is in the database, take from the users column and then make it into a python dict called users
    tmp = {'text':message, 'username':'testNameYup'}
    #user is not a real thing yet, its also just an iterator in python. 
    #users is supposed to be the results from the database.
    
    thisSessionNum = session['uuid']
    
    user = users[thisSessionNum]['username']
    print 'user is :' + user
    if user in users:
        tmp = {'text':message, 'username':user}
   
    #messages is a list of python dictionaries that look like {messages,users} 
    messages.append(tmp)
    
    emit('message', tmp, broadcast=True)

#IDENTIFY    
#LINE 76ish in index.html? $scope.setName - emits identify scope.name
# $scope.setName2 also emits identify, $scope.name2
@socketio.on('identify', namespace='/chat')
def on_identify(userTypedLoginInfo):
    print 'IN IDENTIFY'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print 'identify' + userTypedLoginInfo
    #the message here is where we need to connect to check against the database??
    
    #userTypedLogininfo is the real time variable that is displaying in the server console window and it is being displayed as 
    #the user types things into the username box.
    #we might need to get the username from here and the password from here and get the thing
    users[session['uuid']]={'username':userTypedLoginInfo}
    updateRoster()
    
#LOGI://www.youtube.com/nsprandom% N
#around line 85 index.html $scope.processLogin - emits login, $scope.password
@socketio.on('login', namespace='/chat')
def on_login(loginInfo):
    print 'IN LOGIN'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #pw is whatever was typed into the password box
   
    #this works if it is a string.
    
    usernameVar = loginInfo['username']
    passwordVar = loginInfo['password']
    #THIS DOESN"T WORK YET
    print 'user:' + loginInfo['username']
    print 'pass:'  + loginInfo['password']
    
    user_select_string = "SELECT username FROM users WHERE username = %s AND password = %s;"

    try:
        cur.execute(user_select_string,(usernameVar, passwordVar));
        print 'executed query'
        currentUser = cur.fetchone()

        if(currentUser is None):
            print 'this is not a valid login, please try again'
        else:
            
            print 'successfully fetched one value'
        
            print 'sessionuser:' + session['username']
            #print 'sessionpass:' + session['password']        
        
            print 'currentUser:' + str(currentUser)
            #print 'sessionpass:' + session['password']        
        
            session['username'] = currentUser['username']
            #session['password'] = currentUser['password']

            print 'Logged on as:' + session['username'] #+ 'with pw' + session['password']
    except:
        print 'could not execute login query!'
        traceback.print_exc()
    #users[session['uuid']]={'username':message}
    #updateRoster()
    
#DISCONNECT
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'DISCONNECT'
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
     
