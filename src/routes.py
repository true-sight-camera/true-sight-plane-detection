
from sqlalchemy import text
from src.depth_map import create_depth_map_array
import tempfile
import cv2
import numpy as np
import random
from PIL import Image
from src.encryption import verify_signature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import rsa
from flask_cors import cross_origin
from flask import Blueprint, request, send_file
from main import db, app
from models import Users, Images, DevImages
import uuid
import datetime
import io
from binascii import unhexlify

    
'''
this method is used to create a user in the database w/o the pub_key
online sign up
parameters: username, hashed_password (by sha_256)

UPDATE: WORKS
'''
@cross_origin
@app.route('/api/user-web', methods=['POST'])
def create_user():
    try:
        username = request.form['username']
    except:
        return "Missing username", 400

    if db.session.execute(db.select(Users).filter_by(username=username)).scalar() is not None:
        return "User already exists", 401

    try:
        hashed_pw = request.form['password']
    except:
        return "Missing password", 400
    
    try:
        email = request.form['email']
    except:
        return "Missing email", 400

    salt = generate_salt()

    try:
        new_user = Users(id = uuid.uuid4(),salt = salt, username=username, email=email, complete_password = salt+hashed_pw)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Unable to add user: {e}", 500
    
    return "User has been signed up", 200

'''
this method checks if username is valid
meant for web UI on change if username is taken
parameters: username

returns 200, 401
UPDATE: WORKS
'''
@cross_origin
@app.route('/api/username/<username>', methods=['GET'])
def check_username(username):
    if request.method != "GET":
        return "Method not allowed", 403
    user = db.session.execute(db.select(Users).filter_by(username=username)).scalar()
    # user = Users.find_by_username(username)
    if user == None:
        return "Username valid", 200
    else:
        return "Username taken", 401

'''
this method is used to register a camera with our system for the first time
parameters: cameras pub_key, username, password

find user from database <- needs to register online first, 
moduel sends pub key
username

return 200, 403

UPDATE:  DONE
'''
@cross_origin
@app.route('/api/user', methods=["PUT"])
def update_user_pub_key():
    try:
        username = request.form['username']
    except Exception as e:
        return "Missing a username to register", 400
    
    try:
        hashed_password = request.form['password']
    except Exception as e:
        return "Missing password", 400

    try:
        pub_key = request.form['pub_key']
    except Exception as e:
        return "Missing the camera pub key", 400
    
    try:
        user = db.session.execute(db.select(Users).filter_by(username=username)).scalar()

        if user == None:
            return "User does not exist", 401

        if user.salt + hashed_password != user.complete_password:
            return "Incorrect password", 401
        
        user.pub_key = pub_key
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Unable to add pub key to user: {e}", 500
    return "User pub key updated successfully", 200

'''
this method is used to create an image in the database
parameters: signed_hash, signature created from signed_hash, encrypted_username, username,

module will http post req this endpoint

NOTE: don't flatten the image in python after reading the bytes, just hash using sha256 immediately after adding username to data. react cannot flatten and convert to rgba so please don't.

UPDATE: done
'''
@cross_origin
@app.route('/api/image', methods=["POST"])
def create_image():
    #authentication here first
    #should be username
    try:
        encrypted_username = request.form['encrypted_username']
        username = request.form["username"]
    except:
        return "Not all required data included", 400 

    user = db.session.execute(db.select(Users).filter_by(username=username)).scalar()
    if user == None:
        return "User does not exist", 401

    #decrypt it
    
    pub_key = load_pem_public_key(bytes(user.pub_key, encoding="utf-8"))

    if not verify_signature(pub_key, bytes(username, encoding="utf-8"), unhexlify(encrypted_username), False):
        return "User is not authorized", 401


    try:
        # image_file = request.files['image']
        # image_hash = request.form['image_hash']

        # image_bytes = bytearray(image_file)
        # signature = find_signature_metadata(image_bytes)

        signed_hash = request.form['signed_hash']

        hash_signature = request.form['hash_signature']

        #unsign the signed_hash using verify_signature from encryption.py and pub key
        #load pub key from file -> make sure the camera stores the priv key
        if not verify_signature(pub_key, unhexlify(signed_hash), unhexlify(hash_signature)):
            return "Unverified Signature", 401

        #create image and save it
        image = Images(image_hash = signed_hash, user_id = user.id, last_accessed=datetime.datetime.now(datetime.timezone.utc))

        
        db.session.add(image)
        db.session.commit()
        return 'Image created successfully', 200
        
    except Exception as e:
        db.session.rollback()
        return f"Unable to create image in database: {e}", 400

