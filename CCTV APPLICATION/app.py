from flask import Flask, render_template, Response, request, redirect, url_for,jsonify
import cv2
import yaml


from yolo_video import video_detection,video_detection_main
app = Flask(__name__)
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

address = config['address']

camera = cv2.VideoCapture(address)
selected_condition = ""

def generate_frames_main():
    yolo_outputs = video_detection_main(address)
    for detections in yolo_outputs:
        ret, buffers = cv2.imencode('.jpg', detections)
        frames = buffers.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frames + b'\r\n')

def generate_frames_general():
    yolo_output = video_detection(address)
    for detection in yolo_output:
        ret, buffer = cv2.imencode('.jpg', detection)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global selected_condition
    selected_condition = request.form.get('condition')
    return redirect(url_for('video'))

@app.route('/video')
def video():
    global selected_condition
    if selected_condition:
        return render_template('video.html', condition=selected_condition)
    else:
        return redirect(url_for('index'))

@app.route('/stream')
def stream():
    global selected_condition
    if selected_condition == 'main':
        return Response(generate_frames_main(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif selected_condition == 'general':
        return Response(generate_frames_general(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response('', mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == "__main__":
    app.run(debug=True)
