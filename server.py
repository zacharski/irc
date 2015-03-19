import os
import uuid
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit
import psycopg2
import psycopg2.extras


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.debug = True

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
users = {}

def updateRoster():
    names = []
    for uid in users:
        print users[uid]['username']
        if len(users[uid]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[uid]['username'])
    print 'broadcasting names'
    emit('roster', names, broadcast=True)
    
def connectToDB():
  connectionString = 'dbname=chat user=postgres password=Calut3ch host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")

@socketio.on('connect', namespace='/chat')
def test_connect():
    session['uuid']=uuid.uuid1()
    print 'connected'
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()


@socketio.on('login', namespace='/chat')
def on_login(data):
    print 'login '
    username = data['username']
    password = data['password']
    conn = connectToDB()
    cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "select * from users where username = %s and password = crypt(%s,password)" 
    
    cur.execute(query, (username, password))
    someone = cur.fetchone()
    
    if someone:
        users[session['uuid']]={'username': data['username']}
        session['username']=data['username']
        session['id']=someone['id']
        
        text = "select text, username from messages join users on messages.user_id = users.id"
        cur.execute(text)
        stuff = cur.fetchall()
        
        for something in stuff:
            something = {'text': something['text'], 'name': something['username']}
            emit('message', something)
        updateRoster()
    else:
        print 'user or password not valid'
    



@socketio.on('message', namespace='/chat')
def new_message(text):
    
    if 'username' in session: #if the username is logged in currently
        temp = {'text':text, 'name':users[session['uuid']]['username']}
        messages.append(temp)
        emit('message', temp, broadcast=True)
        
        
        #inserting new message into chat
        conn = connectToDB()
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "INSERT INTO messages VALUES(DEFAULT, %s, %s)" 
        
        cur.execute(query, (text, session['id']))
        conn.commit()
        
        

    
@socketio.on('identify', namespace='/chat')
def on_identify(text):
    print 'identify' + text
    users[session['uuid']]={'username':text}
    updateRoster()

@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()


#search function
@socketio.on('search', namespace='/chat')
def search(term):
    if 'username' in session:
        term = '%' + term +'%'
        conn = connectToDB()
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT text, username FROM messages JOIN users ON messages.user_id = users.id WHERE text LIKE %s OR username LIKE %s"
        cur.execute(query, (term, term))
        stuff = cur.fetchall()
        for result in stuff:
            result = {'text': result['text'], 'name': result['username']}
            emit('result', result)
            
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