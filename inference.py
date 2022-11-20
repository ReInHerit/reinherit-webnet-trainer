import glob
import os
import sqlite3

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
from object_detection.utils import visualization_utils as vis_util
from six import BytesIO


def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: a file path (this can be local or on colossus)

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    img_data = tf.io.gfile.GFile(path, 'rb').read()
    image = Image.open(BytesIO(img_data))
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def run_inference_for_single_image(model, imagepath):
    image_np = load_image_into_numpy_array(imagepath)
    image = np.asarray(image_np)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.2,
                                           tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict, image_np


def annotate_directory(model, imagedir):
    for image_path in glob.glob(os.path.join(imagedir, '*.jpg')):
        output_dict, image_np = run_inference_for_single_image(model, image_path)
        coco_annotations = convert_tensor2list(output_dict, image_path)
        store_annotations(image_path, coco_annotations)
    return True

def annotate_image(model, image_path):
    output_dict, image_np = run_inference_for_single_image(model, image_path)
    coco_annotations = convert_tensor2list(output_dict, image_path)
    store_annotations(image_path, coco_annotations)
    return True


def run_inference(input_path, datasetName, modelName, first=True):
    pretrained_models_dir = "./models/pretrained_models/"
    label_map_path = "./static/new_label_map.pbtxt"
    print(f'Label map file: {label_map_path}')
    if first:
        print('Loading model...')
        tf.keras.backend.clear_session()
        model_dir = pretrained_models_dir + modelName + "/saved_model"
        if os.path.isdir(model_dir):
            print(model_dir)
        model = tf.saved_model.load(model_dir)
        #model = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/fpnlite_320x320/1")
        print('Model loaded.')
    else:
        print('Loading model...')
        tf.keras.backend.clear_session()
        model = tf.saved_model.load("./models/fine_tuned_models/exported_inference_graph/" + datasetName + "/saved_model")
        print('Model loaded.')

    if os.path.isdir(input_path):
        result = annotate_directory(model, input_path)
    else:
        result = annotate_image(model, input_path)
    return result



def convert_tensor2list(output, img_filename):
    annotations = []
    detection_classes = output['detection_classes'].tolist()
    for box_idx in range(len(detection_classes)):
        if output['detection_scores'][box_idx] > 0.5:
            box = output['detection_boxes'][box_idx]
            coco_box = box2coco(box, img_filename)
            box_class = detection_classes[box_idx]
            annotations.append((box_class, coco_box))
    return annotations


def box2coco(box, img_filename):
    coco_box = np.copy(box)
    image = Image.open(img_filename)
    width = image.width
    height = image.height

    coco_box[0], coco_box[1] = coco_box[1], coco_box[0]
    coco_box[2], coco_box[3] = coco_box[3], coco_box[2]
    coco_box[0] = coco_box[0] * width
    coco_box[1] = coco_box[1] * height
    coco_box[2] = coco_box[2] * width
    coco_box[2] = coco_box[2] - coco_box[0]
    coco_box[3] = coco_box[3] * height
    coco_box[3] = coco_box[3] - coco_box[1]

    box_list = coco_box.tolist()
    return box_list


def store_annotations(img_filename, annotations):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    imageId = cursor.execute("SELECT id FROM imagesData WHERE filename = ?", (img_filename,)).fetchall()[0][0]
    cursor.execute("DELETE FROM annotations WHERE image_id = ? AND automatic = ?", (imageId, 1))
    for i in range(len(annotations)):
        area = annotations[i][1][2] * annotations[i][1][3]
        cursor.execute("INSERT INTO annotations (image_id, category_id, area, x_min, y_min, width, height, automatic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (imageId, annotations[i][0], area, annotations[i][1][0], annotations[i][1][1], annotations[i][1][2], annotations[i][1][3], 1))

    connection.commit()
    connection.close()

