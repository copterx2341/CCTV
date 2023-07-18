import cv2
import numpy as np
from PIL import Image
import os 
from MongoDB_client import mongo_connect, download_all_jpg_files, upload_file_here
import time
#import gridfs

#Training model from images that are capture
def train_model(path, modelsname, fs):
    imagepath = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    for imagepaths in imagepath:
        faceimage = Image.open(imagepaths).convert('L')
        faceNP = np.array(faceimage)
        ID = (os.path.split(imagepaths)[-1].split(".")[1])
        ID = int(ID)
        faces.append(faceNP)
        ids.append(ID)
    recog = cv2.face.LBPHFaceRecognizer_create()
    recog.train(faces, np.array(ids))
    recog.write(modelsname + ".yml")
    upload_file_here("face.yml", fs)

def train_model_online(path, modelsname, fs,img):
    download_all_jpg_files(img, path)
    imagepath = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    for imagepaths in imagepath:
        faceimage = Image.open(imagepaths).convert('L')
        faceNP = np.array(faceimage)
        ID = (os.path.split(imagepaths)[-1].split(".")[1])
        ID = int(ID)
        faces.append(faceNP)
        ids.append(ID)
    recog = cv2.face.LBPHFaceRecognizer_create()
    recog.train(faces, np.array(ids))
    recog.write(modelsname + ".yml")
    upload_file_here("face.yml", fs)


#get the id of people in picture
def get_id(path):
    imagepath = [os.path.join(path, f) for f in os.listdir(path)]
    ids = [""]
    for imagepaths in imagepath:
        ID = (os.path.split(imagepaths)[-1].split(".")[1])
        ID = int(ID)
        if ID not in ids:
            ids.append(ID)
    return ids

"""
def Take_img():
    video = cv2.VideoCapture(0)
    model = YOLO('yolov8n-face.pt')
    id = input("Enter Your ID: ")
    id = int(id)
    count = 10
    db = mongo_connect("mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority")
    fs = gridfs.GridFS(db, collection = "images")
    while True:
        ret,frame = video.read()
        results = model(frame, stream=True)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h =  x2-x1, y2-y1
                count = count + 1
                cv2.imwrite('datasets/User.'+str(id)+"."+str(count)+".jpg", gray[y1:y1+h, x1:x1+w])
                upload_file("datasets\\", "User."+str(id)+"."+str(count)+".jpg", fs)
                cv2.rectangle(frame, (x1,y1), (x1+w, y1+h), (50 , 50 , 255), 1)
        cv2.imshow("Frame",frame)
        k=cv2.waitKey(1)
        if count>9:
            break
    video.release()
    cv2.destroyAllWindows()
    print("Collect Done")

#Take_img()


#train_model(datasets,Copter)
"""

"""
import gridfs
client = mongo_connect("mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority")
db = client.facemodel
fs = gridfs.GridFS(db, collection = "files")
bucket = "CCTV"
org = "Count"
token = "EtdJ4V81dQYC-TPg7JewfbLfpYwJ8pR92jbCeRDCngv6EZYyufxgyWadSrcjKpJwDWKY7FKY8x9SpNQ8mpfoqA=="
url = "http://localhost:8086"
imgs = gridfs.GridFS(db, collection = f"images")
train_model("datasets","face",fs)
"""
