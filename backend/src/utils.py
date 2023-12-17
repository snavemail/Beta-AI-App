from PIL import Image
from ultralytics.engine.results import Boxes
import cv2, math, os, numpy as np
from classes.Hold import Hold
from classes.Limb import Limb, LimbName
from classes.State import State
from copy import copy
from ultralytics import YOLO


detect_model = YOLO("../models/detect/detectv2.pt")
classify_model = YOLO("../runs/classify/classifyv3.pt")


# Gets the image at the specified path as a numpy array
def get_image(path):
    """
    Turns a path to an image into an numpy array
    """
    img = cv2.imread(path)
    return img


def run_model(model, path):
    """
    Runs specified model on path for image"""
    return model.predict(path)


# Displays the results of model(image)
def disp_results(results):
    """
    Displays the results in a file called results/results[index]
    results: results from model
    """
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image

        DIR = "../images/results"
        len_folder = len(
            [
                name
                for name in os.listdir(DIR)
                if os.path.isfile(os.path.join(DIR, name))
            ]
        )
        im.save(f"../images/results/results{len_folder}.jpg")  # save image


# Removes all bounding boxes in the results of model(image)
# that may be cut off by the sides
def remove_edges(results):
    """
    Removes boxes where the edges are outside of the image
    results: the results from the model
    """
    for r in results:
        boxes_coords = np.array(r.boxes.xyxy)
        boxes_last = np.array(r.boxes.data[:, 4:])
        i = 0
        while i < (len(boxes_coords)):
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
        newboxes = Boxes(new_data, r.boxes.orig_shape)
        r.boxes = newboxes
    return results


def remove_bad_holds(results):
    """
    Removes bolts, tags, and downclimbs from a route
    results: the results from the model
    """
    for r in results:
        boxes_data = np.array(r.boxes.data)
        new_data = np.array([])
        for i in range(len(boxes_data)):
            img = get_box_as_image(results, i)
            hold_results = run_model(classify_model, img)
            for hold_result in hold_results:
                guesses = hold_result.probs.data
                if (
                    not guesses[0] == max(guesses)
                    and not guesses[1] == max(guesses)
                    and not guesses[9] == max(guesses)
                ):
                    if len(new_data) == 0:
                        new_data = np.array([boxes_data[i]])
                    else:
                        new_data = np.append(new_data, [boxes_data[i]], axis=0)
        newboxes = Boxes(new_data, r.boxes.orig_shape)
        r.boxes = newboxes
    return results


def get_box_as_image(results, index):
    r = results[0]
    x1, y1, x2, y2 = np.array(r.boxes.xyxy)[index]
    im_array = np.array(r.orig_img)
    cropped = im_array[round(y1) : round(y2), round(x1) : round(x2)]
    return cropped


def individual_holds(model, img_path, hold_path):
    try:
        os.rmdir(hold_path)
    except:
        pass
    os.mkdir(hold_path)
    for img_name in os.listdir(img_path):
        img = get_image(f"{img_path}/{img_name}")
        results = model(img)
        results = remove_edges(results)
        r = results[0]
        for i in range(len(r.boxes)):
            im_array = get_box_as_image(results, i)
            im = Image.fromarray(im_array)
            im.save(f"{hold_path}/{str(i) + '-'}{img_name}")


def color_difference(color1, color2):
    c1hsv = cv2.cvtColor(color1, cv2.COLOR_RGB2HSV)
    c2hsv = cv2.cvtColor(color2, cv2.COLOR_RGB2HSV)
    return abs(c1hsv[0] - c2hsv[0])


def get_dom_color(img):
    # Use K-means clustering to find the 2 dominant colors
    # https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv

    average = img.mean(axis=0).mean(axis=0)
    pixels = np.float32(img.reshape(-1, 3))
    n_colors = 2
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    hsv_palette = []
    for i in range(len(palette)):
        hsv_palette.append(
            cv2.cvtColor(np.array([[palette[i]]]), cv2.COLOR_BGR2HSV)[0][0]
        )
        hsv_palette[i] = np.array(
            [
                hsv_palette[i][0],
                hsv_palette[i][1] * 100,
                hsv_palette[i][2] * 100 / 255.0,
            ]
        )
    # compares the saturations of the two colors (to filter for the wall)
    sats = np.array([col[1] for col in hsv_palette])
    return hsv_palette[np.argmax(sats)]


def close_enough(color2, color1, close):
    if color1[1] == 0:
        if color2[1] < 20:
            if color2[2] < 50 and color1[2] < 50:
                return True
            elif color2[2] > 50 and color1[2] > 50:
                return True
            else:
                return False
        return False
    else:
        if color2[1] >= color1[1] and color2[2] >= color1[2]:
            diff = abs(color1[0] - color2[0])
            colcheck = min(diff, 360 - diff) < close
            return colcheck
    return False


