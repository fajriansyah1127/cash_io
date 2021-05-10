from flask import Flask, request,render_template,jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api
from flask_cors import CORS
from mysql.connector import MySQLConnection
# import mysql.connector
import json
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

def DB():
    filejson=open('config_ippl.json','r') # Get Data from config.json 
    config = json.loads(filejson.read()) #Parse the data
    db = MySQLConnection(host=config['host'],user=config['user'],password=config['password'],database=config['database'])
    return db

def queryToDb(db,query, value): #FOR CREATE UPDATE N DELETE
    try:
        cursor = db.cursor()
        cursor.execute(query, value)
        db.commit()
        effectedRow = cursor.rowcount
        cursor.close()
        db.close()
    except Exception as e:
        return 0
    else:
        return int(effectedRow) 

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : "Please, Re-Login"})
        
        db = DB()
        curUser = db.cursor(dictionary=True)
        try:
            data = jwt.decode(token,"secret",algorithms="HS256")
            curUser.execute(f"SELECT * from users WHERE public_id='{data['public_id']}'")
            cur_user = curUser.fetchone()
            endCon(db,curUser)
        except Exception as e:
            return jsonify({'message' : "Token is Invalid !","ERR": str(e)})

        return f(cur_user, *args, **kwargs)
    return decorated

@app.route("/",methods=['GET']) 
def index():
    return 'Hello'

@app.route ("/user",methods=['GET', 'POST'])
@token_required
def user():
    if cur_user['admin'] == 0 :
        return jsonify({'message' : "Illegal User for this Function"})
    if request.method == 'GET' : #GET ALL USER
        db=DB()
        cursor=db.cursor()
        cursor.execute("SELECT * FROM user ")
        user=cursor.fetchall()
        cursor.close()
        db.close()
        # print(user)
        return json.dumps(user)
    
    # {
    #     "username": .... ,
    #     "pin" : 123,
    #     "nama_toko" : salwa
    # }
    elif request.method == 'POST': #Create User
        data = request.get_json()
        query = """INSERT INTO user(username, pin, nama_toko, saldo) VALUES (%s, %s, %s, 0)"""
        value = (data['username'],generate_password_hash(data['pin'],method='sha256'), data['nama_toko'])
        exc = queryToDb(DB(), query, value)
        res = ''        
        if exc < 1 :
            res = "Fail"
        else :
            res = "Success"
        return jsonify({'Notification' : res})

@app.route("/user/<id_user>",methods=['PUT', 'GET', 'DELETE'])
def userCrud(id_user):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM user WHERE id_user='{id_user}'")
    user = cur.fetchone()
    cur.close()
    db.close()
    userToDict = lambda r : dict(id_user=r[0],username=r[1],pin=r[2],nama_toko=r[3],saldo=r[4]) 
    
    if user==None:
        return jsonify({"message" : "fail,User Not Found"})
    elif request.method == 'GET': # GET ONE USER
        return jsonify({"message" : "success", "result" : userToDict(user)})
    elif request.method == 'PUT': # UPDATE USER
        db=DB()
        cur=db.cursor()
        query = f"UPDATE user SET admin = 1 WHERE user.id_user='{id_user}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()

        return jsonify ({"msg" : "Fail" if c<1 else "Success"})
    elif request.method == 'DELETE': # DELETE USER 
        db=DB()
        cur=db.cursor()
        query = f"DELETE FROM user WHERE id_user='{id_user}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()

        return jsonify({"msg" : "Fail" if c<1 else "Success"})

@app.route("/user/DownGrade/<id_user>",methods=['PUT'])
def DownGrade(id_user):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM user WHERE id_user='{id_user}'")
    user = cur.fetchone()
    cur.close()
    db.close()
    userToDict = lambda r : dict(id=r[0],id_user=r[1],name=r[2],password=r[3][5:],admin="YES" if r[4]==1 else "NO")
    
    if user==None:
        return jsonify({"message" : "Ggagal,User Tidak Ditemukan"})
    elif user[4] == 0: 
        return jsonify({"message" : "Gagal, Bukan Admin, Ngapain di downgrade" })
    
    elif request.method == 'PUT' : #UPDATE user

        db = DB()
        cur = db.cursor()
        query = f"UPDATE user SET admin = 0 WHERE user.id_user='{id_user}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        
        return jsonify ({"msg" : "Fail" if c<0 else "Success"})

@app.route("/user/editpin/<username>",methods=['PUT']) 
def editpin(username):
    db = DB()
    cur = db.cursor()
    # if not nim :
        # return jsonify({"message" : "User tidak tersedia"})
    # query = f"UPDATE user SET admin = 0 WHERE user.id_user='{id_user}'"
    pinbaru = request.get_json()
    cur.execute(f"UPDATE user SET pin = '{pinbaru['new_pin']}' WHERE username='{username}'")
    db.commit()
    c=cur.rowcount
    cur.close()
    db.close()
    return jsonify ({"msg" : "Fail" if c<0 else "Success"})


@app.route("/login")
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Wajib Diisi", 401,{'WWW-Authenticate' : 'Basic-realm="Login Required!"'})
    db=DB()
    cur=db.cursor(buffered=True,dictionary=True)
    query = f"SELECT * FROM user WHERE username='{auth.username}'"
    cur.execute(query)
    db.commit()
    userData = cur.fetchone()
    cur.close()
    db.close()
    
    if not userData:
        return make_response("User tidak terdaftar", 401,{'WWW-Authenticate' : 'Basic-realm="Login Required!"'})
    print(auth.password)
    print(userData['pin'])
    if check_password_hash(str(userData['pin']), auth.password):
        token = jwt.encode({'username' : userData['username'],
                     'exp' : str(datetime.datetime.now() + datetime.timedelta(minutes=30))}, 'RAHASIA',algorithm="HS256")
        # return jsonify({"token" : token.decode("UTF-8")})
        return jsonify({"token" : token})

    return make_response("Wrong Password",401,{"WWW-Authenticate" : "Basic realm='Login Required!'"})
    


        














if __name__ == "__main__":
    app.run(debug=True)