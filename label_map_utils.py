import os
from object_detection.utils import dataset_util, label_map_util


def buildLabelMap(categories):
    with open('static/new_label_map.pbtxt', 'w') as the_file:
        the_file.write("")

    with open('static/new_label_map.pbtxt', 'a') as the_file:
        for i in range(len(categories)):
            the_file.write('item {\n')
            the_file.write('\tid: ' + str(categories[i][0]))
            the_file.write('\n')
            the_file.write('\tname: ' + "'" + categories[i][1] + "'")
            the_file.write('\n')
            the_file.write('}\n\n')


def createLabelsDict(labels_path):
    label_map = label_map_util.load_labelmap(labels_path)
    label_map_dict = label_map_util.get_label_map_dict(label_map, True)
    return label_map_dict


def get_labels(labels_path):
    labelsDict = createLabelsDict(labels_path)
    labelsTuple = []
    for key in labelsDict:
        labelsTuple.append((labelsDict[key], key))
    return labelsTuple


if __name__ == '__main__':
    label_map_path = "./static/label_map.pbtxt"
    get_labels(label_map_path)
