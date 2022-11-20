# INSTALL REQUIREMENTS

## Install Anaconda (optional)

* Install the latest version of Anaconda from `https://www.anaconda.com/products/distribution`
* Create a new conda environment:
  `conda create -n tensorflow pip python=3.9`
* Activate conda environment:
  `conda activate tensorflow`

## Install TensorFlow

* Check TensorFlow Object Detection API Installation:

  `https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html`

**Install the TensorFlow PIP package**

* `pip install --ignore-installed --upgrade tensorflow==2.5.0`

**Install GPU support (optional but recommended for training)**

* Check `https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#gpu-support-optional`
  
## Install TensorFlow Object Detection API

**Download TensorFlow Model Garden**

  * Create a new folder under a path of your choice and name it *Tensorflow* (e.g. `C:/Users/user/Documents/Tensorflow`)
  * From terminal, move into *Tensorflow* directory (e.g. `cd Documents/Tensorflow`)
  * Clone TensorFlow models directory: `git clone https://github.com/tensorflow/models`

**Download and install Protobuf**

  * Download the latest release of `protoc-*-*.zip` from `https://github.com/protocolbuffers/protobuf/releases`
  * Extract downloaded files into a directory of your choice (e.g. `C:/Users/user/protoc`)
  * Add *Path/to/protoc* to your *Path* environment variable
  * From *Tensorflow/models/research* run `protoc object_detection/protos/*.proto --python_out=.`

**Install COCO API**

  * `pip install cython`
  * `pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI`

**Install Object Detection API**

  * From *Tensorflow/models/research* run `cp object_detection/packages/tf2/setup.py .` (NOTE: if you are on Windows this command will not work, run it from a Git Bash shell)
  * From *Tensorflow/models/research* `python -m pip install --use-feature=2020-resolver .`

**Test your installation**

  * From *Tensorflow/models/research* `python object_detection/builders/model_builder_tf2_test.py`
  * NOTE: Running the above command, you may observe the error: *ImportError: cannot import name 'builder' from 'google.protobuf.internal'*
    - To solve this error, install the latest version of Protobuf: `pip install protobuf`
    - Copy `builder.py` from `.../Lib/site-packages/google/protobuf/internal` to a path of your choice
    - Install version of Protobuf compatible with your projects (e.g. `pip install protobuf==3.19.6` in our example)
    - Paste `builder.py` in `.../Lib/site-packages/google/protobuf/internal`

## Install Flask
  
  * `pip install Flask`

## Install other dependencies

* `pip install pillow`
* `pip install labelImg`
* Test using `labelImg <path/to/images>`
