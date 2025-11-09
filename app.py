from flask import Flask, request, jsonify, send_from_directory
from google.cloud import speech_v1p1beta1 as speech
from google.api_core.exceptions import GoogleAPIError
import os
import io

# -------------------- Firebase Firestore Setup (Not used in this version, kept for future expansion) --------------------
# 由於這是一個語音辨識練習的單機應用程式，我們暫時不需要 Firestore。

# -------------------- Flask Application and Google Cloud Configuration --------------------
app = Flask(__name__)

# 設置 Google 憑證檔案路徑
import json

if os.path.exists('credentials.json'):
    # 本地開發
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
else:
    # 雲端部署
    credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
    if credentials_json:
        with open('/tmp/credentials.json', 'w') as f:
            f.write(credentials_json)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'

# 初始化 Google Cloud Speech Client
try:
    # 使用 v1p1beta1 才能訪問更高級的語音模型和功能（如標點符號）
    client = speech.SpeechClient()
    print("Google Cloud Speech Client 初始化成功。")
except Exception as e:
    print(f"建立語音辨識客戶端時發生錯誤：{e}")
    client = None

# -------------------- Routes (路由) --------------------

@app.route('/')
def serve_index():
    """服務主頁面 (index.html)"""
    # 確保 app.py 和 index.html 在同一目錄下
    return send_from_directory('.', 'index.html')

@app.route('/recognize', methods=['POST'])
def recognize_audio():
    """處理音訊檔案並進行語音辨識"""
    if not client:
        return jsonify({'error': '伺服器錯誤，無法連接 Google Cloud Speech API。請檢查金鑰設定。'}), 500

    # 檢查請求中是否包含音訊檔案
    if 'audio' not in request.files:
        return jsonify({'error': '沒有上傳音訊檔案'}), 400

    audio_file = request.files['audio']
    content = audio_file.read()

    # 設置 Google Cloud Speech API 的配置
    audio = speech.RecognitionAudio(content=content)
    
    # WEBM_OPUS 是 MediaRecorder 錄製的格式，必須指定
    # sample_rate_hertz=48000 是瀏覽器常見的取樣率
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code='zh-TW',  # 指定為台灣中文
        # 啟用自動標點符號功能，使辨識結果更為準確和完整
        enable_automatic_punctuation=True,
    )

    try:
        # 進行同步語音辨識
        response = client.recognize(config=config, audio=audio)
        
        recognized_text = ""
        # 遍歷所有結果，將多個語音片段串接起來
        for result in response.results:
            # 取得最佳的替代選項
            recognized_text += result.alternatives[0].transcript
        
        # 返回 JSON 格式的辨識結果
        return jsonify({'text': recognized_text})
        
    except GoogleAPIError as e:
        print(f"Google API 錯誤：{e}")
        return jsonify({'error': f'Google Cloud Speech API 錯誤: {e.message}'}), 500
    except Exception as e:
        print(f"處理語音辨識時發生未知錯誤：{e}")
        return jsonify({'error': '處理語音辨識時發生未知錯誤。'}), 500

# -------------------- 伺服器啟動點 (新增的關鍵部分) --------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
