# Use example

### A) Prepare the dataset

**1. Create augmentation**

        python augment_annotated_boxes.py ./dataset/birth_venus/birth_venus.jpg ./augmentation_output/birth_venus -n 1000

**2. Split augmented images in train/test**

        python partition_dataset.py -i ./augmentation_output/birth_venus -o ./dataset/birth_venus -j

**3. Convert COCO JSON files in TFRecord**

* first convert COCO json files of training directory

        python convert_cocojson2tfrecord.py -j ./dataset/birth_venus/train -l ./dataset/birth_venus/label_map.pbtxt -c ./dataset/birth_venus/train/train.csv -o ./dataset/birth_venus/train/train.tfrecord

* then convert COCO json files of test directory

        python convert_cocojson2tfrecord.py -j ./dataset/birth_venus/train -l ./dataset/birth_venus/label_map.pbtxt -c ./dataset/birth_venus/test/test.csv -o ./dataset/birth_venus/test/test.tfrecord

* alternatively convert XML annotation files created using labelImg

* safety check: inspect the .tfrecord files using `tf_utils/tfrecord_viewer.py`:

      python tf_utils/tfrecord_viewer.py ./dataset/birth_venus/test/test.tfrecord -v

## B) Train

**1. Prepare the training pipeline**

* Create a `.config` file using:

      python configure_detector_training.py --dataset_name birth_venus --download_model -l ./dataset/birth_venus/label_map.pbtxt --train_record ./dataset/birth_venus/train/train.tfrecord --test_record ./dataset/birth_venus/test/test.tfrecord

  the program will print the name and path of the new configuration file, e.g. `./models/training/ssd_mobilenet_v2_coco.config`. Use it in the training script

**2. Start TensorBoard to monitor training**

* open a terminal and run:

      tensorboard --logdir ./models/fine_tuned_models/training/birth_venus --host 0.0.0.0 --port 6006

  check it opening a browser window to `http://localhost:6006/`

**3. Start training**

    python path/to/tensorflow/models/research/object_detection/model_main_tf2.py \
    --pipeline_config_path={pipeline_config_path} \
    --model_dir={model_dir} \
    --alsologtostderr \
    --num_train_steps={num_steps} \
    --sample_1_of_n_eval_examples=1


where `{pipeline_config_path}` points to the new pipeline configuration created with `configure_detector_training` and `{model_dir}` is the `./models/fine_tuned/training/DATASET_NAME` directory where the new model will be written

**Export model inference graph**

Once training has been completed the checkpoints must be exported using:

    python path/to/tensorflow/models/research/object_detection/exporter_main_v2.py \
    --trained_checkpoint_dir {model_dir} \
    --output_directory {output_directory} \
    --pipeline_config_path {pipeline_config_path}

e.g. using the following:

    python ~/Workspace/tensorflow/models/research/object_detection/exporter_main_v2.py \
    --trained_checkpoint_dir ./models/fine_tuned_models/training/DATASET_NAME/ \
    --pipeline_config_path ./models/fine_tuned_models/training/DATASET_NAME/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.config \
    --output_directory ./models/fine_tuned_models/exported_inference_graph/DATASET_NAME

**Check model performance**

Test the exported model on some sample images using:

      python model_tester_viewer.py -m ./models/fine_tuned_models/exported_inference_graph/DATASET_NAME/saved_model -l ./dataset/DATASET_NAME/label_map.pbtxt -d ./dataset/test_fine_tuned_model

**Export inference graph to TensorflowJS**

Convert the exported model to TensorflowJS format using:

    tensorflowjs_converter --input_format=tf_saved_model ./models/fine_tuned_models/exported_inference_graph/DATASET_NAME/saved_model ./models/exported_tfjs/DATASET_NAME
