from pymongo import MongoClient
import gridfs
from MongoDB_client import mongo_connect,delete_and_upload__all_jpg_files


import gridfs
if __name__ == '__main__':
    connection_string = "mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority"
    file_name = "face.yml"
    client = mongo_connect("mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority")
    db = client.facemodel
    fs = gridfs.GridFS(db, collection = "files")
    imgs = gridfs.GridFS(db, collection = "test_images")
    #upload_file(file_name , fs)
    #download_file(db, fs, file_name)
    #download_all_jpg_files(fs,"datasets")
    #upload_all_jpg_files("datasets", imgs)
    #download_all_jpg_files(imgs, "datasets")
    #delete_and_load_all_jpg_files(imgs,"datasets")
    delete_and_upload__all_jpg_files("datasets",imgs)
