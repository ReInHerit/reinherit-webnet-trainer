import argparse
import os
import shutil
import urllib.request
import tarfile
import re

MODELS_CONFIG = {
    'ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8': {
        'download_base': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/',
        'model_name': 'ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8',
        'pipeline_file': 'pipeline.config',
        'check_point_name': 'checkpoint/ckpt-0',
        'create_tar_dir': False,
        'batch_size': 12,
        'note': 'Compatible with TF 2.x to train'
    },

    'efficientdet_d0_coco17_tpu-32': {
        'download_base': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/',
        'model_name': 'efficientdet_d0_coco17_tpu-32',
        'pipeline_file': 'pipeline.config',
        'check_point_name': 'checkpoint/ckpt-0',
        'create_tar_dir': False,
        'batch_size': 12,
        'note': 'Compatible with TF 2.x to train'
    },

    'centernet_resnet50_v1_fpn_512x512_coco17_tpu-8': {
        'download_base': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/',
        'model_name': 'centernet_resnet50_v1_fpn_512x512_coco17_tpu-8',
        'pipeline_file': 'pipeline.config',
        'check_point_name': 'checkpoint/ckpt-0',
        'create_tar_dir': False,
        'batch_size': 12,
        'note': 'Compatible with TF 2.x to train'
    },

    'faster_rcnn_resnet50_v1_640x640_coco17_tpu-8': {
        'download_base': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/',
        'model_name': 'faster_rcnn_resnet50_v1_640x640_coco17_tpu-8',
        'pipeline_file': 'pipeline.config',
        'check_point_name': 'checkpoint/ckpt-0',
        'create_tar_dir': False,
        'batch_size': 12,
        'note': 'Compatible with TF 2.x to train'
    },

    'ssd_resnet50_v1_fpn_640x640_coco17_tpu-8': {
        'download_base': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/',
        'model_name': 'ssd_resnet50_v1_fpn_640x640_coco17_tpu-8',
        'pipeline_file': 'pipeline.config',
        'check_point_name': 'checkpoint/ckpt-0',
        'create_tar_dir': False,
        'batch_size': 12,
        'note': 'Compatible with TF 2.x to train'
    },
}
PRETRAINED_DIR = './models/pretrained_models/'
TRAIN_MODEL_DIR = 'models/fine_tuned_models/training/'


def download_model(model_file_name, create_dir=True):
    model_file = model_file_name + '.tar.gz'

    if not (os.path.exists(os.path.join(PRETRAINED_DIR, model_file))):
        full_url = download_base + model_file
        print(f'Downloading file: {full_url}')
        urllib.request.urlretrieve(full_url, os.path.join(PRETRAINED_DIR, model_file))
        print('Download completed.')

        print(f'Untar/Unzip file: {os.path.join(PRETRAINED_DIR, model_file)}')
        tar = tarfile.open(os.path.join(PRETRAINED_DIR, model_file))
        if create_dir:
            tar.extractall(os.path.join(PRETRAINED_DIR, model_file_name))
        else:
            tar.extractall(PRETRAINED_DIR)
        tar.close()
        print('Model ready.')
    else:
        print(
            f'Model already available. Check that it is correctly decompressed in {os.path.join(PRETRAINED_DIR, model_file_name)}')


def get_num_classes(pbtxt_fname):
    from object_detection.utils import label_map_util
    label_map = label_map_util.load_labelmap(pbtxt_fname)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    return len(category_index.keys())


