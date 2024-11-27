from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from depth_map import create_depth_map_array
import tempfile
import cv2
import numpy as np
from PIL import Image


app = Flask(__name__)
app.debug=True

CORS(app)

@cross_origin()
@app.route("/api/depth-map", methods=["POST"])
def depth_map():
    #parse image from request
    if request.method != "POST":
        return
    image = request.files['file']

    try: 
        #make tempfile for received image
        temp_file = tempfile.NamedTemporaryFile(suffix=".png")
        filename = temp_file.name
        image.save(filename)

        # create depth map and image arrays for overlay
        depth_map_array = create_depth_map_array(filename)
        image_array = cv2.imread(filename)

        # overlay depth map at 50% capacity
        overlay_image = cv2.addWeighted(depth_map_array, 0.5, image_array, 0.5, gamma=0)

        #save the overlay image temporarily
        overlay_file = tempfile.NamedTemporaryFile(suffix=".png")
        overlay_filename = overlay_file.name
        overlay_image = Image.fromarray(overlay_image)
        overlay_image.save(overlay_filename)

        #return 
        return send_file(overlay_filename, mimetype="image/png")
    except Exception as e:
        return f"Unable to overlay depth map {e}", 500

if __name__ == "__main__":
    app.run()