'''
this method checks whether an image hash matches the user id send

client has to parse username from metadata and include in request

'''
@cross_origin
@app.route('/api/image/<image_hash>/<username>/<signature>', methods=["GET", "PUT", "DELETE"])
def image_handler(image_hash, username, signature):
    image = db.session.execute(db.select(Images).filter_by(image_hash=image_hash)).scalar()
    if not image:
        return "Image not found", 404
    
    user = db.session.execute(db.select(Users).filter_by(username=username)).scalar()
    if not user:
        return "User not found", 404

    if request.method == "GET":
        image.last_accessed= datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()
        #verify user token
        pub_key = load_pem_public_key(bytes(user.pub_key, encoding="utf-8"))

        #unsign the signed_hash using verify_signature from encryption.py and pub key
        #load pub key from file -> make sure the camera stores the priv key
        print('what 1')
        print(unhexlify(image_hash))
        print(unhexlify(signature))
        if not verify_signature(pub_key, unhexlify(image_hash), unhexlify(signature)):
            return "Unverified Signature", 401
        print('what 2')

        if image.user_id != user.id:
            return "Image user doesn't match sent user", 401
        print('what 3')

        return "Image owner and user_id match", 200
    elif request.method == "PUT": # this method might not be useful
        image.user_id = user.id
        db.session.commit()
        return "Successfully updated owner", 200
    elif request.method == "DELETE": # idk why someone would ever use this lol maybe we found that someone uploaded fake data
        if image.id != user.id: #maybe we should authenticate as either root or the image owner
            return "No permissions to delete", 401
        db.session.delete(image)
        db.session.commit()
        return "Successfully deleted image", 200
    else:
        return "Method not allowed", 401

'''
not sure what this is meant to do atp
'''
@cross_origin()
@app.route('/api/image_hash', methods=["POST"])
def image_hash_check():
    #parse image from request
    if request.method != "POST":
        return
    
    try:
        image = request.files['image']
        #hash image
        print(image)
        print(request.form["image_hash"])
        return "Verified", 200
        
    except Exception as e:
        return f"Unable to parse image file: {e}", 500


'''
this method overlays a depth map onto the sent image
parameters: image, 

-> this might not be needed user_token, signature, signed_hash,

user gets the image, user_token from metadata, signature from metadata, then hash the image and send the signature with the user token

UPDATE: done
'''
@cross_origin()
@app.route("/api/depth-map", methods=["POST"])
def depth_map():
    #parse image from request
    if request.method != "POST":
        return

    try:
        image = request.files['image']
    except Exception as e:
        return f"Unable to parse image file: {e}", 500

    try: 
        #make tempfile for received image
        temp_file = tempfile.NamedTemporaryFile(suffix=".png")
        filename = temp_file.name
        image.save(filename)

        # create depth map and image arrays for overlay
        depth_map_array = create_depth_map_array(filename)
        image_array = cv2.imread(filename)

        # overlay depth map at 50% capacity
        overlay_image = cv2.addWeighted(depth_map_array, 0.6, image_array, 0.4, gamma=0)

        #save the overlay image temporarily
        overlay_file = tempfile.NamedTemporaryFile(suffix=".png")
        overlay_filename = overlay_file.name
        overlay_image = Image.fromarray(overlay_image)
        overlay_image.save(overlay_filename)

        #return 
        return send_file(overlay_filename, mimetype="image/png")
    except Exception as e:
        return f"Unable to overlay depth map {e}", 500
    
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def generate_salt():
    chars=[]
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    return ''.join(chars)
    

# @cross_origin
@app.route('/health', methods=["GET"])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return "Good health", 200
    except Exception as e:
        return f"Unable to open database connection: {e}", 500

"""
requested image store for files

TODO: TEST
"""
    
@app.route('/dev/image-store/', methods=["POST", "GET"])
def dev_images_handler():
    if request.method == "GET":
        image_id = request.args.get('id')
        image = db.session.execute(db.select(DevImages).filter_by(id=image_id)).scalar()

        return send_file(io.BytesIO(image.data), mimetype=image.mimetype, as_attachment=True,download_name=file.filename)
    
    elif request.method == 'POST':
        try:
            file = request.files['file']
            new_file = DevImages(
                filename=file.filename,
                data=file.read(),
                mimetype=file.mimetype
            )
            db.session.add(new_file)
            db.session.commit()
            return "Image uploaded successfully", 200
        except Exception as e:
            db.session.rollback()
            return f"Image not uploaded: {e}", 400