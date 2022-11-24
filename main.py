import shutil

from flask import Flask, render_template, url_for, request, jsonify, session, flash
import sqlite3
import os
from PIL import Image
import subprocess

from label_map_utils import buildLabelMap
from create_annotations import saveCocoBoxes
from inference import run_inference

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def getAllDatasets():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    results = cur.execute("SELECT DISTINCT name FROM datasets").fetchall()
    conn.close()
    return results


def getAllCategories():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    results = cur.execute("SELECT DISTINCT name FROM categories").fetchall()
    conn.close()
    return results


def addCategory(categoryName):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    newId = cur.execute("SELECT MAX(id) FROM categories").fetchall()[0][0] + 1
    cur.execute("INSERT INTO categories (id, name) VALUES (?, ?)", (newId, categoryName))
    conn.commit()
    conn.close()


def storeCategories(data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS selectedCategories")
    cursor.execute("CREATE TABLE selectedCategories (id INTEGER PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL)")
    for i in range(len(data)):
        categoryId = cursor.execute("SELECT id FROM categories WHERE name = ?", (data[i],)).fetchall()[0][0]
        cursor.execute("INSERT INTO selectedCategories (id, name) VALUES (?, ?)", (categoryId, data[i]))
    print(cursor.execute("SELECT * FROM selectedCategories").fetchall())
    connection.commit()
    connection.close()


def getSelectedCategories():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    results = cur.execute("SELECT DISTINCT name FROM selectedCategories").fetchall()
    conn.close()
    return results


def getDatasetSize(datasetName):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    datasetId = cur.execute("SELECT id FROM datasets WHERE name = ?", (datasetName,)).fetchall()[0][0]
    size = cur.execute("SELECT COUNT(*) FROM imagesData WHERE dataset_id = ?", (datasetId,)).fetchall()[0][0]
    conn.close()
    return size


def get_images(data):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    datasetId = cur.execute("SELECT id FROM datasets WHERE name = ?", (data[0]["dataset_name"],)).fetchall()[0][0]
    limit = 9
    offset = (data[1]["page"] - 1) * 9
    data = cur.execute(
        "SELECT id, filename, title, author, description FROM imagesData WHERE dataset_id = ? LIMIT ? OFFSET ?",
        (datasetId, limit, offset)).fetchall()
    conn.close()
    return data


def addDataset(datasetName):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO datasets (name) VALUES (?)", (datasetName,))
    connection.commit()
    connection.close()


def getLastDataset():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    result = cursor.execute("SELECT MAX(id) FROM datasets").fetchall()[0][0]
    connection.close()
    return result


def storeImage(filename, width, height, datasetId):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO imagesData (dataset_id, filename, width, height) VALUES (?, ?, ?, ?)",
                   (datasetId, filename, width, height))
    connection.commit()
    connection.close()


def storeImageData(data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE imagesData SET title=?, author = ?, description = ? WHERE filename = ?",
                   (data[1]["title"], data[2]["author"], data[3]["description"], data[0]["filename"]))
    connection.commit()
    connection.close()


def storeMiniatureData(data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE imagesData SET title = ?, author = ? WHERE filename = ?',
                   (data[1]["title"], data[2]["author"], data[0]["image_name"]))
    connection.commit()
    connection.close()


