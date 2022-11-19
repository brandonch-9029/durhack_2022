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
from azure.storage.blob import BlobServiceClient, ContentSettings
import time
storage_account_key = "htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ=="
storage_account_name = "durhack"
connection_string = "DefaultEndpointsProtocol=https;AccountName=durhack;AccountKey=htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ==;EndpointSuffix=core.windows.net"
container_name = "img"

app = flask.Flask(__name__)
def uploadToBlobStorage(img, name_of_img):
    image_content_setting = ContentSettings(content_type='image/jpeg')
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=name_of_img)
    if img.filename != '':
        img_path = "img/" + name_of_img
        img.save(img_path)
        
    with open(img_path, "rb") as data:
        blob_client.upload_blob(data, overwrite = True,  content_settings=image_content_setting)

    response12 = img_upload_azure("https://durhack.blob.core.windows.net/img/" + name_of_img)
    return response12
    


@app.route("/")
def test():
    return "hello"



@app.route("/img_upload", methods=["POST", "GET"])
def save():
    try:
        img_to_upload = flask.request.files["imgfile"]

    except:
        raise ValueError("Error, nothing recieved")
    
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H%M', t)
    name_of_img = "img" + timestamp + ".jpg"
    

    response = uploadToBlobStorage(img_to_upload, name_of_img)
    return response












def img_upload_azure(bloblink):
    response_list = []
    '''
    Authenticate
    Authenticates your credentials and creates a client.
    '''
    subscription_key = "a417d15b78a4452bb8f1ec5c52836d4e"
    endpoint = "https://computervisiontoad.cognitiveservices.azure.com/"

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
    remote_image_url = bloblink
    '''
    END - Quickstart variables
    '''


    '''
    Tag an Image - remote
    This example returns a tag (key word) for each thing in the image.
    '''
    # Call API with remote image
    tags_result_remote = computervision_client.tag_image(remote_image_url )

    # Print results with confidence score
    print("Tags in the remote image: ")
    if (len(tags_result_remote.tags) == 0):
        print("No tags detected.")
    else:
        for tag in tags_result_remote.tags:
            temp = "'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100)
            response_list.append(temp)
    
    return response_list


if __name__ == "__main__":
    app.run(debug=True)