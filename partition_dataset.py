""" usage: partition_dataset.py [-h] [-i IMAGEDIR] [-o OUTPUTDIR] [-r RATIO] [-x]

Partition dataset of images into training and testing sets

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGEDIR, --imageDir IMAGEDIR
                        Path to the folder where the image dataset is stored. If not specified, the CWD will be used.
  -o OUTPUTDIR, --outputDir OUTPUTDIR
                        Path to the output folder where the train and test dirs should be created.
                        Defaults to the same directory as IMAGEDIR.
  -r RATIO, --ratio RATIO
                        The ratio of the number of test images over the total number of images. The default is 0.1.
  -x, --xml             Set this flag if you want the XML annotation files to be processed and copied over.
  -j, --json            Set this flag if you want the JSON annotation files to be processed and copied over.
"""
import os
import re
from shutil import copyfile
import argparse
import math
import random


def iterate_dir(source, dest, ratio, copy_xml, copy_json):
    source = source.replace('\\', '/')
    dest = dest.replace('\\', '/')
    train_dir = os.path.join(dest, 'train')
    test_dir = os.path.join(dest, 'test')
    print(f'Train directory: {train_dir}')
    print(f'Test directory: {test_dir}')

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    images = [f for f in os.listdir(source)
              if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(?i)(.jpg|.jpeg|.png)$', f)]

    num_images = len(images)
    num_test_images = math.ceil(ratio * num_images)

    print(f'Copying test data... {num_test_images} images')
    for i in range(num_test_images):
        idx = random.randint(0, len(images) - 1)
        filename = images[idx]
        copyfile(os.path.join(source, filename),
                 os.path.join(test_dir, filename))
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0] + '.xml'
            copyfile(os.path.join(source, xml_filename),
                     os.path.join(test_dir, xml_filename))
        if copy_json:
            json_filename = os.path.splitext(filename)[0] + '.json'
            copyfile(os.path.join(source, json_filename),
                     os.path.join(test_dir, json_filename))

        images.remove(images[idx])
    print('Copying test data completed.')

    print(f'Copying train data... {int(num_images-num_test_images)} images')
    for filename in images:
        copyfile(os.path.join(source, filename),
                 os.path.join(train_dir, filename))
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0] + '.xml'
            copyfile(os.path.join(source, xml_filename),
                     os.path.join(train_dir, xml_filename))
        if copy_json:
            json_filename = os.path.splitext(filename)[0] + '.json'
            copyfile(os.path.join(source, json_filename),
                     os.path.join(train_dir, json_filename))
    print('Copying train data completed.')

def main():
    print('Partition Dataset.')
    # Initiate argument parser
    parser = argparse.ArgumentParser(description="Partition dataset of images into training and testing sets",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-i', '--imageDir',
        help='Path to the folder where the image dataset is stored. If not specified, the CWD will be used.',
        type=str,
        default=os.getcwd()
    )
    parser.add_argument(
        '-o', '--outputDir',
        help='Path to the output folder where the train and test dirs should be created. '
             'Defaults to the same directory as IMAGEDIR.',
        type=str,
        default=None
    )
    parser.add_argument(
        '-r', '--ratio',
        help='The ratio of the number of test images over the total number of images. The default is 0.1.',
        default=0.1,
        type=float)
    parser.add_argument(
        '-x', '--xml',
        help='Set this flag if you want the XML annotation files to be processed and copied over.',
        action='store_true'
    )
    parser.add_argument(
        '-j', '--json',
        help='Set this flag if you want the JSON annotation files to be processed and copied over.',
        action='store_true'
    )
    args = parser.parse_args()

    if args.outputDir is None:
        args.outputDir = args.imageDir

    print(f'Input (image) dir: {args.imageDir} - Output dir: {args.outputDir} - train/test ratio {args.ratio}')
    print(f'Copy XML files: {args.xml} - copy JSON files: {args.json}')

    # Now we are ready to start the iteration
    iterate_dir(args.imageDir, args.outputDir, args.ratio, args.xml, args.json)


if __name__ == '__main__':
    main()
