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
#printed = False
#USERS IS A DICTIONARY
users = {} 
names = []
current_subs = []
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
    
    selectRoomsQuery = "SELECT * FROM rooms;"
    cur.execute(selectRoomsQuery)
    previous_rooms = cur.fetchall()

    #if not printed:
    rooms = []
    for room in previous_rooms:
        print room[1]
        rooms.append(room[1])

    #printed = True
    emit('rooms', rooms)    
    

def getSubscriptions(username):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    user_id = getUserId(username)
    selectSubQuery = "SELECT room_id FROM subscriptions WHERE user_id = %s;"
    cur.execute(selectSubQuery, (user_id,))
    subs = cur.fetchall()
    for sub in subs:
        print "this person is subscribed to a chat with the id: " + sub[2]
        current_subs.append(sub[2]) #just stores room_id


def getUserId(username):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    userIdSelectQuery = "SELECT id FROM users WHERE username = %s;"
    
    id_dict = 0 #initializing id_dict, just in case

    try:
        print "trying to execute select room id"
        cur.execute(userIdSelectQuery, (username,))
        print "sucessfully executed select room id "
        
        print "trying to grab id"
        id_dict = cur.fetchone()
        print "this is the current user id  " + str(id_dict[0])


    except:
        print "could not execute select user id"
        traceback.print_exc()
    return id_dict



def getRoomId(roomname):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    roomIdSelectQuery = "SELECT id FROM rooms WHERE roomname = %s;"
    
    id_dict = 0 #initializing id_dict, just in case

    try:
        print "trying to execute select room id"
        cur.execute(roomIdSelectQuery, (roomname,))
        print "sucessfully executed select room id "
        
        print "trying to grab id"
        id_dict = cur.fetchone()
        print "this is the current room id" + str(id_dict[0])


    except:
        print "could not execute select room id"
        traceback.print_exc()
    return id_dict

#we also need a thing that pulls up messages from a chat
#maybe have a subscribe function that determines whether or not join is called??

#THIS IS NOT MINE COPIED FROM DOCUMENTATION, then edited a little bit
@socketio.on('join', namespace='/chat')
#data needs to become session stuff maybe???
def on_join(data):
    #print "data username is " + data['username']
    #print "data room is " + data['room']
    #username = data['username']
    room = data
    join_room(room)

@socketio.on('leave', namespace='/chat')
def on_leave(data):
    #username = data['username']
    room = data
    leave_room(room)
#END COPIED FROM DOCS


#CONNECT    
@socketio.on('connect', namespace='/chat') #handles the connect event
def test_connect():
    print 'IN CONNECT'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    session['uuid']=uuid.uuid1()# each time a uuid is called, a new number is returned

    session['username']='starter name'
    session['room'] = 'General'
    #session['room']['room_id'] = 
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
def new_message(message, roomName):
    print 'IN MESSAGE'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #print 'the message typed was:' + message
    
    updateRooms()
    print "just called update rooms, now back in message"
    
    
    messageToGoInDB = message
    print 'the message typed was:' + message
    
    print 'the room typed was:' + roomName
   
    #roomNameQuery = "INSERT into" 
    temp_room_id = getRoomId(roomName)
    print "this is the room id " + str(temp_room_id)
    room_id = temp_room_id[0]
    
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
   
    #get roomid here
    
        #first get room name from site?
    
    
        #then do a select for the room id that matches that room name
    #but we aren't inserting into the room table yet so we can't do that.
    
    
    #insert message into the database    
    insertStatement = "INSERT INTO messages (original_poster_id, message_content, room_id) VALUES (%s, %s, %s)"
    try: 
        cur.execute(insertStatement, (originalPosterID, messageToGoInDB, int(room_id)));
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
    
    #from zacharskis
    tmp = {'text':message, 'room':roomName, 'username':users[session['uuid']]['username']}
    
        
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
    updateRooms()
    #call update rooms with update roster?
   
    
#LOGIN
#around line 85 index.html $scope.processLogin - emits login, $scope.password
@socketio.on('login', namespace='/chat')
def on_login(loginInfo):
    print 'IN LOGIN'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    previousMessages = []
    usernameVar = loginInfo['username']
    passwordVar = loginInfo['password']
    #print 'user:' + loginInfo['username']
    #print 'pass:'  + loginInfo['password']
    oldMessages = [{'text':'oldMessageInitText', 'username':'oldMessageInitUsername'}]
    
    user_select_string = "SELECT id, username FROM users WHERE username = %s AND password = %s;"

    try:
        cur.execute(user_select_string,(usernameVar, passwordVar));
        #print 'executed query'
        currentUser = cur.fetchone()
        if(currentUser is None):
            print 'this is not a valid login, please try again'
        else:
            session['username'] = currentUser['username']
            subsSelectQuery = "SELECT room_id FROM subscriptions WHERE user_id = %s";
            cur.execute(subsSelectQuery, (currentUser['id'],))
            sub_results=cur.fetchall()
            subscriptions = []
            for sub in sub_results:
                subscriptions.append(sub[0])
            session['current_subs'] = subscriptions


            print 'Logged on as:' + session['username'] 
    except:
        print 'could not execute login query!'
        traceback.print_exc()
    
    #printing all previous messages from database here.
    subs_string = str(tuple(session['current_subs']))
    #this part grabs the stuff from messages
    messageQuery = "SELECT message_content, original_poster_id FROM messages WHERE room_id IN %s;"%subs_string 
    print messageQuery
    try:
        print "entering try with current_subs"
        cur.execute(messageQuery) #this may not work, but imma try it
        print "successfully executed query"
        previousMessages = cur.fetchall()
        print "successfully fetched"
    except:
        print("I couldn't grab messages from the previous database")
    
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
    #this searches in the room in session, not what users are subscribed to
    print 'IN SEARCH'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    roomName = session['room']
    print roomName
    print searchTerm
    searchTerm = '%'+ searchTerm +'%'
    #make select statement and execute query
    searchQuery = "SELECT messages.message_content FROM messages INNER JOIN rooms ON rooms.id = messages.room_id WHERE messages.message_content LIKE %s AND rooms.roomname = %s;" 
    try:
        print 'entering try'
        cur.execute(searchQuery,(searchTerm, roomName));
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
def new_room(room): 
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print 'updating rooms'
    rooms.append(room)
    session['room'] = room

    
    roomInsertQuery="INSERT INTO rooms (id, roomname) VALUES (DEFAULT, %s)" 
    
    #this pos isn't working, it either gives me a syntax error
    #roomInsertQuery="INSERT INTO rooms (id, roomname) SELECT * FROM rooms WHERE NOT EXISTS (SELECT roomname FROM rooms WHERE roomname = %s)" 
    try:
        cur.execute(roomInsertQuery, (room,))
        print "did the thing successfully I guess. after try and before emit"
    except:
        print "I couldn't do the room insert augh"
        traceback.print_exc()
    
    conn.commit()
    print room
   # printed = False
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
     
