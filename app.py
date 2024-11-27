from flask import Flask, request, send_file
from flask_cors import CORS
from flask_cors import cross_origin
from depth_map import create_depth_map
import tempfile
import cv2


app = Flask(__name__)

CORS(app)

@cross_origin()
@app.route("/api/depth-map", methods=["POST"])
def depth_map():
    #parse image from request
    if request.method != "POST":
        return
    image = request.files['file']

    try:
        file_bytes = np.frombuffer(image.read(), np.uint8)
        cv2_image = cv2.decode(file_bytes, cv2.IMREAD_COLOR)
    except Exception as e:
        return f"Error Processing Image {e}", 500

    #make tempfile
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        filename = temp_file.name
        cv2.imwrite(filename, image)
        depth_map = create_depth_map(filename)
        cv2.imshow("depth map",depth_map)
        cv2.waitKey()
        cv2.destroyAllWindows()
        return send_file(filename, mimetype="image/png")





if __name__ == "__main__":
    app.run()