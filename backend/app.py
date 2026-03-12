from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename  # ★新增：處理上傳檔案名稱，避免危險字元
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 允許前端跨來源連線

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 首頁路由
@app.route('/')
def home():
    return "Flask 後端正在運行"  # 回傳 HTML


# API 範例：接收 GET 請求
@app.route('/api/hello', methods=['GET'])
def hello():
    name = request.args.get('name', 'World')
    return jsonify({"message": f"Hello, {name}!"})


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

    # 取得前端傳來的 JSON 資料
    data = request.json

    date = data.get("date")
    record = data.get("record")
    mood = data.get("mood")
    growth = data.get("growth")

    # ★新增：連接資料庫
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ★新增：將資料存入資料庫
    cursor.execute("""
        INSERT INTO plant_records (date, record, mood, growth)
        VALUES (?, ?, ?, ?)
    """, (date, record, mood, growth))

    # 儲存變更
    conn.commit()

    # 關閉資料庫
    conn.close()

    # 回傳成功訊息給前端
    return jsonify({
        "status": "success",
        "message": "紀錄已儲存"
    })

def init_db():
    # 連接 SQLite 資料庫
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ★修改：建立植物紀錄資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plant_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        record TEXT,
        mood TEXT,
        growth TEXT
    )
    """)

    # 儲存變更
    conn.commit()

    # 關閉資料庫連線
    conn.close()

init_db()  # ★新增：啟動程式時建立資料表


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
# 上傳植物照片 API
@app.route("/api/uploadPhoto", methods=["POST"])
def upload_photo():

    # 如果沒有照片欄位
    if "photo" not in request.files:
        return jsonify({"error": "沒有照片"}), 400

    file = request.files["photo"]

    # 使用 secure_filename 避免危險檔名
    filename = secure_filename(file.filename)

    # 設定儲存路徑
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 儲存檔案
    file.save(filepath)

    return jsonify({
        "status": "success",
        "filename": file.filename
    })


# 啟動 Flask 伺服器
@app.route("/api/records", methods=["GET"])

def get_records():

    # 連接資料庫
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 查詢所有紀錄
    cursor.execute("SELECT * FROM plant_records")

    # 取得查詢結果
    rows = cursor.fetchall()

    # 關閉資料庫
    conn.close()

    # 將資料回傳給前端
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)  # debug 模式方便開發

