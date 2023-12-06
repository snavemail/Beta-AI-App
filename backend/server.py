from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO
import base64
import os
import utils as Util

app = Flask(__name__)

# difficulty_classifier_model = YOLO('backend/models/classify/classifyv1.pt')
hold_detection_model = YOLO('backend/models/detect/detectv1.pt')

# API endpoint for receiving images and returning predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.form:
            raise ValueError("Missing 'image' in form data", request.form)
        image_data = request.form.get('image')
        image_data = image_data.split(',')[1]
        image_data = base64.b64decode(image_data)

        with open(os.path.join('backend/react_images/detect', 'image.jpg'), 'wb') as f:
            f.write(image_data)

        img = Util.get_image(os.path.join('backend/react_images/detect', 'image.jpg'))
        results = hold_detection_model(img)
        results = Util.remove_edges(results)
        Util.disp_results(results, "detect")

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# @app.route('/predict-difficulty', methods=['POST'])
# def predict_difficulty():
#     try:
#         if 'image' not in request.form:
#             raise ValueError("Missing 'image' in form data", request.form)
#         image_data = request.form.get('image')
#         image_data = image_data.split(',')[1]
#         image_data = base64.b64decode(image_data)

#         with open(os.path.join('backend/react_images', 'image.jpg'), 'wb') as f:
#             f.write(image_data)

#         img = Util.get_image(os.path.join('backend/react_images/classify', 'image.jpg'))
#         results = difficulty_classifier_model.predict(img)
#         Util.disp_results(results, "classify")

#         return jsonify({"difficulty": Util.get_difficulty(results)})

#         # processed_image_path = os.path.join('react_images/classify', 'result.jpg')
#         # return send_file(processed_image_path, mimetype="image/jpeg")
        
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})

@app.route('/get-image', methods=['GET'])
def get_image():
    processed_image_path = os.path.join('react_images/detect', 'result.jpg')
    return send_file(processed_image_path, mimetype="image/jpeg")

@app.route('/')
def hello():
    return 'Hello, Flask is working!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
