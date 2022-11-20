# WebNet Trainer

WebNet Trainer is a web annotation tool for object detection.
It allows to annotate images with bounding boxes and train a neural network asynchronously using Tensorflow models.

Purposes:
- Train a neural network for object recognition in works of art
- Automate or speed up the annotation process for object detection
- Simplify annotation and training operations to make them available for everyone

## Frontend

The system provides a web interface that allows to perform all operations described above.
From the interface it is possible to create a new dataset from local images. Then the user can add metadata to images (such as title and author of the work of art) and simply draw bounding boxes on them.
Furthermore, the system allows to run inference on images to draw bounding boxes automatically, using a network selected from Tensorflow models.
![alt text](https://github.com/EleonoraRistori/SmartLens/blob/master/Suddivisione.png?raw=true)
Since all dataset images are annotated, it is possible to start training of the selected model.

## Backend

### main.py

This is the main Python script of the system. Thanks to Flask framework, it is able to capture all client requests and handle them.
Firstly, it is used to load dataset images and display them on web interface.
Secondly, it provides methods to store annotations and metadata in the database and allows client to modify them.
Finally, it launches all subprocess to train the network


### inference.py

This module exposes the methods to run inference on images using pretrained TensorFlow models, in order to perform automatic annotation.
It is capable to deal both with a single image and the entire dataset.
Once the inference operation is preformed, it converts boxes in coco format and stores them in the database.

### create_annotations.py

This script is used in order to prepare annotations for training.
It gets all dataset annotations from the database, converts them in COCO format and dumps them into a JSON file.

### augment_annotated_boxes.py

This is the script used to perform augmentation of images before training. Thanks to data augmentation, it is possible to always train the network on many images, even if the dataset is relatively small.
It stores new images in `/webnet_augmented_dataset/<dataset_name>`

### partition_dataset.py

This script is launched to split the dataset in train and test sets and save results in `/webnet_splitted_dataset/<dataset_name>`

### convert_cocojson2tfrecord.py

This script allows to convert COCO annotations into tfRecords, that is the format used by the Tensorflow models.

### configure_detector_training.py

This last script is used to configure the pipeline for the training. It uses the sample *.config* file and modify it with all necessary paths
