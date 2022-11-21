import os
import argparse
import shutil
import sqlite3
from PIL import Image

from label_map_utils import get_labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tensorflow_path', type=str, help='Absolute path to tensorflow directory')
    args = parser.parse_args()

    path_to_tensorflow = args.tensorflow_path
    with open("static/tensorflow_path.txt", "w") as file:
        file.write(path_to_tensorflow)

    with open("static/tensorflow_path.txt", "r") as file:
        print(file.readline())

    path_to_labels = "./static/label_map.pbtxt"

    folder = 'static/upload_images'
    if os.path.isdir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    folder = 'webnet_splitted_dataset'
    if os.path.isdir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    folder = 'webnet_augmented_dataset'
    if os.path.isdir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    folder = 'webnet_tf_dataset'
    if os.path.isdir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    connection = sqlite3.connect('database.db')

    with open('schema.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    sql = ("INSERT INTO datasets (name) VALUES (?)")
    datasetName = [('exampleImages'), ]
    cur.execute(sql, datasetName)

    imagesDirectory = "static/images"
    annotations_file = os.path.join(imagesDirectory, "annotations.json")
    if os.path.isfile(annotations_file):
        os.unlink(annotations_file)
    for img in os.listdir(imagesDirectory):
        path = os.path.join(imagesDirectory, img)
        image = Image.open(path)
        width = image.width
        height = image.height
        cur.execute("INSERT INTO imagesData (dataset_id, filename, width, height) VALUES (?, ?, ?, ?)",
                    (1, path, width, height))

    sql3 = "INSERT INTO categories VALUES (?, ?)"
    categories = get_labels(path_to_labels)
    cur.executemany(sql3, categories)

    sql4 = "INSERT INTO models (display_name, name) VALUES(?, ?)"
    models = [
        ("SSD MobileNet V2", "ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8"),
        ("SSD ResNet50 V1", "ssd_resnet50_v1_fpn_640x640_coco17_tpu-8"),
        ("EfficientDet D0", "efficientdet_d0_coco17_tpu-32"),
        ("CenterNet ResNet50 V1", "centernet_resnet50_v1_fpn_512x512_coco17_tpu-8"),
        ("Faster R-CNN ResNet50 V1", "faster_rcnn_resnet50_v1_640x640_coco17_tpu-8")
    ]

    cur.executemany(sql4, models)

    connection.commit()

    print(cur.execute("SELECT * FROM categories").fetchall())

    connection.close()

if __name__ == "__main__":
    main()
