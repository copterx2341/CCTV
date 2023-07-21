import yaml
import math
from ultralytics import YOLO
import cv2
from influxwrite import write_data
from trainingmodel import get_id
from countpeople import count_people
from MongoDB_client import mongo_connect, check_face_yml_modified, check_face_yml_start, download_all_jpg_files,upload_file,delete_and_load_all_jpg_files
import gridfs
import threading
import time,os
import cvzone
from PIL import Image
import requests

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

connect_str = config['mongodb']['connect_str']
client = mongo_connect(connect_str)
db = client.facemodel
collection_name = config['mongodb']['collection_name']
img_name = config['mongodb']['img_name']
fs = gridfs.GridFS(db, collection= collection_name)
imgs = gridfs.GridFS(db, collection= img_name)
bucket = config['bucket']
org = config['org']
token = config['token']
url = config['url']
frame_rate = config['frame_rate']
path = config['path']
model_names = config['names']
No_CCTV = config['No_CCTV']
address = config['address']
frame_rate = config['frame_rate']
line_token = config['line_token']
line_url = ' https://notify-api.line.me/api/notify'
headers = {'Authorization' : 'Bearer {}'.format(line_token)}


def resize_image(file_path, new_width, new_height):
    # Open the image file
    image = Image.open(file_path)

    # Resize the image
    resized_image = image.resize((new_width, new_height))

    # Overwrite the original image file
    resized_image.save(file_path)

def video_detection(address):
    #Create a Webcam Object
    check_face_yml_start(fs)
    delete_and_load_all_jpg_files(imgs, path)
    cap=cv2.VideoCapture(address)
    if cap.isOpened(): 
        recog = cv2.face.LBPHFaceRecognizer_create()
        recog.read("face.yml")
        count = 0
        model = YOLO('yolov8n-face.pt')
        num_cctv = "CCTV" + str(No_CCTV)
        def write_data_threads():
            nonlocal thread_running
            if thread_running:
                write_data(bucket, num_cctv, "People", org, token, url, num)
                time.sleep(1)
                thread_running = False
        thread_running = False
        frame_rate = 0
        thread_run = False
        def write_data_thread():
            nonlocal thread_run
            if thread_run:
                write_data(bucket, num_cctv, "People_ID", org,token,url, str(ids))
                time.sleep(1)
                thread_run = False
        def imwrite_thread():
            nonlocal thread_runs
            if thread_runs:
                os.makedirs("linePic", exist_ok=True)
                cv2.imwrite('linePic/line' + time_local + ".png", img)
                img_line = {'imageFile' : open('linePic/line'+ time_local + ".png", 'rb')}
                data = {'message' : f'พบเจอคน ID:{ids}'}
                requests.post(line_url, headers= headers , files = img_line, params= data)
                time.sleep(60)
                thread_runs = False
        thread_runs = False
        while True:
            success, img = cap.read()
            if success:
                frame_rate += 1
                if frame_rate % 8 != 0:
                    continue
                check = check_face_yml_modified(fs)
                if check:
                    recog = cv2.face.LBPHFaceRecognizer_create()
                    recog.read("face.yml")
                    download_all_jpg_files(imgs, path)
                ids = []
                name_list = get_id(path)
                count += 1
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                results=model(img,stream=True)
                
                for r in results:
                    boxes=r.boxes
                    for box in boxes:
                        x1,y1,x2,y2=box.xyxy[0]
                        x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
                        w, h = x2 - x1, y2 - y1
                        serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
                        conf=math.ceil((box.conf[0]*100))/100
                        if conf > 0.65:
                            if confs <= 85:
                                cvzone.putTextRect(img, f'ID:{name_list[serial]}', (max(0, x1), max(35, y1)), scale=0.6,
                                            thickness=1, offset=3)
                                cvzone.cornerRect(img, (x1, y1, w, h), l=10)
                                ids.append(name_list[serial])
                                
                            else:
                                cvzone.putTextRect(img, "UNKNOWN", (max(0, x1), max(35, y1)), scale=0.6, thickness=1, offset=3)
                                cvzone.cornerRect(img, (x1, y1, w, h), l=10)
                    if ids:
                        if not thread_run:
                            thread_run = True
                            threading.Thread(target=write_data_thread,daemon=False).start()
                    num = count_people(model, img)
                    if not thread_running:
                        thread_running = True
                        threading.Thread(target=write_data_threads, daemon=False).start()
                    time_local = time.strftime("%m%d%Y%H%M%S")
                    time_local = str(time_local)
                    time_string = time.strftime("%H")
                    time_hour = int(time_string)

                    if time_hour >= 20:
                        if num >=2:
                            if not thread_runs:
                                thread_runs = True
                                threading.Thread(target=imwrite_thread,daemon=False).start()        
                    elif time_hour>=0 and time_hour<=4:
                        if num >=1:
                            if not thread_runs:
                                thread_runs = True
                                threading.Thread(target=imwrite_thread,daemon=False).start()
                yield img
            else:
                break
        