def get_holds_near_color(results, color, close):
    for r in results:
        boxes_data = np.array(r.boxes.data)
        new_data = np.array([])
        for i in range(len(boxes_data)):
            img = get_box_as_image(results, i)
            dom = get_dom_color(img)
            if close_enough(dom, color, close):
                if len(new_data) == 0:
                    new_data = np.array([boxes_data[i]])
                else:
                    new_data = np.append(new_data, [boxes_data[i]], axis=0)
        newboxes = Boxes(new_data, r.boxes.orig_shape)
        r.boxes = newboxes
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


def state_difficulty(state: State):
    """
    Finds the difficulty of a certain state
    state: the state that is being evaluated for difficulty
    """
    if state.lh.hold != None and state.rh.hold != None:
        average_hands_x = (state.lh.hold.x + state.rh.hold.x) / 2
        average_hands_y = (state.lh.hold.y + state.rh.hold.y) / 2
    else:
        if state.rh.hold == None:
            average_hands_x = state.lh.hold.x
            average_hands_y = state.lh.hold.y
        else:
            average_hands_y = state.rh.hold.y
            average_hands_x = state.rh.hold.x
    if state.lf.hold != None and state.rf.hold != None:
        average_legs_x = (state.lf.hold.x + state.rf.hold.x) / 2
        average_legs_y = (state.lf.hold.y + state.rf.hold.y) / 2
    else:
        if state.rf.hold == None:
            average_legs_x = state.lf.hold.x
            average_legs_y = state.lf.hold.y
        else:
            average_legs_y = state.rf.hold.y
            average_legs_x = state.rf.hold.x

    hands_difference_x = (
        abs(state.rh.hold.x - state.lh.hold.x)
        if state.lh.hold != None and state.rh.hold != None
        else 0
    )
    hands_difference_y = (
        abs(state.rh.hold.y - state.lh.hold.y)
        if state.lh.hold != None and state.rh.hold != None
        else 0
    )

    legs_difference_x = (
        abs(state.rf.hold.x - state.lf.hold.x)
        if state.lf.hold != None and state.rf.hold != None
        else 0
    )
    legs_difference_y = (
        abs(state.lf.hold.y - state.rf.hold.y)
        if state.lf.hold != None and state.rf.hold != None
        else 0
    )
    hands_difference_raw_x = (
        state.rh.hold.x - state.lh.hold.x
        if state.lh.hold != None and state.rh.hold != None
        else 0
    )
    legs_difference_raw_x = (
        state.rf.hold.x - state.lf.hold.x
        if state.lf.hold != None and state.rf.hold != None
        else 0
    )

    leg_match_diff = 0
    if (
        state.lf.hold != None
        and state.rf.hold != None
        and state.lf.hold.x - state.rf.hold.x == 0
    ):
        leg_match_diff = 25

    cross_diff = 0
    if hands_difference_raw_x < 0:
        cross_diff += 2 * abs(hands_difference_raw_x / 88)
    if legs_difference_raw_x < 0:
        cross_diff += 100
    if hands_difference_raw_x < 0 and legs_difference_raw_x < 0:
        cross_diff *= 3

    diff = 0
    center_diff = abs(average_hands_x - average_legs_x) ** 2

    target_distance = state.inches_to_pixels(state.person.height * 0.95)
    distance_diff = target_distance - abs(average_legs_y - average_hands_y)
    scrunched_up_diff = distance_diff**2

    limb_strength_diff = 0
    angle_diff = 0

    # Check each limb and find the strength ratio for the holds
    for limb in [state.lh, state.rh, state.lf, state.rf]:
        if limb.hold != None:
            limb_strength_diff += limb.hold.diff / limb.strength
            if limb.name == LimbName.LEFT_HAND:
                if 315 >= limb.hold.angle >= 270:
                    angle_diff += 2
                elif 90 >= limb.hold.angle or limb.hold.angle > 315:
                    angle_diff += 1
                elif 180 >= limb.hold.angle > 90:
                    angle_diff += 2.5
                else:
                    angle_diff += 3
            if limb.name == LimbName.RIGHT_HAND:
                if 90 >= limb.hold.angle >= 45:
                    angle_diff += 2
                elif 45 >= limb.hold.angle or limb.hold.angle > 270:
                    angle_diff += 1
                elif 270 >= limb.hold.angle > 180:
                    angle_diff += 2.5
                else:
                    angle_diff += 3
            if limb.name in [LimbName.LEFT_LEG, LimbName.RIGHT_LEG]:
                if 90 <= limb.hold.angle <= 270:
                    angle_diff += 2
        else:
            limb_strength_diff += 6
    separation_diff = 0
    separation_diff += 0.1 * hands_difference_y
    separation_diff += 0.1 * legs_difference_y

    # If separated too far, make it harder
    if hands_difference_x > state.inches_to_pixels(0.8 * state.person.wingspan):
        separation_diff += 0.5 * hands_difference_x
    separation_diff += 0.5 * legs_difference_y
    if legs_difference_x > state.inches_to_pixels(0.6 * state.person.wingspan):
        separation_diff += 0.5 * legs_difference_x

    # Weight all of the different difficulties to balance them out
    center_diff *= 0.04
    scrunched_up_diff *= 0.05
    angle_diff *= 1
    limb_strength_diff *= 30
    separation_diff *= 0.5
    cross_diff *= 1
    leg_match_diff *= 20
    diff += (
        center_diff
        + scrunched_up_diff
        + angle_diff
        + limb_strength_diff
        + separation_diff
        + leg_match_diff
        + cross_diff
    )
    return diff


