import math


def count_people(model, frame):
    results = model(frame, stream=True)
    for r in results:
        countclass = []
        boxes = r.boxes  
        for box in boxes:           
            #Bounding box
            #x1, y1, x2, y2 = box.xyxy[0]
            #x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            #w, h = x2-x1, y2-y1
            #confidence
            conf = math.ceil(box.conf[0]*100)/100
            cls = int(box.cls[0])
            if conf> 0.65:
                countclass.append(cls)
        num=countclass.count(0)
    return num

"""def count_people(model, frame):
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                "teddy bear", "hair drier", "toothbrush"]
    results = model(frame, stream=True)
    for r in results:
        countclass = []
        boxes = r.boxes      
        for box in boxes:           
            #Bounding box
            #x1, y1, x2, y2 = box.xyxy[0]
            #x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            #w, h = x2-x1, y2-y1
            #confidence
            conf = math.ceil(box.conf[0]*100)/100
            cls = int(box.cls[0])
            currentclass = classNames[cls]
            if currentclass == "person" and conf > 0.6:              
                countclass.append(currentclass)
        num=countclass.count('person')

    return num"""
"""video = cv2.VideoCapture("rtsp://admin:abc12345@192.168.1.64/Streaming/Channels/101")
model = YOLO('yolov8n-face.pt')
while True:
    ret, frame = video.read()
    results = model(frame, stream=True)
    for r in results:
        countclass = []
        boxes = r.boxes  
        for box in boxes:           
            #Bounding box
            #x1, y1, x2, y2 = box.xyxy[0]
            #x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            #w, h = x2-x1, y2-y1
            #confidence
            conf = math.ceil(box.conf[0]*100)/100
            cls = int(box.cls[0])
            countclass.append(cls)
        num=countclass.count(0)
    print(num)"""
            