def storeImageAnnotations(data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    imageId = cursor.execute("SELECT id FROM imagesData WHERE filename = ?", (data[0][0]['image_name'],)).fetchall()[0][
        0]
    cursor.execute("DELETE FROM annotations WHERE image_id = ?", (imageId,))

    sql_insert = "INSERT INTO annotations (image_id, category_id, area, x_min, y_min, width, height, automatic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    for i in range(len(data)):
        categoryId = \
            cursor.execute("SELECT id FROM categories WHERE name = ?", (data[i][1]['category'],)).fetchall()[0][0]
        print(imageId, categoryId)
        values = (
            imageId, categoryId, data[i][2]['area'], data[i][3]['x_min'], data[i][4]['y_min'], data[i][5]['width'],
            data[i][6]['height'], data[i][7]['automatic'])
        cursor.execute(sql_insert, values)

    connection.commit()
    connection.close()


def get_image_data(filename):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    result = cursor.execute("SELECT id, filename, title, author, description FROM imagesData WHERE filename = ?",
                            (filename,)).fetchall()
    connection.close()
    print(result)
    return result


def get_image_annotations(filename):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    imageId = cursor.execute("SELECT id FROM imagesData WHERE filename = ?", (filename,)).fetchall()[0][0]
    annotations = cursor.execute("SELECT * FROM annotations WHERE image_id = ?", (imageId,)).fetchall()
    result = []
    for i in range(len(annotations)):
        result.append(list(annotations[i]))
    for i in range(len(result)):
        categoryName = cursor.execute("SELECT name FROM categories WHERE id = ?", (result[i][2],)).fetchall()[0][0]
        result[i][2] = categoryName
    connection.close()
    return result


def removeImageAnnotations(filename):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    imageId = cursor.execute("SELECT id FROM imagesData WHERE filename = ?", (filename,)).fetchall()[0][0]
    cursor.execute("DELETE FROM annotations WHERE image_id = ?", (imageId,))
    connection.commit()
    connection.close()


def createLabelMap():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    categories = cursor.execute("SELECT * FROM categories").fetchall()
    buildLabelMap(categories)
    connection.close()


def saveCocoAnnotations(datasetName):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    datasetId = cursor.execute("SELECT id FROM datasets WHERE name = ?", (datasetName,)).fetchall()[0][0]

    images = cursor.execute("SELECT id, filename, width, height FROM imagesData WHERE dataset_id = ?",
                            (datasetId,)).fetchall()
    imagesIds = []
    for i in range(len(images)):
        imagesIds.append(images[i][0])

    anns = cursor.execute("SELECT * FROM annotations").fetchall()
    annotations = []
    for i in range(len(anns)):
        if anns[i][1] in imagesIds:
            annotations.append(anns[i])

    categories = cursor.execute("SELECT * FROM selectedCategories").fetchall()
    connection.close()
    if datasetName == "exampleImages":
        output_dir = "static/images/"
    else:
        output_dir = "static/upload_images/" + datasetName + "/"
    saveCocoBoxes(categories, images, annotations, output_dir)


def getAllModels():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    models = cursor.execute("SELECT display_name FROM models").fetchall()
    print(models)
    connection.close()
    return models


def augmentImages(datasetName):
    if datasetName == "exampleImages":
        json_path = "static/images/annotations.json"
    else:
        json_path = "static/upload_images/" + datasetName + "/annotations.json"

    augmented_dir = "./webnet_augmented_dataset/" + datasetName
    if os.path.isdir(augmented_dir):
        for filename in os.listdir(augmented_dir):
            file_path = os.path.join(augmented_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    subprocess.call(["python", "augment_annotated_boxes.py", json_path, augmented_dir, "-n", "10"])


def splitDataset(datasetName):
    augmented_dir = "./webnet_augmented_dataset/" + datasetName

    splitted_dir = "./webnet_splitted_dataset/" + datasetName

    if os.path.isdir(splitted_dir):
        for filename in os.listdir(splitted_dir):
            file_path = os.path.join(splitted_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    subprocess.call(["python", "partition_dataset.py", "-i", augmented_dir, "-o", splitted_dir, "-j"])


def convertAnnotationFormat(datasetName):
    path_to_labels = "./static/new_label_map.pbtxt"
    splitted_dir = "./webnet_splitted_dataset/" + datasetName
    train_dir = splitted_dir + "/train"
    test_dir = splitted_dir + "/test"
    train_tf_dir = "./webnet_tf_dataset/" + datasetName + "/train"
    test_tf_dir = "./webnet_tf_dataset/" + datasetName + "/test"
    if not os.path.exists(train_tf_dir):
        os.makedirs(train_tf_dir)
    if not os.path.exists(test_tf_dir):
        os.makedirs(test_tf_dir)
    train_csv_path = train_tf_dir + "/train.csv"
    test_csv_path = test_tf_dir + "/test.csv"
    train_record_path = train_tf_dir + "/train.tfrecord"
    test_record_path = test_tf_dir + "/test.tfrecord"

    subprocess.call(
        ["python", "convert_cocojson2tfrecord.py", "-j", train_dir, "-l", path_to_labels, "-c", train_csv_path, "-o",
         train_record_path])
    subprocess.call(
        ["python", "convert_cocojson2tfrecord.py", "-j", test_dir, "-l", path_to_labels, "-c", test_csv_path, "-o",
         test_record_path])


def startTraining(datasetName, selectedModel):
    with open("static/tensorflow_path.txt", "r") as f:
        path_to_tensorflow = f.readline()

    path_to_labels = "./static/new_label_map.pbtxt"
    train_record_path = "./webnet_tf_dataset/" + datasetName + "/train" + "/train.tfrecord"
    test_record_path = "./webnet_tf_dataset/" + datasetName + "/test" + "/test.tfrecord"

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    modelName = cursor.execute("SELECT name FROM models WHERE display_name = ?", (selectedModel,)).fetchall()[0][0]
    connection.close()

    subprocess.call(
        ["python", "configure_detector_training.py", "--model_name", modelName, "--dataset_name", datasetName,
         "--download_model", "-l", path_to_labels, "--train_record", train_record_path, "--test_record", test_record_path])

    logdir = "./models/fine_tuned_models/training/" + datasetName + "/" + modelName
    subprocess.Popen(["tensorboard", "--logdir", logdir, "--host", "0.0.0.0", "--port", "6006"], shell=True)

    pipeline_config_path = "models/fine_tuned_models/training/" + datasetName + "/" + modelName + "/pipeline.config"
    model_dir = "models/fine_tuned_models/training/" + datasetName + "/" + modelName
    model_main_path = path_to_tensorflow + "/models/research/object_detection/model_main_tf2.py"
    subprocess.call(
        ["python", model_main_path, "--pipeline_config_path", pipeline_config_path, "--model_dir",
         model_dir, "--alsologtostderr", "--num_train_steps", "30000", "--sample_1_of_n_eval_examples", "1"])

    training_checkpoint_dir = "models/fine_tuned_models/training/" + datasetName + "/" + modelName
    output_dir = "models/fine_tuned_models/exported_inference_graph/" + modelName
    exporter_main_path = path_to_tensorflow + "/models/research/object_detection/exporter_main_v2.py"
    subprocess.call(
        ["python", exporter_main_path, "--trained_checkpoint_dir", training_checkpoint_dir,
         "--pipeline_config_path", pipeline_config_path, "--output_directory", output_dir])


def annotateImages(datasetName, selectedModel):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    modelName = cursor.execute("SELECT name FROM models WHERE display_name = ?", (selectedModel,)).fetchall()[0][0]
    connection.close()

    if datasetName == "exampleImages":
        imagesDirectory = "static/images"
    else:
        imagesDirectory = "static/upload_images/" + datasetName

    if os.path.isdir("models/fine_tuned_models/exported_inference_graph/" + modelName):
        run_inference(imagesDirectory, datasetName, modelName, first=False)
    else:
        run_inference(imagesDirectory, datasetName, modelName)


def annotateSingleImage(file_path, selectedModel):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    modelName = cursor.execute("SELECT name FROM models WHERE display_name = ?", (selectedModel,)).fetchall()[0][0]
    datasetId = cursor.execute("SELECT dataset_id FROM imagesData WHERE filename = ?", (file_path,)).fetchall()[0][0]
    datasetName = cursor.execute("SELECT name FROM datasets WHERE id = ?", (datasetId,)).fetchall()[0][0]
    connection.close()

    if os.path.isdir("models/fine_tuned_models/exported_inference_graph/" + modelName):
        run_inference(file_path, datasetName, modelName, first=False)
    else:
        run_inference(file_path, datasetName, modelName)


PATH_TO_NEW_DATASET = "static/images/"


@app.route('/')
def index():
    conn = get_db_connection()
    conn.close()
    return render_template('index.html')


@app.route('/load-labels', methods=['POST'])
def load_labels():
    if request.method == "POST":
        results = getAllCategories()
    return jsonify(results)


@app.route('/add-label', methods=['POST'])
def add_label():
    if request.method == "POST":
        data = request.get_json()
        addCategory(data)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/set-categories', methods=['POST'])
def set_categories():
    if request.method == "POST":
        data = request.get_json()
        storeCategories(data)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/load-selected-labels', methods=['POST'])
def load_selected_labels():
    if request.method == 'POST':
        results = getSelectedCategories()
    return jsonify(results)


@app.route('/load-all-datasets', methods=['POST'])
def load_all_datasets():
    if request.method == "POST":
        results = getAllDatasets()
    return jsonify(results)


@app.route('/load-dataset', methods=['POST'])
def load_dataset():
    if request.method == "POST":
        data = request.get_json()
        result = getDatasetSize(data)
        print(result)
    return jsonify(result)


@app.route('/load-images-page', methods=['POST'])
def load_images():
    if request.method == "POST":
        data = request.get_json()
        results = get_images(data)
    return jsonify(results)


@app.route('/create-dataset', methods=['POST'])
def createDataset():
    if request.method == "POST":
        datasetName = request.get_json()
        addDataset(datasetName)
        global PATH_TO_NEW_DATASET
        PATH_TO_NEW_DATASET = "static/upload_images/" + datasetName
        os.mkdir(PATH_TO_NEW_DATASET)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/save-images', methods=['POST'])
def saveImages():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files[]')
    for file in files:
        path = os.path.join(PATH_TO_NEW_DATASET, file.filename)
        file.save(path)
        img = Image.open(path)
        width = img.width
        print(width)
        height = img.height
        print(height)
        storeImage(path, width, height, getLastDataset())

    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/load-image-data', methods=['POST'])
def load_image_data():
    if request.method == "POST":
        filename = request.get_json()
        results = get_image_data(filename)
    return jsonify(results)


@app.route('/load-image-annotations', methods=['POST'])
def load_image_annotations():
    if request.method == "POST":
        filename = request.get_json()
        results = get_image_annotations(filename)
    return jsonify(results)


@app.route('/process-data', methods=['POST'])
def get_data():
    if request.method == "POST":
        data = request.get_json()
        storeImageData(data)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/save-miniature-data', methods=['POST'])
def save_miniature_data():
    if request.method == "POST":
        data = request.get_json()
        storeMiniatureData(data)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/process-annotations', methods=['POST'])
def save_image_annotations():
    if request.method == "POST":
        data = request.get_json()
        storeImageAnnotations(data)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/reset-image-annotations', methods=['POST'])
def reset_image_annotations():
    if request.method == "POST":
        filename = request.get_json()
        removeImageAnnotations(filename)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/load-models', methods=['POST'])
def load_models():
    if request.method == "POST":
        models = getAllModels()
    return jsonify(models)


@app.route('/inference', methods=['POST'])
def annotate_images():
    if request.method == 'POST':
        data = request.get_json()
        annotateImages(data[0]['dataset_name'], data[1]['model'])
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/inference-single-image', methods=['POST'])
def annotate_image():
    if request.method == 'POST':
        data = request.get_json()
        annotateSingleImage(data[0]['filename'], data[1]['model'])
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/save-annotations', methods=['POST'])
def save_coco_annotations():
    if request.method == 'POST':
        datasetName = request.get_json()
        createLabelMap()
        saveCocoAnnotations(datasetName)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/augment-images', methods=['POST'])
def augment_images():
    if request.method == 'POST':
        datasetName = request.get_json()
        augmentImages(datasetName)
        splitDataset(datasetName)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/convert-annotations', methods=['POST'])
def convert_annotations():
    if request.method == 'POST':
        datasetName = request.get_json()
        convertAnnotationFormat(datasetName)
    results = {'processed': 'true'}
    return jsonify(results)


@app.route('/train', methods=['POST'])
def train():
    if request.method == 'POST':
        data = request.get_json()
        startTraining(data[0]["dataset_name"], data[1]["model"])
    results = {'processed': 'true'}
    return jsonify(results)


if __name__ == "__main__":
    app.run()