def video_detection_main(address):
    check_face_yml_start(fs)
    delete_and_load_all_jpg_files(imgs, path)
    #Create a Webcam Object
    cap=cv2.VideoCapture(address)
    if cap.isOpened():
        model = YOLO('yolov8n-face.pt')
        recog = cv2.face.LBPHFaceRecognizer_create()
        recog.read("face.yml")
        person_count = 0
        count = 0
        point_blocks = {}
        point_block_prv = []
        frame_rate = 0
        def resize_image_thread():    
            resize_image('datasets/User.' + str(points) + "." + str(person_count) + str(int(x1)) + ".jpg", 200, 200)
        def upload_file_thread():
            upload_file('datasets/User.' + str(points) + "." + str(person_count) + str(int(x1)) + ".jpg", imgs)
        def imwrite_thread():
            cv2.imwrite('datasets/User.' + str(points) + "." + str(person_count) + str(int(x1)) + ".jpg", gray[y1:y1 + h, x1:x1 + w])
        
        while True:
            success, img = cap.read()
            if success:
                frame_rate += 1
                if frame_rate % 8 != 0:
                    continue
                check = check_face_yml_modified(fs)
                if check:
                    recog = cv2.face.LBPHFaceRecognizer_create()
                    recog.read("face.yml")
                    download_all_jpg_files(imgs, path)
                name_list = get_id(path)
                point = len(name_list)
                count += 1
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                point_block = []
                results = model(img, stream=True)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        w, h = x2 - x1, y2 - y1
                        serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
                        conf = math.ceil(box.conf[0] * 100) / 100
                        if conf > 0.65:
                            if confs <= 90:
                                cvzone.putTextRect(img, f'ID:{name_list[serial]}', (max(0, x1), max(35, y1)),
                                                scale=0.6, thickness=1, offset=3)
                                cvzone.cornerRect(img, (x1, y1, w, h), l=10)
                            else:
                                cvzone.putTextRect(img, "UNKNOWN", (max(0, x1), max(35, y1)), scale=0.6, thickness=1, offset=3)
                                cvzone.cornerRect(img, (x1, y1, w, h), l=10)
                                if w >= 60 and h >= 60: 
                                    maxx = max(0, x1)
                                    maxy = max(35, y1)
                                    point_block.append((maxx, maxy))
                    if count <= 2:
                        for xy in point_block:
                            for xy2 in point_block_prv:
                                distance = math.hypot(xy2[0] - xy[0], xy2[1] - xy[1])
                                if distance < 20:
                                    point_blocks[point] = xy
                                    point += 1

                    else:
                        point_blocks_copy = point_blocks.copy()
                        point_block_copy = point_block.copy()
                        for points, xy2 in point_blocks_copy.items():
                            obj_exist = False
                            for xy in point_block_copy:
                                distance = math.hypot(xy2[0] - xy[0], xy[1] - xy[1])
                                if distance < 20:
                                    point_blocks[points] = xy
                                    obj_exist = True
                                    if xy in point_block:
                                        point_block.remove(xy)
                                    continue
                            if not obj_exist:
                                point_blocks.pop(points)
                        for xy in point_block:
                            point_blocks[point] = xy
                            point += 1
                    for points, xy in point_blocks.items():
                        count = count + 1

                        for box in boxes:
                            person_count += 1
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            w, h = x2 - x1, y2 - y1
                            conf = math.ceil(box.conf[0] * 100) / 100
                            maxx = max(0, x1)
                            maxy = max(35, y1)
                            serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
                            if conf > 0.65:
                                if confs > 90 and xy == (maxx, maxy):
                                    t1=threading.Thread(target=imwrite_thread,daemon=False)
                                    t2=threading.Thread(target=resize_image_thread,daemon=False)
                                    t3=threading.Thread(target=upload_file_thread,daemon=False)
                                    
                                    t1.start()
                                    t1.join()  # Wait for Thread 1 to finish
                                    t2.start()
                                    t2.join()  # Wait for Thread 2 to finish
                                    t3.start()
                point_block_prv = point_block.copy()
                yield img
            else:
                break


