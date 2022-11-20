import cv2

BOX_COLOR = (0, 0, 255)  # BGR Red
TEXT_COLOR = (255, 255, 255)  # White


def yolo2bbox(bboxes):
    """
    Function to convert bounding boxes in YOLO format to
    xmin, ymin, xmax, ymax.

    Parmaeters:
    :param bboxes: Normalized [x_center, y_center, width, height] list
    return: Normalized xmin, ymin, xmax, ymax
    """
    xmin, ymin = bboxes[0] - bboxes[2] / 2, bboxes[1] - bboxes[3] / 2
    xmax, ymax = bboxes[0] + bboxes[2] / 2, bboxes[1] + bboxes[3] / 2
    return xmin, ymin, xmax, ymax

def xyxy2coco(self, bbox):
    """Convert ``xyxy`` style bounding boxes to ``xywh`` style for COCO
    evaluation.

    Args:
        bbox (numpy.ndarray): The bounding boxes, shape (4, ), in
            ``xyxy`` order.

    Returns:
        list[float]: The converted bounding boxes, in ``xywh`` order.
    """

    _bbox = bbox.tolist()
    return [
        _bbox[0],
        _bbox[1],
        _bbox[2] - _bbox[0],
        _bbox[3] - _bbox[1],
    ]


def draw_boxes(bgr_image, bboxes, titles, format='coco', font_thickness = 2, font_scale = 0.35):
    """
    Function accepts an image and bboxes list and returns
    the image with bounding boxes drawn on it.
    Parameters
    :param bgr_image: Image, type NumPy array.
    :param bboxes: Bounding box in Python list format.
    :param format: One of 'coco', 'voc', 'yolo' depending on which final
        bounding noxes are formated.
    Return
    image: Image with bounding boxes drawn on it.
    box_areas: list containing the areas of bounding boxes.
    """
    bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_RGB2BGR)
    box_areas = []
    h, w, _ = bgr_image.shape  # to denormalize YOLO coordinates

    for box_num, (box, title) in enumerate(zip(bboxes, titles)):
        if format == 'coco':
            # coco has bboxes in xmin, ymin, width, height format
            # we need to add xmin and width to get xmax and...
            # ... ymin and height to get ymax
            xmin = int(box[0])
            ymin = int(box[1])
            xmax = int(box[0]) + int(box[2])
            ymax = int(box[1]) + int(box[3])
            width = int(box[2])
            height = int(box[3])
        if format == 'voc':
            xmin = int(box[0])
            ymin = int(box[1])
            xmax = int(box[2])
            ymax = int(box[3])
            width = xmax - xmin
            height = ymax - ymin
        if format == 'yolo':
            # need the image height and width to denormalize...
            # ... the bounding box coordinates
            x1, y1, x2, y2 = yolo2bbox(box)
            # denormalize the coordinates
            xmin = int(x1 * w)
            ymin = int(y1 * h)
            xmax = int(x2 * w)
            ymax = int(y2 * h)
            width = xmax - xmin
            height = ymax - ymin

        cv2.rectangle(
            bgr_image,
            (xmin, ymin), (xmax, ymax),
            color=BOX_COLOR,
            thickness=2
        )
        ((text_width, text_height), _) = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        cv2.putText(bgr_image, title, (xmin, ymin - int(0.3 * text_height)), cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    TEXT_COLOR, font_thickness, lineType=cv2.LINE_AA)

    return bgr_image
