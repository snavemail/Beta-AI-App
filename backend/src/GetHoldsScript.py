from utils import (
    predict_holds,
    get_box_as_image,
    get_holds_near_color,
    disp_results,
    remove_edges,
    remove_bad_holds,
    get_ideal_rotation,
)
from classes.Hold import Hold
import numpy as np, sys


def get_holds_array(path, color, close):
    results = predict_holds(path)
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


def main(argv):
    print(
        get_holds_array(
            argv[0], np.array([int(argv[1]), int(argv[2]), int(argv[3])]), int(argv[4])
        )
    )
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