def move_difficulty(state: State, limb: Limb, next_hold: Hold):
    """
    Evaluates the difficulty of a move
    state: the state that is being evaluated
    """
    distance = math.sqrt(
        ((limb.hold.x - next_hold.x) ** 2) + ((limb.hold.y - next_hold.y) ** 2)
    )
    distance_diff = distance

    new_state = State(
        copy(state.lf),
        copy(state.rf),
        copy(state.lh),
        copy(state.rh),
        state.person,
        state.route,
        state.wall_height_pixels,
    )
    new_state_limbs = [new_state.lh, new_state.rh, new_state.lf, new_state.rf]
    for new_state_limb in new_state_limbs:
        if new_state_limb.name == limb.name:
            new_state_limb.hold = None
    state_without_limb_difficulty = 0.3 * state_difficulty(new_state)
    distance_diff *= 0.1
    move_diff = distance_diff + state_without_limb_difficulty
    return move_diff


def move_to_text(action, route):
    output = "- Move your "
    if action[0].name == LimbName.LEFT_LEG:
        output += "left leg "
    elif action[0].name == LimbName.LEFT_HAND:
        output += "left hand "
    elif action[0].name == LimbName.RIGHT_LEG:
        output += "right leg "
    elif action[0].name == LimbName.RIGHT_HAND:
        output += "right hand "
    output += "to hold number "
    output += str(route.holds.index(action[1]))
    output += " from the top"
    return output


def get_hold_data(holds: Hold):
    len_hold = len(holds)
    hold_data = [(i, hold.x, hold.y, hold.diff) for i, hold in enumerate(holds)]
    return (len_hold, hold_data)


def get_results(results):
    for r in results:
        guesses = r.probs.data
        if guesses[0] == max(guesses):
            return "bolt"
        if guesses[1] == max(guesses):
            return "downclimb"
        if guesses[9] == max(guesses):
            print(guesses[9])
            return "tag"
        aggregate = (
            10 * guesses[2]
            + 5 * guesses[3]
            + 4 * guesses[4]
            + 11 * guesses[5]
            + 1 * guesses[6]
            + 7 * guesses[7]
            + 6 * guesses[8]
            + 12 * guesses[10]
            + 3 * guesses[11]
            + 2 * guesses[12]
        )
        return min(float(aggregate), 10)


def get_confidence(results):
    for r in results:
        guesses = r.probs.data
        squares = 0
        for guess in guesses:
            squares += guess**2

    return float(squares)


def rotate_image(mat, angle):
    height, width = mat.shape[:2]  # image shape has 3 dimensions
    image_center = (
        width / 2,
        height / 2,
    )  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def get_ideal_rotation(image):
    best = (0, 0)
    for i in range(7):
        rot = rotate_image(image, (i * 45))
        res = run_model(classify_model, rot)
        print("running")
        conf = get_confidence(res)
        if i == 0:
            diff = get_results(res)
            if diff in ["bolt", "downclimb", "tag"]:
                print(f"************************{diff}************************")
                return (0, diff)
        if (i == 0 and conf > best[1]) or (conf > best[1] + 0.3):
            best = ((360 - i * 45) % 360, conf)
    return (best[0], diff)


def get_holds_array(path, color, close):
    results = run_model(path)
    results = remove_edges(results)
    results = get_holds_near_color(results, color, close)
    results = remove_bad_holds(results)
    disp_results(results)
    for r in results:
        holds = []
        boxes_data = np.array(r.boxes.xywh)
        for i in range(len(boxes_data)):
            hold = get_box_as_image(results, i)
            angle, diff = get_ideal_rotation(hold)
            if diff != "tag" and diff != "bolt" and diff != "downclimb":
                holds.append(
                    Hold(
                        x=boxes_data[i][0],
                        y=boxes_data[i][1],
                        width=boxes_data[i][2],
                        height=boxes_data[i][3],
                        diff=float(diff),
                        angle=int(angle),
                    )
                )
            else:
                print(f"FOUND {diff} at {boxes_data[i][0]}, {boxes_data[i][1]}")
    return holds
