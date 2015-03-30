import psycopg2
import psycopg2.extras
import traceback

import os
import uuid
from flask import Flask, session, jsonify, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room

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

#the list of rooms
rooms = []

#USERS IS A DICTIONARY
users = {} 
names = []
#What the actual is this thing doing.
app.debug = True

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]

rooms = ['General']

def updateRoster():
    names = []
    for user_id in  users:
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    traceback.print_exc()
    emit('roster', names, broadcast=True)

#UPDATE ROOMS
def updateRooms():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    #I know we need this, but not sure where to put it
    room = data['room']
    
    roomInsertQuery="INSERT INTO rooms (roomname) VALUES (%s)" 
    
    try:
        cur.execute(roomInsertQuery, room)
    except:
        print "I couldn't do the room insert augh"
        traceback.print_exc()
    
    

#we also need a thing that pulls up messages from a chat
#maybe have a subscribe function that determines whether or not join is called??

#THIS IS NOT MINE COPIED FROM DOCUMENTATION, then edited a little bit
@socketio.on('join', namespace='/chat')
#data needs to become session stuff maybe???
def on_join(data):
    print "data username is " + data['username']
    print "data room is " + data['room']
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave', namespace='/chat')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)
#END COPIED FROM DOCS


#CONNECT    
@socketio.on('connect', namespace='/chat') #handles the connect event
def test_connect():
    print 'IN CONNECT'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    session['uuid']=uuid.uuid1()# each time a uuid is called, a new number is returned

    session['username']='starter name'
    #print 'connected'
    
    #this means that it goes to the users list thing and gets the session id 
    #this instance of the chat and makes the username field = new user
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()
    updateRooms()
    
    for item in messages:
        emit('message', item)


#MESSAGE
#THIS IS ON LINE 55 IN INDEX.HTML $scope.send - emits message and text
@socketio.on('message', namespace='/chat')
def new_message(message):
    print 'IN MESSAGE'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #print 'the message typed was:' + message
    
    
    messageToGoInDB = message
    
    #get id here from users
    posterIdQuery = "SELECT id FROM users;"
    try:
        cur.execute(posterIdQuery)
    except:
        print("couldn't get posterID from users!")
    listOfPosterIDs = cur.fetchall()
    
    originalPosterID = -7
            
    #first get the username of the person who is posting.
    thisSessionNum = session['uuid']
    currentUsername = users[thisSessionNum]['username']
   
    #then go through database and get that user's id
    userIdSelectQuery = "SELECT id FROM users WHERE username = %s"
    try:
        cur.execute(userIdSelectQuery, (currentUsername,))
    except:
        print("I had a problem getting the users id from their username.")
    usersIdResult = cur.fetchone()
    
    originalPosterID = usersIdResult[0] 
    
    #insert message into the database    
    insertStatement = "INSERT INTO messages (original_poster_id, message_content) VALUES (%s, %s)"
    try: 
        cur.execute(insertStatement, (originalPosterID, messageToGoInDB));
    except:
        print "there was an error with the insert"
        traceback.print_exc()
        
    conn.commit()
    
    #take what is in the database, take from the users column and then 
    #make it into a python dict called users
    tmp = {'text':message, 'username':session['username']}
    
    thisSessionNum = session['uuid']
    user = users[thisSessionNum]['username']
    if user in users:
        tmp = {'text':message, 'username':user}
    
    #messages needs the room stuff too!
    #added rooms into tmp, which means that it is a part of the message thing
        
    #messages is a list of python dictionaries that look like {messages,users} 
    messages.append(tmp)
    
    emit('message', tmp, broadcast=True)


#IDENTIFY    
#LINE 76ish in index.html? $scope.setName - emits identify scope.name
# $scope.setName2 also emits identify, $scope.name2
@socketio.on('identify', namespace='/chat')
def on_identify(userTypedLoginInfo):
    print 'IN IDENTIFY'
    # conn = connectToDB()
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #print 'identify' + userTypedLoginInfo
    #the message here is where we need to connect to check against the database??
    
    #userTypedLogininfo is the real time variable that is displaying in the server console window and it is being displayed as 
    #the user types things into the username box.
    #we might need to get the username from here and the password from here and get the thing
    if 'uuid' in session:
        users[session['uuid']]={'username':userTypedLoginInfo}
        updateRoster()
    else:
        print 'sending information'
        session['uuid']=uuid.uuid1()
        session['username']='starter name'
  
    
        updateRoster()
        updateRooms()

        for message in messages:
            emit('message', message)
    
    users[session['uuid']]={'username':userTypedLoginInfo}
    updateRoster()
    #call update rooms with update roster?
   
    
