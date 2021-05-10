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

app = Flask(__name__)

def DB():
    filejson=open('config.json','r') # Get Data from config.json 
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
        return e
    else:
        return int(effectedRow) 

@app.route("/",methods=['GET'])
def index():
    return ''
################        PENJUALAN ########################################

@app.route("/penjualan",methods=['GET','POST'])
def penjualan():
    if request.method == 'GET': # GET ALL Penjualan
        db=DB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM penjualan")
        penjualan = cursor.fetchall()
        cursor.close()
        db.close()
        penjualanTodict = lambda r : dict(id=r[0],daftar_barang=r[1],total_harga=r[2],dibayar=r[3]
        ,kembalian=r[4])
        return json.dumps(list(map(penjualanTodict,[r for r in penjualan])))

    elif request.method == 'POST': # CREATE penjualan
        data = request.get_json()
        query = """INSERT INTO penjualan(daftar_barang,total_harga,dibayar,kembalian ) VALUES (%s,%s,%s,%s)"""
        value = (data["daftar_barang"],data["total_harga"],data["dibayar"],data["kembalian"])
        return jsonify({'message' : "Fail" if queryToDb(DB(),query,value) <1 else "Succes"})

################        PENJUALAN ########################################
@app.route("/penjualan/<id>",methods=['PUT','GET','DELETE'])
def penjualanCrud(id):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM penjualan WHERE id='{id}'")
    penjualan = cur.fetchone()
    cur.close()
    db.close()
    penjualanTodict = lambda r : dict(id=r[0],daftar_barang=r[1],total_harga=r[2],dibayar=r[3]
        ,kembalian=r[4])
    if penjualan==None:
        return jsonify({"message" : "fail,penjualan Not Found"})
    
    if request.method == "PUT":
        newpenjualan = request.get_json()
        db=DB()
        cur=db.cursor()
        query = f"""UPDATE penjualan 
                    SET daftar_barang='{newpenjualan['daftar_barang']}',total_harga='{newpenjualan['total_harga']}',
                    dibayar='{newpenjualan['dibayar']}',
                    kembalian='{newpenjualan['kembalian']}'
                    WHERE penjualan.id='{id}'"""
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({'message' : 'Gagal update' if c<1 else 'Berhasil update'})
    elif request.method == 'GET': # GET ONE transaksi
        return jsonify({"message" : "success", "result" : penjualanTodict(penjualan)})
    
    elif request.method == 'DELETE': # DELETE penjualan
        # return ''
        db=DB()
        cur=db.cursor()
        query = f"DELETE FROM penjualan WHERE id='{id}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({"msg" : "Fail" if c<1 else "Success"})
    
    

################        PENJUALAN     ########################################


################        TRANSAKSI ########################################
@app.route("/transaksi",methods=['GET','POST'])
def transaksi():
    if request.method == 'GET': # GET ALL Penjualan
        db=DB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM transaksi")
        transaksi = cursor.fetchall()
        cursor.close()
        db.close()
        transaksiTodict = lambda r : dict(id=r[0],tanggal_transaksi=r[1],keterangan=r[2],jenis_transaksi=r[3]
        )
        return json.dumps(list(map(transaksiTodict,[r for r in transaksi])))

    elif request.method == 'POST': # CREATE penjualan
        data = request.get_json()
        query = """INSERT INTO transaksi(tanggal_transaksi,keterangan,jenis_transaksi) VALUES (%s,%s,%s)"""
        value = (data["tanggal_transaksi"],data["keterangan"],data["jenis_transaksi"])
        return jsonify({'message' : "Fail" if queryToDb(DB(),query,value) <1 else "Succes"})
    
   

@app.route("/transaksi/<id>",methods=['PUT','GET','DELETE']) 
def transaksiCrud(id):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM transaksi WHERE id='{id}'")
    transaksi = cur.fetchone()
    cur.close()
    db.close()
    transaksiTodict = lambda r : dict(id=r[0],tanggal_transaksi=r[1],keterangan=r[2],jenis_transaksi=r[3])

    if transaksi==None:
        return jsonify({"message" : "fail,transaksi Not Found"})
    elif request.method == 'GET': # GET ONE transaksi
        return jsonify({"message" : "success", "result" : transaksiTodict(transaksi)})
    
    elif request.method == "PUT":
        newtransaksi = request.get_json()
        db=DB()
        cur=db.cursor()
        query = f"""UPDATE transaksi
                    SET tanggal_transaksi='{newtransaksi['tanggal_transaksi']}',keterangan='{newtransaksi['keterangan']}',
                    jenis_transaksi='{newtransaksi['jenis_transaksi']}'
                    WHERE transaksi.id='{id}'"""
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({'message' : 'Gagal update' if c<1 else 'Berhasil update'})
    elif request.method == 'DELETE': # DELETE penjualan
        # return ''
        db=DB()
        cur=db.cursor()
        query = f"DELETE FROM transaksi WHERE id='{id}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()

        return jsonify({"msg" : "Fail" if c<1 else "Success"})

@app.route("/transaksi/<tanggal_transaksi>",methods=['GET']) 
def tanggal_transaksi(tanggal_transaksi):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM transaksi WHERE tanggal_transaksi='{tanggal_transaksi}'")
    transaksi_tanggal = cur.fetchone()
    cur.close()
    db.close()
    transaksi_tanggalTodict = lambda r : dict(id=r[0],tanggal_transaksi=r[1],keterangan=r[2],jenis_transaksi=r[3])

    if transaksi_tanggal==None:
        return jsonify({"message" : "fail,transaksi Not Found"})
    elif request.method == 'GET': # GET ONE transaksi
        return jsonify({"message" : "success", "result" : transaksi_tanggalTodict(transaksi_tanggal)})

