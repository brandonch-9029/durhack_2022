from array import array
import requests
import os
#from PIL import Image
import sys
import time
import flask
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.data.tables import TableServiceClient, TableClient
import time
import json
from flask_cors import CORS
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

    upload = img_upload_azure('https://durhack.blob.core.windows.net/img/' + name_of_img, name_of_img)
    return upload
    


@app.route("/")
def test():
    return "hello"


# POST request to upload img to azure database and use computer vision
@app.route("/img_upload", methods=["POST", "GET"])
def save():
    try:
        img_to_upload = flask.request.files["imgfile"]

    except:
        raise ValueError("Error, nothing recieved")
    
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H%M', t)
    name_of_img = 'img' + timestamp + '.jpg'
    

    final_return = uploadToBlobStorage(img_to_upload, name_of_img)
    return final_return

# request for JSONData to draw rectangles
@app.route("/get_data/<name_of_img>", methods=["GET"])
def returnJson(name_of_img):
    data = get_table_data_azure(name_of_img=name_of_img)
    JSONData = flask.jsonify(data)
    return JSONData


# uploading the img to the azure datalake
def img_upload_azure(bloblink, name_of_img):
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
        width_img = data["metadata"]["width"]
        height_img = data["metadata"]["height"]
        items_list.append(width_img)
        items_list.append(height_img)
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
        upload_to_azure_tables(items_list, name_of_img=name_of_img)
        return name_of_img
    except Exception as e:
        print(e)
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
# create the dictionary to upload to the azure table
def create_dict(items_list):
    objects = {"width": items_list[0], "height" : items_list[1]}
    print(items_list)
    n = len(items_list)
    for i in range(2, n):
        objects["object"+ str(i-1)] ={}
        for j in range(0, 5):
            if j == 0:
                objects["object" + str(i-1)]["item"] = items_list[i][j]
            elif j == 1:
                objects["object" + str(i-1)]["x"] = items_list[i][j]
            elif j == 2:
                objects["object" + str(i-1)]["y"] = items_list[i][j]
            elif j == 3:
                objects["object" + str(i-1)]["w"] = items_list[i][j]
            elif j == 4:
                objects["object" + str(i-1)]["h"] = items_list[i][j]
    return objects

               
# upload JSON data to azure table         
def upload_to_azure_tables(items_list, name_of_img):
    dict_to_upload = create_dict(items_list)
    entity = {
        "PartitionKey" : name_of_img,
        "RowKey" : json.dumps(dict_to_upload)
        }
    connection_string_tables = "DefaultEndpointsProtocol=https;AccountName=durhack;AccountKey=htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ==;EndpointSuffix=core.windows.net"
    service = TableServiceClient.from_connection_string(connection_string_tables)
    table_client = service.get_table_client(table_name="durhacktable")
    entity = table_client.create_entity(entity=entity)
    return name_of_img 
# query azure table for img data
def get_table_data_azure(name_of_img):
    my_filter = "PartitionKey eq '{}'".format(name_of_img)
    table_client = TableClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=durhack;AccountKey=htIhM+7rKVqMCz8G27yqpk7S7QPTOC8uU5Lo5viq+YjhDRfJzupx9v5+CmzpTXptVUMf5kgo5KGq+AStR4DoJQ==;EndpointSuffix=core.windows.net", table_name="durhacktable")
    entities = table_client.query_entities(my_filter)
    for entity in entities:
        return entity["RowKey"]


if __name__ == "__main__":
    app.run(debug=True)