#LOGIN
#around line 85 index.html $scope.processLogin - emits login, $scope.password
@socketio.on('login', namespace='/chat')
def on_login(loginInfo):
    print 'IN LOGIN'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    usernameVar = loginInfo['username']
    passwordVar = loginInfo['password']
    #print 'user:' + loginInfo['username']
    #print 'pass:'  + loginInfo['password']
    oldMessages = [{'text':'oldMessageInitText', 'username':'oldMessageInitUsername'}]
    
    user_select_string = "SELECT username FROM users WHERE username = %s AND password = %s;"

    try:
        cur.execute(user_select_string,(usernameVar, passwordVar));
        #print 'executed query'
        currentUser = cur.fetchone()
        if(currentUser is None):
            print 'this is not a valid login, please try again'
        else:
            session['username'] = currentUser['username']
            print 'Logged on as:' + session['username'] 
    except:
        print 'could not execute login query!'
        traceback.print_exc()
    
    #printing all previous messages from database here.
    #this part grabs the stuff from messages
    messageQuery = "SELECT message_content, original_poster_id FROM messages;"
    try:
        cur.execute(messageQuery)
    except:
        print("I couldn't grab messages from the previous database")
    previousMessages = cur.fetchall()
    
    for message in previousMessages:
        messageStr = str(message['message_content'])
        #print 'a previous message was:' + messageStr
        idStr = str(message['original_poster_id'])
        #print 'the users id was: ' + idStr
    
        #this part grabs the stuff from users
        userQuery = "SELECT id, username FROM users WHERE id = %s;"
        try:
            cur.execute(userQuery, (idStr,))
        except:
            print("I couldn't grab users from database")
        idMatchUserResults = cur.fetchall()    
       
        theUserMatchName = "" 
        for user in idMatchUserResults:
            #print 'the id is:' + idStr
            theUserMatchName = user['username']
            #print 'the username that hopefully matches is' + theUserMatchName
        temp = {'text':messageStr, 'username':theUserMatchName}   
        oldMessages.append(temp)
        #oldMessages = [{'text':messageStr, 'username':theUserMatchName}]    
    
    count = 0   
    for item in oldMessages:    
        if count >= len(oldMessages):
            thing = 'nope'
        else :
            usernameName = oldMessages[count]['username']
            messageFromUsername = oldMessages[count]['text']
            print messageFromUsername
            print 'from:' + usernameName 
            count = count + 1
    #put emit here
            emit('message', item)
    
     
    #what why is this commented out. zacharski did that and I don't know. 
    #users[session['uuid']]={'username':message}
    #updateRoster()


#SEARCH RESULTS
@socketio.on('search', namespace='/chat')
def on_search(searchTerm):
    print 'IN SEARCH'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #grab search term from database. 
    #somehow we need to get access to the current room
    print roomName
    print searchTerm
    searchTerm = '%'+ searchTerm +'%'
    #make select statement and execute query
    searchQuery = "SELECT messages.message_content FROM messages WHERE messages.message_content LIKE %s AND rooms.roomname = %s JOIN messages ON rooms.id = messages.room_id" #create a join to a room here
    try:
        print 'entering try'
        cur.execute(searchQuery,(roomName, searchTerm));
        print 'query successfully executed'
    except:
        print 'could not execute search query!'
        traceback.print_exc()
    searchResults = cur.fetchall()
    #return and print results in chat messages
    for item in searchResults:
        print len(searchResults)
        if item:
            item = {'text': str(item[0])}
            emit('search', item)
        else:
            print 'there is nothing here'
    #if time, then print out messages in another spot
    #do this by changing emit to send it somewhere else 


#need another route here for rooms
#call update rooms

    
#DISCONNECT
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'DISCONNECT'
    #disconnect happens when you close the thing!
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()

    emit('roster', names)
    
@socketio.on('new_room', namespace='/chat')
def new_room(the_room): 
    print 'updating rooms'
    rooms.append(the_room)
    updateRooms()
    print 'back'

    # return jsonify(success= "ok")

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
     
