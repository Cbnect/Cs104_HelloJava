from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database.db"

# 1. ฟังก์ชันเชื่อมต่อฐานข้อมูล SQL
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # ช่วยให้เรียกข้อมูลด้วยชื่อคอลัมน์ได้ เช่น row['player_name']
    return conn

# 2. ฟังก์ชันสร้างตาราง และเพิ่ม Mock Data อัตโนมัติ (ตารางละ 10 Records รวม 50)
def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        setup_sql = """
        CREATE TABLE Teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT NOT NULL, region TEXT);
        CREATE TABLE Players (player_id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT NOT NULL, role TEXT, team_id INTEGER, FOREIGN KEY(team_id) REFERENCES Teams(team_id));
        CREATE TABLE Gears (gear_id INTEGER PRIMARY KEY AUTOINCREMENT, gear_type TEXT, brand TEXT, player_id INTEGER, FOREIGN KEY(player_id) REFERENCES Players(player_id));
        CREATE TABLE Tournaments (tournament_id INTEGER PRIMARY KEY AUTOINCREMENT, tourney_name TEXT, prize_pool INTEGER);
        CREATE TABLE Results (result_id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, team_id INTEGER, placement INTEGER, FOREIGN KEY(tournament_id) REFERENCES Tournaments(tournament_id), FOREIGN KEY(team_id) REFERENCES Teams(team_id));

        -- Insert Teams (10)
        INSERT INTO Teams (team_name, region) VALUES ('T1', 'Korea'), ('Paper Rex', 'APAC'), ('Sentinels', 'Americas'), ('Fnatic', 'EMEA'), ('LOUD', 'Americas'), ('DRX', 'Korea'), ('ZETA DIVISION', 'Japan'), ('Talon Esports', 'APAC'), ('Team Liquid', 'EMEA'), ('NRG', 'Americas');
        -- Insert Players (10)
        INSERT INTO Players (player_name, role, team_id) VALUES ('Faker', 'Mid', 1), ('Oner', 'Jungle', 1), ('f0rsakeN', 'Flex', 2), ('something', 'Duelist', 2), ('TenZ', 'Duelist', 3), ('zekken', 'Flex', 3), ('Boaster', 'Controller', 4), ('Derke', 'Duelist', 4), ('aspas', 'Duelist', 5), ('stax', 'Initiator', 6);
        -- Insert Gears (10)
        INSERT INTO Gears (gear_type, brand, player_id) VALUES ('Mouse', 'Logitech', 1), ('Keyboard', 'Razer', 1), ('Mouse', 'Zowie', 2), ('Headset', 'HyperX', 3), ('Mouse', 'Finalmouse', 4), ('Keyboard', 'Wooting', 5), ('Mouse', 'Logitech', 6), ('Monitor', 'Zowie', 7), ('Mouse', 'Razer', 8), ('Keyboard', 'Corsair', 9);
        -- Insert Tournaments (10)
        INSERT INTO Tournaments (tourney_name, prize_pool) VALUES ('Worlds 2023', 2225000), ('VCT Champions 2023', 2250000), ('VCT Masters Tokyo', 1000000), ('IEM Cologne', 1000000), ('The International 2023', 3000000), ('EWC 2024', 5000000), ('VCT LOCK//IN', 500000), ('BLAST Premier', 425000), ('MSI 2024', 250000), ('ALGS Championship', 2000000);
        -- Insert Results (10)
        INSERT INTO Results (tournament_id, team_id, placement) VALUES (1, 1, 1), (2, 2, 2), (2, 3, 1), (3, 4, 1), (2, 5, 3), (3, 2, 3), (7, 4, 1), (7, 5, 2), (2, 6, 5), (3, 9, 5);
        """
        conn.executescript(setup_sql)
        conn.commit()
        conn.close()
        print("สร้าง Database และ Mock Data สำเร็จแล้ว!")

# 3. ROUTE: หน้าแรก แสดงผลข้อมูล (Read) พร้อมดึงชื่อทีมมาร่วมด้วย (JOIN)
@app.route('/')
def index():
    conn = get_db_connection()
    # ใช้ INNER JOIN หรือ LEFT JOIN เพื่อผูกข้อมูล Players เข้ากับ Teams
    players = conn.execute('''
        SELECT Players.player_id, Players.player_name, Players.role, Teams.team_name 
        FROM Players 
        LEFT JOIN Teams ON Players.team_id = Teams.team_id
    ''').fetchall()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('index.html', players=players, teams=teams)

# 4. ROUTE: เพิ่มข้อมูลนักแข่ง (Create)
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    role = request.form['role']
    team_id = request.form['team_id']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO Players (player_name, role, team_id) VALUES (?, ?, ?)', (name, role, team_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index')) # อัปเดตเสร็จแล้วสั่งดีดกลับหน้าแรกทันทีเพื่อดึงข้อมูลใหม่

# 5. ROUTE: แก้ไขข้อมูลนักแข่ง (Update)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        team_id = request.form['team_id']
        
        conn.execute('UPDATE Players SET player_name = ?, role = ?, team_id = ? WHERE player_id = ?', (name, role, team_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # ถ้าเป็น GET ให้ดึงข้อมูลเก่ามาแสดงในฟอร์มแก้ไข
    player = conn.execute('SELECT * FROM Players WHERE player_id = ?', (id,)).fetchone()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('edit.html', player=player, teams=teams)

# 6. ROUTE: ลบข้อมูลนักแข่ง (Delete)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Players WHERE player_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db() # ตรวจสอบฐานข้อมูลตอนรันแอป
    app.run(debug=True)