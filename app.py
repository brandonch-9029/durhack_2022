from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import requests
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

    response12 = img_upload_azure('https://durhack.blob.core.windows.net/img/' + name_of_img)
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
    name_of_img = 'img' + timestamp + '.jpg'
    

    response = uploadToBlobStorage(img_to_upload, name_of_img)
    return response


def img_upload_azure(bloblink):
    items_list = []
    headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': 'a417d15b78a4452bb8f1ec5c52836d4e',
    }

    body = {'url': bloblink}
    try:
        response = requests.post("https://computervisiontoad.cognitiveservices.azure.com/vision/v3.2/detect?model-version=latest", json=body, headers=headers)
        data = response.json()
        for objects in data["objects"]:
            object_info = []
            item = objects["object"]
            x = objects["rectangle"]["x"]
            y = objects["rectangle"]["y"]
            w = objects["rectangle"]["w"]
            h = objects["rectangle"]["h"]
            object_info.append(item)
            object_info.append(x)
            object_info.append(y)
            object_info.append(w)
            object_info.append(h)
            items_list.append(object_info)
        print(data)
        return items_list
    except Exception as e:
        print(e)
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


if __name__ == "__main__":
    app.run(debug=True)