def configure_pipeline(num_classes, model_path, checkpoint_name, dataset_name, dest_dir=PRETRAINED_DIR):
    pipeline_fname = os.path.join(PRETRAINED_DIR, model_path, pipeline_file)
    assert os.path.isfile(pipeline_fname), '`{}` not exist'.format(pipeline_fname)
    fine_tune_checkpoint = os.path.join(dest_dir, model_path + "/" + checkpoint_name)
    print(fine_tune_checkpoint)
    print(dest_dir)
    print(model_path)
    print(checkpoint_name)
    model_training_dir = os.path.join(TRAIN_MODEL_DIR, dataset_name, model_path)
    if os.path.exists(model_training_dir):
        shutil.rmtree(model_training_dir)
    os.makedirs(model_training_dir)

    with open(pipeline_fname) as f:
        s = f.read()
    pipeline_out_fname = os.path.join(model_training_dir, pipeline_file)
    with open(pipeline_out_fname, 'w') as f:

        # fine_tune_checkpoint
        s = re.sub('fine_tune_checkpoint: ".*?"',
                   'fine_tune_checkpoint: "{}"'.format(fine_tune_checkpoint), s)

        # Set train tf-record file path train
        s = re.sub('input_path: ".*?"',
                   'input_path: "{}"'.format(train_record_fname), s)

        # Set test tf-record file path validation
        s = re.sub('input_path: ".*?"',
                   'input_path: "{}"'.format(test_record_fname), s)

        # label_map_path
        s = re.sub(
            'label_map_path: ".*?"', 'label_map_path: "{}"'.format(label_map_pbtxt_fname), s)

        # Set training batch_size.
        s = re.sub('batch_size: [0-9]+',
                   'batch_size: {}'.format(batch_size), s)

        # Set training steps, num_steps
        s = re.sub('num_steps: [0-9]+',
                   'num_steps: {}'.format(num_steps), s)

        # Set number of classes num_classes.
        s = re.sub('num_classes: [0-9]+',
                   'num_classes: {}'.format(num_classes), s)

        # Set fine-tune checkpoint type to detection
        s = re.sub('fine_tune_checkpoint_type: "classification"',
                   'fine_tune_checkpoint_type: "{}"'.format('detection'), s)

        f.write(s)
        print(f'New configuration for training: {pipeline_out_fname}')
        print(f'To train use: python path/to/tensorflow/models/research/object_detection/model_main_tf2.py --pipeline_config_path={pipeline_out_fname} --model_dir={model_training_dir} --alsologtostderr --num_train_steps={num_steps} --sample_1_of_n_eval_examples=1')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_model', action='store_true', help='download specified model')
    parser.add_argument('-m', '--model_name', type=str, default='ssd_mobilenet_v2_fpnlite_320',
                        help='Name of the model to be used')
    parser.add_argument('-n', '--num_training_steps', type=int, default=30000,
                        help='Number of training steps. 1000 for fast train, 200000 for better results...')
    parser.add_argument('-l', '--label_map_path', type=str, help='Path to label map file (.pbtxt file)')
    parser.add_argument('--dataset_name', type=str, help='Dataset name (to track the model and manage dirs)')
    parser.add_argument('--test_record', type=str, help='path to test TFRecord file')
    parser.add_argument('--train_record', type=str, help='path to train TFRecord file')
    args = parser.parse_args()

    # Number of training steps - 1000 will train very quickly, but more steps will increase accuracy.
    num_steps = args.num_training_steps  # 200000 to improve
    # Number of evaluation steps.
    num_eval_steps = 50

    # Pick the model you want to use
    # Select a model in `MODELS_CONFIG`.
    selected_model = args.model_name

    # Name of the object detection model to use.
    model_name = MODELS_CONFIG[selected_model]['model_name']
    download_base = MODELS_CONFIG[selected_model]['download_base']
    # Name of the pipline file in tensorflow object detection API.
    pipeline_file = MODELS_CONFIG[selected_model]['pipeline_file']
    if 'check_point_name' in MODELS_CONFIG[selected_model].keys():
        checkpoint_name = MODELS_CONFIG[selected_model]['check_point_name']
    else:
        checkpoint_name = 'model.ckpt'  # TF 1.x format
    # Training batch size fits in Colab's Tesla K80 GPU memory for selected model.
    batch_size = MODELS_CONFIG[selected_model]['batch_size']

    train_record_fname = args.train_record
    test_record_fname = args.test_record
    label_map_pbtxt_fname = args.label_map_path
    num_classes = get_num_classes(label_map_pbtxt_fname)
    print(f'Dataset name: {args.dataset_name}')
    print(f'Train record file : {train_record_fname}')
    print(f'Test record file  : {test_record_fname}')
    print(f'Labels file       : {label_map_pbtxt_fname}')
    print(f'Num. classes      : {num_classes}')
    print(f'Fine-tuned model  : {model_name}')
    print(f'Check point file  : {checkpoint_name}')
    print(f'Training steps    : {num_steps}')
    note_txt = MODELS_CONFIG[selected_model]['note']
    print(f'NOTE: {note_txt}')

    if args.download_model:
        if 'create_tar_dir' in MODELS_CONFIG[selected_model]:
            create_tar_dir = MODELS_CONFIG[selected_model]['create_tar_dir']
        else:
            create_tar_dir = True  # default for old TF 1.x models
        print(f'Download model: {selected_model} - create TAR dir: {create_tar_dir}')
        download_model(model_name, create_tar_dir)

    configure_pipeline(num_classes, model_name,  checkpoint_name, args.dataset_name)