################        TRANSAKSI ########################################

################        BARANG_RETAIL ########################################
@app.route("/barang_retail",methods=['GET','POST'])
def barang_retail():
    if request.method == 'GET': # GET ALL barang_retail
        db=DB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang_retail")
        barang_retail = cursor.fetchall()
        cursor.close()
        db.close()
        barang_retailTodict = lambda r : dict(id=r[0],nama_barang=r[1],harga=r[2],tanggal_kadaluarsa=r[3]
        ,jumlah_barang=r[4],merk=r[5])
        return json.dumps(list(map(barang_retailTodict,[r for r in barang_retail])))

    elif request.method == 'POST': # CREATE barang_retail
        data = request.get_json()
        query = """INSERT INTO barang_retail(nama_barang,harga,tanggal_kadaluarsa,jumlah_barang,merk) VALUES (%s,%s,%s,%s,%s)"""
        value = (data["nama_barang"],data["harga"],data["tanggal_kadaluarsa"],data["jumlah_barang"],data["merk"])
        return jsonify({'message' : "Fail" if queryToDb(DB(),query,value) <1 else "Succes"})

@app.route("/barang_retail/<id>",methods=['PUT','GET','DELETE'])
def barang_retailCrud(id):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM barang_retail WHERE id='{id}'")
    barang_retail = cur.fetchone()
    cur.close()
    db.close()
    barang_retailTodict =lambda r : dict(id=r[0],nama_barang=r[1],harga=r[2],tanggal_kadaluarsa=r[3],jumlah_barang=r[4],merk=r[5])
    if barang_retail==None:
        return jsonify({"message" : "fail,barang_retail Not Found"})
    elif request.method == 'GET': # GET ONE barang_retail
        return jsonify({"message" : "success", "result" :barang_retailTodict(barang_retail)})

    elif request.method == "PUT":
        newbarang_retail = request.get_json()
        db=DB()
        cur=db.cursor()
        query = f"""UPDATE barang_retail
                    SET nama_barang='{newbarang_retail['nama_barang']}',
                    harga='{newbarang_retail['harga']}',
                    tanggal_kadaluarsa='{newbarang_retail['tanggal_kadaluarsa']}',
                    jumlah_barang='{newbarang_retail['jumlah_barang']}',
                    merk='{newbarang_retail['merk']}'
                    WHERE barang_retail.id='{id}'"""
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({'message' : 'Gagal update' if c<1 else 'Berhasil update'})
    
    elif request.method == 'DELETE': # DELETE penjualan
        # return ''
        db=DB()
        cur=db.cursor()
        query = f"DELETE FROM barang_retail WHERE id='{id}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({"msg" : "Fail" if c<1 else "Success"})

################        BARANG_RETAIL ########################################

################        BARANG_NONRETAIL ########################################
@app.route("/barang_nonretail",methods=['GET','POST'])
def barang_nonretail():
    if request.method == 'GET': # GET ALL barang_nonretail
        db=DB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang_nonretail")
        barang_nonretail = cursor.fetchall()
        cursor.close()
        db.close()
        barang_nonretailTodict = lambda r : dict(id=r[0],nama_barang=r[1],harga=r[2],status=r[3])
        return json.dumps(list(map(barang_nonretailTodict,[r for r in barang_nonretail])))

    elif request.method == 'POST': # CREATE barang_nonretail
        data = request.get_json()
        query = """INSERT INTO barang_nonretail(nama_barang,harga,status) VALUES (%s,%s,%s)"""
        value = (data["nama_barang"],data["harga"],data["status"])
        return jsonify({'message' : "Fail" if queryToDb(DB(),query,value) <1 else "Succes"})

@app.route("/barang_nonretail/<id>",methods=['PUT','GET','DELETE'])
def barang_nonretailCrud(id):
    db = DB()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM barang_nonretail WHERE id='{id}'")
    barang_nonretail = cur.fetchone()
    cur.close()
    db.close()
    barang_nonretailTodict =lambda r : dict(id=r[0],nama_barang=r[1],harga=r[2],status=r[3])
    if barang_nonretail==None:
        return jsonify({"message" : "fail,barang_nonretail Not Found"})
    elif request.method == 'GET': # GET ONE barang_retail
        return jsonify({"message" : "success", "result" :barang_nonretailTodict(barang_nonretail)})
    
    elif request.method == 'DELETE': # DELETE penjualan
        # return ''
        db=DB()
        cur=db.cursor()
        query = f"DELETE FROM barang_nonretail WHERE id='{id}'"
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({"msg" : "Fail" if c<1 else "Success"})

    elif request.method == "PUT":
        newbarang_nonretail = request.get_json()
        db=DB()
        cur=db.cursor()
        query = f"""UPDATE barang_nonretail
                    SET nama_barang='{newbarang_nonretail['nama_barang']}',
                    harga='{newbarang_nonretail['harga']}',
                    status='{newbarang_nonretail['status']}'
                    WHERE barang_nonretail.id='{id}'"""
        cur.execute(query)
        db.commit()
        c=cur.rowcount
        cur.close()
        db.close()
        return jsonify({'message' : 'Gagal update' if c<1 else 'Berhasil update'})

################        BARANG_NONRETAIL ########################################

if __name__ == "__main__":
     app.run(debug=True)