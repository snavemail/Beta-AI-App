from PIL import Image
import numpy as np
from ultralytics.engine.results import Boxes
import cv2
import os


def get_image(path):
    img = cv2.imread(path)
    return img


def disp_results(results, folder):
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.save(
            os.path.join(f"backend/react_images/{folder}", "result.jpg")
        )  # save image


def remove_edges(results):
    for r in results:
        boxes_coords = np.array(r.boxes.xyxy)
        boxes_last = np.array(r.boxes.data[:, 4:])
        i = 0
        while i < len(boxes_coords):
            x1, y1, x2, y2 = boxes_coords[i]
            imh = r.boxes.orig_shape[0]
            imw = r.boxes.orig_shape[1]
            if (
                (x1 < imw / 100.0)
                or (y1 < imh / 100)
                or (x2 > imw - imw / 100.0)
                or (y2 > imh - imh / 100.0)
            ):
                boxes_coords = np.delete(boxes_coords, i, 0)
                boxes_last = np.delete(boxes_last, i, 0)
                i -= 1
            i += 1
        new_data = np.concatenate((boxes_coords, boxes_last), axis=1)
        new_boxes = Boxes(new_data, r.boxes.orig_shape)
        r.boxes = new_boxes
    return results


# Displays the results of model(image)
def get_difficulty(results):
    for r in results:
        guesses = r.probs.data
        if guesses[0] == max(guesses):
            return "bolt"
        if guesses[1] == max(guesses):
            return "downclimb"
        if guesses[9] == max(guesses):
            return "tag"
        aggregate = (
            8 * guesses[2]
            + 5 * guesses[3]
            + 4 * guesses[4]
            + 9 * guesses[5]
            + 1 * guesses[6]
            + 7 * guesses[7]
            + 6 * guesses[8]
            + 10 * guesses[10]
            + 3 * guesses[11]
            + 2 * guesses[12]
        ) / (
            guesses[2]
            + guesses[3]
            + guesses[4]
            + guesses[5]
            + guesses[6]
            + guesses[7]
            + guesses[8]
            + guesses[10]
            + guesses[11]
            + guesses[12]
        )
        return float(aggregate)
