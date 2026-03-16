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

# ★新增：判斷聖女番茄生長階段
def get_tomato_stage(day):

    if day <= 10:
        return "發芽期"

    elif day <= 25:
        return "幼苗期"

    elif day <= 40:
        return "營養生長期"

    elif day <= 50:
        return "開花期"

    elif day <= 70:
        return "結果期"

    else:
        return "成熟期"

# ★新增：智慧植物回覆 + AI建議
@app.route("/api/plantTalk", methods=["POST"])
def plant_talk():

    data = request.json

   day = int(data.get("day", 0))
   water_times = int(data.get("water_times", 0))
   symptoms = data.get("symptoms", [])
   flower = data.get("flower")
   fruit = data.get("fruit")
   sunlight = data.get("sunlight_hours")

    # ---------- 判斷植物生長階段 ----------
    stage = get_tomato_stage(day)

    # ---------- 智慧植物今日回覆 ----------
    plant_message = ""

    if "葉片枯萎" in symptoms:
        plant_message = " 我今天有點不太舒服，葉子感覺有點渴...( ´•̥̥̥ω•̥̥̥` )"

    elif "葉片發黃" in symptoms:
        plant_message = " 我今天有幾片葉子變黃了，希望沒有生病(◞‸◟)"

    elif water_times == 0:
        plant_message = " 我今天有點口渴，你都沒有給喝水!! (╬☉д⊙) "

    else:
        plant_message = " 我今天感覺還不錯，正在努力長大！ヽ(●´∀`●)ﾉ"


    # ---------- AI建議 ----------
    ai_advice = ""

    if "葉片發黃" in symptoms:

        ai_advice = f"""
AI建議：
目前植物處於{stage}，
葉片出現發黃情況，
可能與水分或養分不足有關。

建議：
1. 檢查最近澆水是否足夠
2. 若天氣晴朗可增加日照
3. 觀察是否持續擴散
"""

    elif "葉片枯萎" in symptoms:

        ai_advice = f"""
AI建議：
目前植物處於{stage}，
葉片出現枯萎情況，
可能與缺水或高溫有關。

建議：
1. 適量增加澆水
2. 避免正午強光
3. 保持土壤濕度穩定
"""

    elif water_times == 0:

        ai_advice = f"""
AI建議：
目前植物處於{stage}，
今日沒有澆水。

建議：
1. 視天氣情況適量補充水分
2. 保持每日穩定澆水習慣
"""

    elif stage == "開花期" and flower == False:

        ai_advice = f"""
AI建議：
目前植物理論上已接近開花期，
若尚未開花可能與光照或養分有關。

建議：
1. 增加日照時間
2. 保持穩定水分
"""

    elif stage == "結果期" and fruit == False:

        ai_advice = f"""
AI建議：
目前植物應逐漸進入結果期，
若尚未結果可以持續觀察。

建議：
1. 保持充足日照
2. 適量補充養分
"""

    else:

        ai_advice = f"""
AI建議：
目前植物處於{stage}，
整體狀況看起來穩定。

建議：
1. 維持規律澆水
2. 保持充足日照
3. 持續觀察葉片與生長情況
"""


    return jsonify({

        "status": "success",

        "plantStage": stage,

        "plantMessage": plant_message,

        "aiAdvice": ai_advice

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

