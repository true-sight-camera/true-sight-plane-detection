
from sqlalchemy import text
from plane_detection.src.depth_map import create_depth_map_array
import tempfile
import cv2
import numpy as np
from PIL import Image
from plane_detection.src.encryption import hash_image_sha256
from flask_sqlalchemy import SQLAlchemy
from flask_cors import cross_origin
from flask import Blueprint, request, send_file
from plane_detection.main import db, app
from models import Users, Images

# app = Blueprint('app', __name__)

# from main import db, app

# print("in routes")

@cross_origin
@app.route('/health', methods=["GET"])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return "Good health", 200
    except Exception as e:
        return f"Unable to open database connection: {e}", 500

@cross_origin
@app.route('/api/image', methods=["POST"])
def create_image():
    try:
        image = request.files['image']
        # image_hash = request.form['image_hash']
        image_bytes = bytearray(image)

        signature = find_signature_metadata(image_bytes)

        signed_hash = request.form['signed_hash']

        #should be username
        user_token = request.form["token"]
        user = Users.find_by_username(user_token)
        pub_key = user.pub_key

        #compute h(m) from image
        #check that they match
        #hash
        computed_hash = hash_image_sha256(image_bytes)

        #unsign the signed_hash using verify_signature from encryption.py and pub key
        #load pub key from file -> make sure the camera stores the priv key
        pub_key = request.form['pub_key']

        verified_hash = verify_signature(pub_key, signed_hash)

        if computed_hash != image_hash:
            print(image_bytes)
            print(computed_hash)
            return "Hashes don't match", 404 #in traffic bytes got shifted around
        
    except Exception as e:
        db.session.rollback()
        return f"Unable to create image in database: {e}", 500

@cross_origin
@app.route('/api/image/<hash>', methods=["GET", "PUT", "DELETE"])
def image_handler(image_hash):
    image = Images.get_by_hash(image_hash)
    if not image:
        return "Image not found", 404

    if request.method == "GET":
        image.last_accessed= lambda: datetime.now(timezone.utc)
        db.session.commit()
        return image, 200
    elif request.method == "PUT":
        user_token = request.form['token']
        user = Users.find_by_username(user_token)
        image.user_id = user.id
        db.session.commit()
        return "Successfully updated owner", 200
    elif request.method == "DELETE":
        Images.delete(image.id)
        return "Successfully deleted image", 200
    else:
        return "Method not allowed", 401


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


@cross_origin()
@app.route("/api/depth-map", methods=["POST"])
def depth_map():
    #parse image from request
    if request.method != "POST":
        return
    print(request.files)
    # image = request.files['image']
    try:
        image = request.files['image']
    except Exception as e:
        return f"Unable to parse image file: {e}", 500

    try: 
        #get image hash

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