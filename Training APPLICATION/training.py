from PyQt5 import QtCore, QtGui, QtWidgets
from trainingmodel import train_model_online
from MongoDB_client import mongo_connect
import sys
import yaml
import gridfs
import time
from PIL import Image


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(244, 90)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 10, 141, 51))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "TRAINING......"))

class TrainingThread(QtCore.QThread):
    def __init__(self, path, model_names, fs, imgs, label):
        super().__init__()
        self.path = path
        self.model_names = model_names
        self.fs = fs
        self.imgs = imgs
        self.label = label
        self.running = True

    def run(self):
        while self.running:
            train_model_online(self.path, self.model_names, self.fs, self.imgs)
            self.label.setText("Train Success")
            time.sleep(5)
            self.label.setText("Training.....")
            time.sleep(55) 

    def stop(self):
        self.running = False

def resize_image(file_path, new_width, new_height):
    # Open the image file
    image = Image.open(file_path)

    # Resize the image
    resized_image = image.resize((new_width, new_height))

    # Overwrite the original image file
    resized_image.save(file_path)


if __name__ == "__main__":
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)

    connect_str = config['mongodb']['connect_str']
    client = mongo_connect(connect_str)
    db = client.facemodel
    collection_name = config['mongodb']['collection_name']
    img_name = config['mongodb']['img_name']
    fs = gridfs.GridFS(db, collection=collection_name)
    imgs = gridfs.GridFS(db, collection=img_name)
    path = config['path']
    model_names = config['names']
    frame_rate = 0
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    label = ui.label
    training_thread = TrainingThread(path, model_names, fs, imgs, label)
    training_thread.start()

    app.aboutToQuit.connect(training_thread.stop)  # Connect stop method to application closing

    sys.exit(app.exec_())
