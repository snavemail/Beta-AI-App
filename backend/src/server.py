from flask import Flask, request, jsonify, send_file
import numpy as np
from ultralytics import YOLO
import base64, os, utils as Util, pathlib, platform, json
from classes.ImageAttribute import ImageAttribute
from classes.Hold import Hold

app = Flask(__name__)

difficulty_classifier_model = YOLO("backend/models/classify/classifyv3.pt")
hold_detection_model = YOLO("backend/models/detect/detectv1.pt")


# API endpoint for receiving images and returning possible holds
@app.route("/get-holds", methods=["POST"])
def get_holds():
    """
    Takes in an image and returns all of the holds from the image
    """
    try:
        if "image" not in request.form:
            raise ValueError("Missing 'image' in form data", request.form)
        image_data = request.form.get("image")
        image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)

        with open(os.path.join("backend/react_images/detect", "image.jpg"), "wb") as f:
            f.write(image_data)

        img = Util.get_image(os.path.join("backend/react_images/detect", "image.jpg"))
        results = hold_detection_model(img)
        results = Util.remove_edges(results)
        Util.disp_results(results, "detect")

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/predict-difficulty", methods=["POST"])
def predict_difficulty():
    """
    Takes in an image and returns the difficulty (1-10) of the hold
    """
    try:
        if "image" not in request.form:
            raise ValueError("Missing 'image' in form data", request.form)
        image_data = request.form.get("image")
        image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)

        with open(
            os.path.join("backend/react_images/classify", "image.jpg"), "wb"
        ) as f:
            f.write(image_data)

        img = Util.get_image(os.path.join("backend/react_images/classify", "image.jpg"))
        results = difficulty_classifier_model.predict(img)
        Util.disp_results(results=results, folder="classify")
        return jsonify({"difficulty": Util.get_difficulty(results)})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get-color-holds", methods=["POST"])
def get_color_holds():
    """
    Takes in an image and returns all of the holds from the image of a certain color
    """
    try:
        if "image" not in request.form:
            raise ValueError("Missing 'image' in form data", request.form)
        image_data = request.form.get("image")
        image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)
        hsvr_json = request.form.get("hsvr")
        hsvr_list = json.loads(hsvr_json)

        with open(
            os.path.join("backend/react_images/route-finder", "image.jpg"), "wb"
        ) as f:
            f.write(image_data)

        img_path = os.path.join("backend/react_images/route-finder", "image.jpg")
        print("working")
        holds = Util.get_holds_array(
            img_path, [hsvr_list[0], hsvr_list[1], hsvr_list[2]], hsvr_list[3]
        )

        # image_attribute = ImageAttribute(path=img_path)
        print("good")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get-image", methods=["GET"])
def get_image():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    processed_image_path = os.path.join(
        base_dir, "react_images", "classify", "result.jpg"
    )
    return send_file(processed_image_path, mimetype="image/jpeg")


@app.route("/get-color-image", methods=["GET"])
def get_color_image():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    processed_image_path = os.path.join(
        base_dir, "react_images", "route-finder", "result.jpg"
    )
    print("sending file")
    return send_file(processed_image_path, mimetype="image/jpeg")


@app.route("/")
def hello():
    return "Hello, Flask is working!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
