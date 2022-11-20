import json
import os

def saveCocoBoxes(categories, images, annotations, output_dir):
    classes = []
    imagesData = []
    annotationsData = []
    
    for i in range(len(categories)):
        classData = dict()
        classData["id"] = categories[i][0]
        classData["name"] = categories[i][1]
        classes.append(classData)
    
    for i in range(len(images)):
        imgData = dict()
        imgData["id"] = images[i][0]
        _, imgData["file_name"] = os.path.split(images[i][1])
        imgData["width"] = images[i][2]
        imgData["height"] = images[i][3]
        imagesData.append(imgData)

    for i in range(len(annotations)):
        bbox = [annotations[i][4], annotations[i][5], annotations[i][6], annotations[i][7]]
        annData = dict()
        annData["id"] = annotations[i][0]
        annData["image_id"] = annotations[i][1]
        annData["category_id"] = annotations[i][2]
        annData["area"] = annotations[i][3]
        annData["bbox"] = bbox
        annotationsData.append(annData)

    json_results = dict()
    json_results['categories'] = classes
    json_results['images'] = imagesData
    json_results['annotations'] = annotationsData

    annotations_path = output_dir + "annotations.json"
    with open(annotations_path, 'w') as outfile:
        json.dump(json_results, outfile)
