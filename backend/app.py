from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)  # 允許前端跨來源連線

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#登入 API
@app.route("/api/login", methods=["POST"])
def login():

    data = request.json
    email = data.get("email")
    password = data.get("password")

    # 先假裝登入成功
    return jsonify({
        "status": "success",
        "message": "登入成功",
        "user": email
    })


#儲存植物紀錄
@app.route("/api/saveRecord", methods=["POST"])
def save_record():

    data = request.json

    date = data.get("date")
    record = data.get("record")
    mood = data.get("mood")
    growth = data.get("growth")

    return jsonify({
        "status": "success",
        "message": "紀錄已儲存",
        "data": {
            "date": date,
            "record": record,
            "mood": mood,
            "growth": growth
        }
    })

#AI 建議
@app.route("/api/aiAdvice", methods=["POST"])
def ai_advice():

    data = request.json

    record = data.get("record")
    mood = data.get("mood")
    growth = data.get("growth")

    advice = "植物狀況良好，建議保持穩定澆水與日照。"

    return jsonify({
        "status": "success",
        "advice": advice
    })


#上傳照片
@app.route("/api/uploadPhoto", methods=["POST"])
def upload_photo():

    if "photo" not in request.files:
        return jsonify({"error": "沒有照片"}), 400

    file = request.files["photo"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({
        "status": "success",
        "filename": file.filename
    })
    
    
# 首頁路由
@app.route('/')
def home():
    return "Flask 後端正在運行"  # 回傳 HTML

# API 範例：接收 GET 請求
@app.route('/api/hello', methods=['GET'])
def hello():
    name = request.args.get('name', 'World')
    return jsonify({"message": f"Hello, {name}!"})

# API 範例：接收 POST 請求
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json  # 假設前端送 JSON
    print(data)
    return jsonify({"status": "success", "received": data})

# 啟動 Flask 伺服器
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)  # debug 模式方便開發


