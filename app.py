from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
#from PIL import Image
import sys
import time
import flask
from azure.storage.blob import BlobServiceClient

storage_account_key = "htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ=="
storage_account_name = "durhack"
connection_string = "DefaultEndpointsProtocol=https;AccountName=durhack;AccountKey=htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ==;EndpointSuffix=core.windows.net"
container_name = "img"

app = flask.Flask(__name__)
counter = 1
def uploadToBlobStorage(img, name_of_img):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=name_of_img)

    with open(img, "rb") as data:
        blob_client.upload_blob(data)
    counter += 1
    return counter


@app.route("/")
def test():
    return "hello"



@app.route("/img_upload", methods=["POST", "GET"])
def save():
    try:
        img_to_upload = flask.request.files["imgfile"]

    except:
        raise ValueError("Error, nothing recieved")
    
    name_of_img = "img"+ counter
    

    uploadToBlobStorage(img_to_upload, name_of_img)
    return flask.Response("{'a':'b'}", status=201, mimetype='application/json')












def img_upload_azure():
    '''
    Authenticate
    Authenticates your credentials and creates a client.
    '''
    subscription_key = "a417d15b78a4452bb8f1ec5c52836d4e"
    endpoint = "PASTE_YOUR_COMPUTER_VISION_ENDPOINT_HERE"

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    '''
    END - Authenticate
    '''

    '''
    Quickstart variables
    These variables are shared by several examples
    '''
    # Images used for the examples: Describe an image, Categorize an image, Tag an image, 
    # Detect faces, Detect adult or racy content, Detect the color scheme, 
    # Detect domain-specific content, Detect image types, Detect objects
    images_folder = os.path.join (os.path.dirname(os.path.abspath(__file__)), "images")
    remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
    '''
    END - Quickstart variables
    '''


    '''
    Tag an Image - remote
    This example returns a tag (key word) for each thing in the image.
    '''
    print("===== Tag an image - remote =====")
    # Call API with remote image
    tags_result_remote = computervision_client.tag_image(remote_image_url )

    # Print results with confidence score
    print("Tags in the remote image: ")
    if (len(tags_result_remote.tags) == 0):
        print("No tags detected.")
    else:
        for tag in tags_result_remote.tags:
            print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))
    print()
    '''
    END - Tag an Image - remote
    '''
    print("End of Computer Vision quickstart.")
if __name__ == "__main__":
    app.run(debug=True)