from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Boxes
from io import BytesIO
import base64
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = './react_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = YOLO('models/weights/best.pt')

def get_image_from_path(path):
    img = cv2.imread(path)
    return img

def disp_results(results):
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.save('results.jpg')  # save image

def remove_edges(results):
    for r in results:
        boxes_coords = np.array(r.boxes.xyxy)
        boxes_last = np.array(r.boxes.data[:, 4:])
        i = 0
        while i < len(boxes_coords):
            x1, y1, x2, y2 = boxes_coords[i]
            imh = r.boxes.orig_shape[0]
            imw = r.boxes.orig_shape[1]
            if (x1 < imw / 100.0) or (y1 < imh / 100) or (x2 > imw - imw / 100.0) or (y2 > imh - imh / 100.0):
                boxes_coords = np.delete(boxes_coords, i, 0)
                boxes_last = np.delete(boxes_last, i, 0)
                i -= 1
            i += 1
        new_data = np.concatenate((boxes_coords, boxes_last), axis=1)
        new_boxes = Boxes(new_data, r.boxes.orig_shape)
        r.boxes = new_boxes
    return results

@app.route('/test', methods=['POST'])
def test():
    try:
        if 'dummy_data' not in request.form:
            raise ValueError("Missing 'dummy_data' in form data")

        dummy_data = request.form['dummy_data']

        result = f"Received dummy data: {dummy_data}"

        return jsonify({"status": "success", "message": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# API endpoint for receiving images and returning predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            raise ValueError("Missing 'file' in form data", request.files)
        img_path = request.files['file']

        # img = cv2.imread(img_path)

        # img = get_image_from_path(path=img_path)
        # print("Predicting image")
        # results = model(img)
        # results = remove_edges(results)

        # results_img = disp_results(results)

        # # Encode the results image as a base64 string
        # results_img_buffer = BytesIO()
        # results_img.save(results_img_buffer, format='JPEG')
        # results_img_base64 = base64.b64encode(results_img_buffer.getvalue()).decode('utf-8')

        return jsonify({
            "status": "success",
            "message": "Prediction successful",
            # "results_image": results_img_base64,
            "img_path": f"{img_path}",
            # "img": img,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def hello():
    return 'Hello, Flask is working!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
