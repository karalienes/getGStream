import cv2
import sys
from flask import Flask, render_template, Response

app = Flask(__name__)


def gen_frames():
    print(cv2.getBuildInformation())

    # H264 we get some latency video = cv2.VideoCapture("udpsrc port=5000 ! application/x-rtp,payload=96,
    # encoding-name=H264 ! rtpjitterbuffer mode=1 ! rtph264depay ! h264parse ! decodebin ! videoconvert ! appsink",
    # cv2.CAP_GSTREAMER)

    # Fastest stream JPEG with RTP
    video = cv2.VideoCapture(
        "udpsrc port=5000 ! application/x-rtp, media=video, encoding-name=JPEG, framerate=30/1, payload=26, "
        "clock-rate=90000 ! rtpjpegdepay ! jpegdec ! videoconvert ! appsink",
        cv2.CAP_GSTREAMER)

    if not video.isOpened():
        print("Could not open Video")
        sys.exit()

    while True:
        success, frame = video.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    video.release()
    cv2.destroyAllWindows()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
