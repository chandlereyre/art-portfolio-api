import json
from flask_cors import CORS
from unicodedata import name
from flask import Flask, request, session, g
from pymongo import MongoClient
from bson import json_util, objectid
import PIL.Image as Image
import io
import base64

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)
# app.config['SESSION_TYPE'] = 'mongodb'
app.config['SECRET_KEY']='secret key'
app.config['SESSION_PERMANENT']=True


client = MongoClient()
db = client.artportfolio

def parse_json(data):
    return json.loads(json_util.dumps(data))

# get username and password from file

password_file = open('login-values.txt', 'r')
registered_username = password_file.readline().strip()
registered_password = password_file.readline()

@app.route('/portfolio-items', methods=['GET', 'POST', 'DELETE'])
def portfolioItems():
    if request.method == 'POST':
        # convert dataURL to image
        head, image = request.json['image']['dataURL'].split(',', 1)

        bits = head.split(';')
        mime_type = bits[0] if bits[0] else 'text/plain'    
        _, file_type = mime_type.split('/')
        print(file_type)
        
        b = base64.b64decode(image)

        img = Image.open(io.BytesIO(b))

        # save image locally in 'img' folder
        img.save(f'/img/{request.json["name"]}.{file_type}')

        values = {  
            "name" : request.json['name'], 
            "description" : request.json['description'], 
            "image": f'/img/{request.json["name"]}.{file_type}'
        }

        if len(request.json['id']) > 0:
            global id 
            id = objectid.ObjectId(request.json['id'])
            query = { '_id': id }
            doc = db.art.find_one(query)
            if id == doc['_id']:
                db.art.replace_one(doc, values)
        else:
            db.art.insert_one(values)
        return 'done!'
    elif request.method == 'GET':
        portfolio = []
        for item in db.art.find():
            portfolio.append(parse_json(item))
        return portfolio
    elif request.method == 'DELETE':
        query = { '_id': objectid.ObjectId(request.json['id']) }
        db.art.delete_one(query)
        return 'item deleted'

@app.route('/create_session', methods=['POST', 'GET', 'OPTIONS'])
def createSession():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        print(username)
        if username == registered_username and password == registered_password:
            session['username'] = request.json['username']
            print(session)
            return 'created'
        else:
            return 'not created'
    elif request.method == 'GET':
        print(session)
        if 'username' in session:
            return 'true'
        else:
            return 'false'
    return ''
    
@app.route('/delete_session', methods=['DELETE'])
def deleteSession():
    session.pop('username')
    return 'deleted'

app.run(host='0.0.0.0', port=2000, debug=True)