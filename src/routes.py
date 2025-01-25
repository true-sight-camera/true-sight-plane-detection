
from sqlalchemy import text
from plane_detection.src.depth_map import create_depth_map_array
import tempfile
import cv2
import numpy as np
import rsa
import random
from PIL import Image
from plane_detection.src.encryption import hash_image_sha256
from flask_sqlalchemy import SQLAlchemy
from flask_cors import cross_origin
from flask import Blueprint, request, send_file
from plane_detection.main import db, app
from models import Users, Images
import uuid

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def generate_salt():
    chars=[]
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    return ''.join(chars)
    

@cross_origin
@app.route('/health', methods=["GET"])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return "Good health", 200
    except Exception as e:
        return f"Unable to open database connection: {e}", 500
    
'''
this method is used to create a user in the database w/o the pub_key
online sign up
parameters: username, hashed_password (by sha_256)

TODO: test
'''
@cross_origin
@app.route('/api/user-web', methods=['POST'])
def create_user():
    try:
        username = request.form['username']
    except:
        return "Missing username", 400

    try:
        hashed_pw = request.form['password']
    except:
        return "Missing password", 400
    
    try:
        email = request.form['email']
    except:
        return "Missing email", 400

    salt = generate_salt();

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
TODO: test
'''
@cross_origin
@app.route('/api/username/<username>', methods=['GET'])
def check_username(username):
    if request.method != "GET":
        return "Method not allowed", 403
    user = Users.find_by_username(username)
    if user == None:
        return "Username valid", 200
    else:
        return "Username taken", 401

'''
this method is used to register a camera with our system for the first time
parameters: cameras pub key, username, password

find user from database <- needs to register online first, 
moduel sends pub key
user generates user_token -> basically a username

TODO: test
'''
@cross_origin
@app.route('/api/user', methods=["UPDATE"])
def populate_user():
    try:
        token = request.form['username']
    except Exception as e:
        return "Missing a user_token to register", 400
    
    try:
        hashed_password = request.form['password']
    except Exception as e:
        return "Missing password", 400

    try:
        pub_key = request.form['pub_key']
    except Exception as e:
        return "Missing the camera pub key", 400
    
    try:
        user = Users.find_by_username(token)
        if user.salt + hashed_password != user.complete_password:
            return "Incorrect password", 401
        
        user.pub_key = pub_key
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return "Unable to add pub key to user", 500
    return "User created successfully", 200

'''
this method is used to create an image in the database
parameters: signed_hash, encrypted_user_token , user_token, signature

module will http post req this endpoint

TODO: test
'''
@cross_origin
@app.route('/api/image', methods=["POST"])
def create_image():
    #authentication here first
    #should be username
    try:
        encrypted_user_token = request.form['encrypted_token'].encode('utf8')
        username = request.form["username"]
    except:
        return "Not all required data included", 400 

    user = Users.find_by_username(username)
    if not user:
        return "User is not authorized", 401

    #decrypt it
    pub_key = user.pub_key
    unencrypted_user_token = rsa.decrypt(encrypted_user_token, pub_key).decode('utf8')
    print(encrypted_user_token, unencrypted_user_token)
    if unencrypted_user_token != username:
        return "User is not authorized", 401


    try:
        # image_file = request.files['image']
        # image_hash = request.form['image_hash']

        image_bytes = bytearray(image_file)
        # signature = find_signature_metadata(image_bytes)

        signed_hash = request.form['signed_hash']

        signature = request.form['signature']

        #unsign the signed_hash using verify_signature from encryption.py and pub key
        #load pub key from file -> make sure the camera stores the priv key
        if not verify_signature(pub_key, signed_hash, signature):
            return "Unverified Signature", 401

        #compute h(m) from image
        #check that they match
        #hash
        # computed_hash = hash_image_sha256(image_bytes)

        # if computed_hash != image_hash:
        #     print(image_bytes)
        #     print(computed_hash)
        #     return "Hashes don't match", 404 #in traffic bytes got shifted around

        #create image and save it
        image = Images(image_hash = computed_hash, user_id = user.id, last_accessed=datetime.now(timezone.utc))
        
        db.session.add(image)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return f"Unable to create image in database: {e}", 400

'''
this method checks whether an image hash matches the user id send

user has to parse user_token from metadata and include in request
TODO: verify the user_token
'''
@cross_origin
@app.route('/api/image/<hash>/<user_token>', methods=["GET", "PUT", "DELETE"])
def image_handler(image_hash, user_token):
    image = Images.get_by_hash(image_hash)
    if not image:
        return "Image not found", 404

    if request.method == "GET":
        image.last_accessed= lambda: datetime.now(timezone.utc)
        #verify user token
        user = Users.find_by_user_token(user_token)
        db.session.commit()

        if image.user_id !=- user.id:
            return "Image user doesn't match sent user", 401

        return image, 200
    elif request.method == "PUT": # this method might not be useful
        user_token = user_token
        user = Users.find_by_user_token(user_token)
        image.user_id = user.id
        db.session.commit()
        return "Successfully updated owner", 200
    elif request.method == "DELETE": # idk why someone would ever use this lol
        Images.delete(image.id)
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

    # try:

'''
this method overlays a depth map onto the sent image
parameters: image, 

-> this might not be needed user_token, signature, signed_hash,

user gets the image, user_token from metadata, signature from metadata, then hash the image and send the signature with the user token

TODO: write verification of hash
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