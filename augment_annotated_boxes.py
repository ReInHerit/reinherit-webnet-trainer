from coco_utils import COCOManager
import box_augmentations_transformer as atf
import cv2
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename', type=str,
                        help='Input file name (.json file with COCO annotation)')
    parser.add_argument('output_directory', type=str,
                        help='Output directory to store augmented images and associated JSON file with COCO annotations')
    parser.add_argument('-n', '--num_iterations', help='Number of iterations for each transformation set', default=5,
                        type=int)
    parser.add_argument('-m', '--min_visibility', type=float, default=0.2, help='Minimum visibility of augmented boxes')
    parser.add_argument('-s', '--single_json_file', action='store_true', default=False,
                        help='Produce a single COCO JSON file for each augmentation')
    args = parser.parse_args()

    output_dir = args.output_directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    dataset_dir, filename = os.path.split(args.input_filename)
    num_iterations = args.num_iterations
    print('Augment annotation boxes')
    print(f'Input COCO JSON file: {args.input_filename} - Dataset directory: {dataset_dir}\n'
          f'augmentation_output directory: {output_dir} - num iterations: {num_iterations} - min. visibility: {args.min_visibility}')

    coco = COCOManager(args.input_filename)
    images, images_sizes, bboxes, titles = coco.get_all_images_annotation()
    num_images = len(images)
    print(f'Processing {num_images} images.')

    print('Augmentation started...')
    num_augmentations = 0
    for image_idx in range(len(images)):
        img_filename = images[image_idx]
        img_coco_bboxes = bboxes[image_idx]
        img_titles = titles[image_idx]

        # read image and convert to RGB format
        bgr_image = cv2.imread(os.path.join(dataset_dir, img_filename))
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

        all_transformed_filenames = []
        all_transformed_image_sizes = []
        all_transformed_bboxes = []
        all_transformed_class_labels = []
        for i in range(num_iterations):
            progress = int((float(i+1) * (image_idx + 1)) / (num_iterations * num_images) * 100)
            if progress % 10 == 0 and i % 100 == 0:
                print(f'Augmentations created: {progress}%')
            for transform_name in atf.TRANSFORMS_DICT:
                transforms = atf.TRANSFORMS_DICT[transform_name]
                transform = transforms(args.min_visibility)

                transformed_instance = transform(image=rgb_image, bboxes=img_coco_bboxes, class_labels=img_titles)
                transformed_filename = img_filename + "_" + transform_name + "_iter" + str(i) + ".jpg"

                transformed_rgb_image = transformed_instance['image']
                transformed_bboxes = transformed_instance['bboxes']
                transformed_class_labels = transformed_instance['class_labels']
                if not transformed_bboxes:
                    continue  # transformation resulted in an image below min_visibility threshold, skip it
                # else if transformation provided results add them to list
                all_transformed_filenames.append(transformed_filename)
                transformed_bgr_image = cv2.cvtColor(transformed_rgb_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(output_dir, transformed_filename), transformed_bgr_image)
                num_augmentations += 1
                all_transformed_image_sizes.append([transformed_bgr_image.shape[0], transformed_bgr_image.shape[1]])
                all_transformed_bboxes.append(transformed_bboxes)
                all_transformed_class_labels.append(transformed_class_labels)

        print(f'Augmentation completed. Images created: {num_augmentations}')
        print('Creating JSON annotations for augmentations')
        if args.single_json_file:
            coco.save_coco_boxes(os.path.join(output_dir, "augmented_files.json"), all_transformed_filenames,
                                 all_transformed_image_sizes, all_transformed_bboxes, all_transformed_class_labels)
        else:
            coco.save_coco_boxes_files(output_dir, all_transformed_filenames,
                                       all_transformed_image_sizes, all_transformed_bboxes,
                                       all_transformed_class_labels)
        print('Annotations completed.')

