from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database.db"

# ฟังก์ชันเชื่อมต่อ Database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้างและจำลองข้อมูลตอนเริ่มต้น
def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        # นำคำสั่ง SQL ด้านบนมาใส่ตรงนี้ (ย่อไว้เพื่อความกระชับในโค้ด)
        setup_sql = """
        CREATE TABLE Teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT NOT NULL, region TEXT);
        CREATE TABLE Players (player_id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT NOT NULL, role TEXT, team_id INTEGER, FOREIGN KEY(team_id) REFERENCES Teams(team_id));
        -- (สร้างตารางอื่นๆ และ INSERT ข้อมูลเหมือนด้านบน)
        INSERT INTO Teams (team_name, region) VALUES ('T1', 'Korea'), ('Paper Rex', 'APAC');
        INSERT INTO Players (player_name, role, team_id) VALUES ('Faker', 'Mid', 1), ('f0rsakeN', 'Flex', 2);
        """
        conn.executescript(setup_sql)
        conn.commit()
        conn.close()

# Route หน้าหลัก (Read)
@app.route('/')
def index():
    conn = get_db_connection()
    # ดึงข้อมูลผู้เล่นพร้อมชื่อทีม (JOIN)
    players = conn.execute('''
        SELECT Players.player_id, Players.player_name, Players.role, Teams.team_name 
        FROM Players 
        LEFT JOIN Teams ON Players.team_id = Teams.team_id
    ''').fetchall()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('index.html', players=players, teams=teams)

# Route เพิ่มข้อมูล (Create)
@app.route('/add', methods=('POST',))
def add():
    name = request.form['name']
    role = request.form['role']
    team_id = request.form['team_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO Players (player_name, role, team_id) VALUES (?, ?, ?)', (name, role, team_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route ลบข้อมูล (Delete)
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Players WHERE player_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db() # เรียกใช้เพื่อสร้าง DB อัตโนมัติ
    app.run(debug=True)