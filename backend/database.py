import sqlite3

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # 讓結果可以用欄位名稱存取
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 修改：建立植物紀錄資料表
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS plant_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            record TEXT,
            mood TEXT,
            growth TEXT,
            photo_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # 儲存變更
    conn.commit()

    # 關閉資料庫連線
    conn.close()

init_db()  # 新增：啟動程式時建立資料表