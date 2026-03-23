from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename  # 新增：處理上傳檔案名稱，避免危險字元
from inference.generate import generate_reply
from database import get_db, init_db
import os
import bcrypt



app = Flask(__name__)
CORS(app)  # 允許前端跨來源連線

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


# 首頁
@app.route('/')
def home():
    return "Flask 後端正在運行"  # 回傳 HTML


#模型連接API
@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.json["message"]
    reply = generate_reply(user_text)
    return jsonify({"reply":reply})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~註冊與登入~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

####註冊####
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                      (email, hashed.decode("utf-8")))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "註冊成功"})
    except:
        return jsonify({"status": "error", "message": "此 email 已被註冊"}), 400



####登入####
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"status": "success", "message": "登入成功", "user_id": user["id"], "email": email})
    else:
        return jsonify({"status": "error", "message": "帳號或密碼錯誤"}), 401





'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~使用者日記顯示管理~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

###每天的照顧日記，一株植物可以有很多筆###
###記錄每天的照顧狀況###

#儲存植物日記
@app.route("/api/saveRecord", methods=["POST"])
def save_record():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO plant_records (email, date, day, img, plant_Name, text, weather)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data.get("email"), data.get("date"), data.get("day"),
          data.get("img"),  data.get("plant_Name"), data.get("text"), data.get("weather")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "紀錄已儲存"})



# 取得所有日記
@app.route("/api/records", methods=["GET"])
def get_records():
    email = request.args.get("email")
    plant_name = request.args.get("plant_name")
    conn = get_db()
    cursor = conn.cursor()

    if plant_name and email:
        # 查特定使用者的特定植物日記
        cursor.execute("SELECT * FROM plant_records WHERE email = ? AND plant_name = ?", (email, plant_name))
    elif email:
        # 查特定使用者的所有日記
        cursor.execute("SELECT * FROM plant_records WHERE email = ?", (email,))
    else:
        # 查全部
        cursor.execute("SELECT * FROM plant_records")

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)



#刪除日記API
#讓使用者可以刪掉自己不要的植物日記
@app.route("/api/deleteRecord/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plant_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "紀錄已刪除"})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~植物相關功能~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

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


# 植物建議
@app.route("/api/plantTalk", methods=["POST"])
def plant_talk():
    data = request.json
    day = int(data.get("day", 0))
    water_times = int(data.get("water_times", 0))
    symptoms = data.get("symptoms", [])
    flower = data.get("flower")
    fruit = data.get("fruit")
    stage = get_tomato_stage(day)

    if "葉片枯萎" in symptoms:
        plant_message = "我今天有點不太舒服，葉子感覺有點渴...( ´•̥̥̥ω•̥̥̥` )"
    elif "葉片發黃" in symptoms:
        plant_message = "我今天有幾片葉子變黃了，希望沒有生病(◞‸◟)"
    elif water_times == 0:
        plant_message = "我今天有點口渴，你都沒有給喝水!! (╬☉д⊙)"
    else:
        plant_message = "我今天感覺還不錯，正在努力長大！ヽ(●´∀`●)ﾉ"

    # 用 AI 生成建議
    prompt = f"""
    
    
    你是一個專業又溫暖的植物照顧助理，同時也是使用者的陪伴夥伴。
    請根據以下資訊，用溫暖親切的語氣回應，包含：
    1. 一句關心使用者的陪伴話語
    2. 2到3點具體的植物照顧建議
    3. 一個與植物相關的小知識

    植物生長天數：{day} 天
    目前生長階段：{stage}
    今日澆水次數：{water_times} 次
    目前症狀：{', '.join(symptoms) if symptoms else '無'}
    是否開花：{'是' if flower else '否'}
    是否結果：{'是' if fruit else '否'}

    請使用繁體中文回覆。
    
    """
    
    ai_advice = generate_reply(prompt)

    return jsonify({
        "status": "success",
        "plantStage": stage,
        "plantMessage": plant_message,
        "aiAdvice": ai_advice
    })


'''

# 新增：智慧植物回覆 + AI建議
@app.route("/api/plantTalk", methods=["POST"])
def plant_talk():
    data = request.json
    day = int(data.get("day", 0))
    water_times = int(data.get("water_times", 0))
    symptoms = data.get("symptoms", [])
    flower = data.get("flower")
    fruit = data.get("fruit")

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

'''

# 上傳植物照片 API
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
        "filename": filename,
        "filepath": f"/uploads/{filename}"  # 回傳可存取的路徑
    })



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~植物管理（新增植物、命名、選類型）~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

'''
###管理使用者養了哪些植物###

# 新增植物
@app.route("/api/addPlant", methods=["POST"])
def add_plant():
    data = request.json
    user_id = data.get("user_id")
    name = data.get("name")          # 使用者自己命名，例如「小綠」
    species = data.get("species")    # 植物類型，例如「聖女番茄」
    start_date = data.get("start_date")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO plants (user_id, name, species, start_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, name, species, start_date))
    conn.commit()
    plant_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "植物已新增", "plant_id": plant_id})

# 取得使用者的所有植物
@app.route("/api/plants", methods=["GET"])
def get_plants():
    user_id = request.args.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE user_id = ?", (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

# 刪除植物
@app.route("/api/deletePlant/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "植物已刪除"})

'''


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~執行程式~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)  # debug 模式方便開發

