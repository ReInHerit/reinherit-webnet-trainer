import re
import os
import numpy as np

output_directory = './models/fine_tuned_model/'
training_directory = './models/training/'

lst = os.listdir(training_directory)
lst = [l for l in lst if 'model.ckpt-' in l and '.meta' in l]
steps=np.array([int(re.findall('\d+', l)[0]) for l in lst])
last_model = lst[steps.argmax()].replace('.meta', '')

last_model_path = os.path.join(training_directory, last_model)
print(f'The model that must be exported is: {last_model_path}')
print(f'Output path: {output_directory}')