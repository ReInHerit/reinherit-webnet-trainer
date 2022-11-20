# Use example

## Initialize your database

  * From your terminal run `python init_db.py path/to/Tensorflow` (e.g. `python init_db.py C:/Users/user/Documents/Tensorflow`)

## Run Flask app

  * Set Flask app location
    - on Windows: `set FLASK_APP=main.py`
    - on Linux/macOS: `export FLASK_APP=main.py`

  * Run with `flask run` (default port: 5000)
    - if you want to use another port use `flask run -h localhost -p 3000`

## WebNet Trainer - Home Page

  * Click `Upload your dataset` to create a new dataset from your images
  * Select concepts of your interest and click `Use these concepts`
  * Select pretrained model that you want to use
  * Click on images previews to open relative annotation pages
  * Click `Annotate` to run automatic annotation on all images with the selected model
  * Click `Start training` to train that model on your images

## WebNet Trainer - Annotation Page

  * Use text inputs on the left to add metadata to your work of art
  * Click `+` button to draw a bounding box manually and select the relative concept
  * Click `Annotate` to run automatic annotation on this image
  * Click `Save annotations` to save boxes and metadata and go back to the home page
