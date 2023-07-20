import cv2
from ultralytics import YOLO
import cvzone
import math
from trainingmodel import train_model, get_id
from countpeople import count_people
from MongoDB_client import mongo_connect, check_face_yml_modified, check_face_yml_start, download_all_jpg_files, upload_file, upload_all_jpg_files
from influxwrite import write_data
import threading
import time
import gridfs
"""
file_name = "face.yml"
file_loc = "C:\\Users\\User\\OneDrive\\Desktop\\IPCamera\\Project\\Complete Code\\" + file_name
down_loc = os.path.join(os.getcwd() + "\\downloads\\", file_name)
collection = db['files']
change_stream = collection.watch()
connection_string = "mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority"
db = mongo_connect(connection_string)
fs = gridfs.GridFS(db, collection = "Images")
"""


# Use in main CCTV camera to detect people and deep learn to recognize people
def face_detect_training(frame, model, recog, name_list, point, person_count, count, point_blocks, point_block_prv, img, No_CCTV):
    """
    name_list = get_id("datasets")
    point_blocks = {}
    point_block_prv=[]
    point = len(name_list)
    count = 0
    person_count = 1
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    point_block = []
    # People_id=[]
    results = model(frame, stream=True)
    def upload_all_jpg_files_thread():
        nonlocal thread_upload
        if thread_upload:
            time.sleep(60)
        #upload_file("datasets\\", "User." + str(points) + "." + str(person_count) + str(int(x1)) + ".jpg", img)
            upload_all_jpg_files("datasets",img)
            thread_upload = False


    def imwrite_thread():
        cv2.imwrite('datasets/User.' + str(points) + "." + str(person_count) + str(int(x1)) + ".jpg", gray[y1:y1 + h, x1:x1 + w])
    
    def write_data_thread():
        nonlocal thread_runnings
        if thread_runnings:
            time.sleep(1)
            write_data("CCTV",No_CCTV,"People_ID", "Count", "EtdJ4V81dQYC-TPg7JewfbLfpYwJ8pR92jbCeRDCngv6EZYyufxgyWadSrcjKpJwDWKY7FKY8x9SpNQ8mpfoqA==", "http://localhost:8086", str(name_list[serial]))
            thread_runnings = False

    thread_upload = False
    thread_runnings = False
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
            conf = math.ceil(box.conf[0] * 100) / 100
            if conf > 0.6:
                if confs <= 100:
                    cvzone.putTextRect(frame, f'ID:{name_list[serial]}', (max(0, x1), max(35, y1)),
                                       scale=0.6, thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                    if not thread_runnings:
                        thread_runnings = True
                        threading.Thread(target=write_data_thread,daemon=False).start()
                else:
                    cvzone.putTextRect(frame, "UNKNOWN", (max(0, x1), max(35, y1)), scale=0.6, thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                    maxx = max(0, x1)
                    maxy = max(35, y1)
                    point_block.append((maxx, maxy))
        if count <= 2:
            for xy in point_block:
                for xy2 in point_block_prv:
                    distance = math.hypot(xy2[0] - xy[0], xy2[1] - xy[1])
                    if distance < 25:
                        point_blocks[point] = xy
                        point += 1
        else:
            point_blocks_copy = point_blocks.copy()
            point_block_copy = point_block.copy()
            for points, xy2 in point_blocks_copy.items():
                obj_exist = False
                for xy in point_block_copy:
                    distance = math.hypot(xy2[0] - xy[0], xy[1] - xy[1])
                    if distance < 25:
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
            # cv2.putText(frame, f'ID:{str(points)}', (xy[0], xy[1]-7), 0, 0.5 , (0, 0, 255), 1)
            for box in boxes:
                person_count += 1

                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                conf = math.ceil(box.conf[0] * 100) / 100
                maxx = max(0, x1)
                maxy = max(35, y1)
                serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])

                if conf > 0.6:
                    if confs >= 100 and xy == (maxx, maxy):
                        threading.Thread(target=imwrite_thread,daemon=False).start()
                        if not thread_upload:
                            thread_upload = True
                            threading.Thread(target=upload_all_jpg_files_thread,daemon=True).start()
                        #train_model("datasets", "face", fs)
                        #name_list = get_id("datasets")
                        #recog = cv2.face.LBPHFaceRecognizer_create()
                        #recog.read("face.yml")
    point_block_prv = point_block.copy()


# use to detect people and face recognize then send data who are there
def detect_people(frame, model, recog, name_list, No_CCTV, bucket, org, token, url):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = model(frame, stream=True)
    thread_run = False
    def write_data_thread():
        nonlocal thread_run
        if thread_run:
            time.sleep(1)
            write_data(bucket, No_CCTV, "People_ID", org,
            token,
            url, str(name_list[serial]))
            thread_run = False
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
            conf = math.ceil(box.conf[0] * 100) / 100
            if conf > 0.6:
                if confs <= 100:
                    cvzone.putTextRect(frame, f'ID:{name_list[serial]}', (max(0, x1), max(35, y1)), scale=0.6,
                                       thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                    if not thread_run:
                        thread_run = True
                        threading.Thread(target=write_data_thread,daemon=False).start()
                else:
                    cvzone.putTextRect(frame, "UNKNOWN", (max(0, x1), max(35, y1)), scale=0.6, thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
    return frame

# detect and label the face
def detect_and_label_faces(frame, model, recog, name_list):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = model(frame, stream=True)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
            conf = math.ceil(box.conf[0] * 100) / 100
            if conf > 0.6:
                if confs <= 100:
                    cvzone.putTextRect(frame, f'ID: {name_list[serial]}', (max(0, x1), max(35, y1)),
                                       scale=0.6, thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                else:
                    cvzone.putTextRect(frame, "UNKNOWN", (max(0, x1), max(35, y1)),
                                       scale=0.6, thickness=1, offset=3)
                    cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
    return frame


# use to recognize what id of people in frame
def id_people(frame, model, recog, name_list):
    
    id = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = model(frame, stream=True)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
            conf = math.ceil(box.conf[0] * 100) / 100
            if conf > 0.6:
                if confs <= 100:
                    if name_list[serial] not in id:
                        id.append(name_list[serial])
    return str(id)

# Use in main CCTV camera to detect people and deep learn to recognize people
def front_face_detect_training(frame, facedetect, recog, name_list, point, person_count, count, point_blocks, point_block_prv, img, No_CCTV, bucket, org, token, url):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    point_block = []
    faces = facedetect.detectMultiScale(gray,1.3,5)
    
    def upload_all_jpg_files_thread():
        nonlocal thread_upload
        if thread_upload:
            #time.sleep(60)
            upload_file("datasets\\", "User." + str(points) + "." + str(person_count) + str(int(x)) + ".jpg", img)
            #upload_all_jpg_files("datasets",img)
            thread_upload = False

    def imwrite_thread():
        cv2.imwrite('datasets/User.' + str(points) + "." + str(person_count) + str(int(x)) + ".jpg", gray[y:y + h, x:x + w])
    
    def write_data_thread():
        nonlocal thread_runnings
        if thread_runnings:
            time.sleep(1)
            write_data(bucket,No_CCTV,"People_ID", org, token, url, str(name_list[serial]))
            thread_runnings = False

    thread_upload = False
    thread_runnings = False

    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y+h), (50, 50, 255), 1)
        serial, confs = recog.predict(gray[y:y + h, x:x + w])
        if confs <= 100:
            cvzone.putTextRect(frame, f'ID:{name_list[serial]}', (max(0, x), max(35, y)),
                                       scale=0.6, thickness=1, offset=3)
            cvzone.cornerRect(frame, (x, y, w, h), l=10)
            if not thread_runnings:
                thread_runnings = True
                threading.Thread(target=write_data_thread,daemon=False).start()
        else:
            cvzone.putTextRect(frame, "UNKNOWN", (max(0, x), max(35, y)), scale=0.6, thickness=1, offset=3)
            cvzone.cornerRect(frame, (x, y, w, h), l=10)
            maxx = max(0, x)
            maxy = max(35, y)
            point_block.append((maxx, maxy))
    if count <= 2:
        for xy in point_block:
            for xy2 in point_block_prv:
                distance = math.hypot(xy2[0] - xy[0], xy2[1] - xy[1])
                if distance < 25:
                    point_blocks[point] = xy
                    point += 1

    else:
        point_blocks_copy = point_blocks.copy()
        point_block_copy = point_block.copy()
        for points, xy2 in point_blocks_copy.items():
            obj_exist = False
            for xy in point_block_copy:
                distance = math.hypot(xy2[0] - xy[0], xy[1] - xy[1])
                if distance < 25:
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

        for (x,y,w,h) in faces:
            person_count += 1
            maxx = max(0, x)
            maxy = max(35, y)
            serial, confs = recog.predict(gray[y:y + h, x:x + w])

            if confs >= 100 and xy == (maxx, maxy):
                threading.Thread(target=imwrite_thread,daemon=False).start()
                if not thread_upload:
                    thread_upload = True
                    threading.Thread(target=upload_all_jpg_files_thread,daemon=False).start()    
    point_block_prv = point_block.copy()
    return frame,point_block_prv


# use to detect people and face recognize then send data who are there
def front_detect_people(frame, facedetect, recog, name_list, No_CCTV, bucket, org, token, url):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray,1.3,5)
    thread_run = False
    def write_data_thread():
        nonlocal thread_run
        if thread_run:
            time.sleep(1)
            write_data(bucket, No_CCTV, "People_ID", org,
            token,
            url, str(name_list[serial]))
            thread_run = False
    for (x,y,w,h) in faces:
        serial, confs = recog.predict(gray[y:y + h, x:x + w])
        if confs <= 100:
            cvzone.putTextRect(frame, f'ID:{name_list[serial]}', (max(0, x), max(35, y)), scale=0.6,
                                       thickness=1, offset=3)
            cvzone.cornerRect(frame, (x, y, w, h), l=10)
            if not thread_run:
                thread_run = True
                threading.Thread(target=write_data_thread,daemon=False).start()
            else:
                cvzone.putTextRect(frame, "UNKNOWN", (max(0, x), max(35, y)), scale=0.6, thickness=1, offset=3)
                cvzone.cornerRect(frame, (x, y, w, h), l=10)

def test_show(No_CCTV, address, fs, bucket, org, token, url, imgs, frame_rate):
    video = cv2.VideoCapture(address)
    if video.isOpened():
        check_face_yml_start(fs)
        recog = cv2.face.LBPHFaceRecognizer_create()
        recog.read("face.yml")
        count = 0
        num_cctv = "CCTV" + str(No_CCTV)
        model = YOLO('yolov8n-face.pt')
        def write_data_thread():
            nonlocal thread_running
            if thread_running:
                time.sleep(1)
                write_data(bucket, num_cctv, "People", org, token, url, num)
                thread_running = False
        thread_running = False
        while True:
            ret, frame = video.read()
            if ret:
                frame_rate += 1
                if frame_rate % 6 != 0:
                    continue
                check = check_face_yml_modified(fs)
                if check:
                    recog = cv2.face.LBPHFaceRecognizer_create()
                    recog.read("face.yml")
                    download_all_jpg_files(imgs, "datasets")
                frame = cv2.resize(frame, (1024, 620))
                name_list = get_id("datasets")
                count += 1
                # face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                results = model(frame, stream=True)
                thread_run = False
                def write_data_thread():
                    nonlocal thread_run
                    if thread_run:
                        time.sleep(1)
                        write_data(bucket, No_CCTV, "People_ID", org,
                        token,
                        url, str(name_list[serial]))
                        thread_run = False
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        w, h = x2 - x1, y2 - y1
                        serial, confs = recog.predict(gray[y1:y1 + h, x1:x1 + w])
                        conf = math.ceil(box.conf[0] * 100) / 100
                        if conf > 0.6:
                            if confs <= 100:
                                cvzone.putTextRect(frame, f'ID:{name_list[serial]}', (max(0, x1), max(35, y1)), scale=0.6,
                                                thickness=1, offset=3)
                                cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                                if not thread_run:
                                    thread_run = True
                                    threading.Thread(target=write_data_thread,daemon=False).start()
                            else:
                                cvzone.putTextRect(frame, "UNKNOWN", (max(0, x1), max(35, y1)), scale=0.6, thickness=1, offset=3)
                                cvzone.cornerRect(frame, (x1, y1, w, h), l=10)
                if not thread_running:
                    thread_running = True
                    num = count_people(model, frame)
                    threading.Thread(target=write_data_thread, daemon=False).start()
                
                yield frame
                

