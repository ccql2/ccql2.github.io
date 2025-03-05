from flask import Flask, request, jsonify, session
from datetime import datetime, timedelta
import pymysql
import bcrypt
import random
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 设置一个安全的密钥

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'chili_wx',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 连接到数据库
def get_db_connection():
    return pymysql.connect(**db_config)

# 生成防伪码
def generate_anti_counterfeiting_code():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

# 检查账号是否被锁定
def is_account_locked(phone):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT locked_until FROM users WHERE phone = %s"
            cursor.execute(sql, (phone,))
            user = cursor.fetchone()
            if user and user['locked_until'] and user['locked_until'] > datetime.now():
                return True
        return False
    finally:
        connection.close()

# 增加登录失败次数
def increment_failed_attempts(phone):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE phone = %s"
            cursor.execute(sql, (phone,))
            if cursor.rowcount > 0:
                sql = "SELECT failed_attempts FROM users WHERE phone = %s"
                cursor.execute(sql, (phone,))
                user = cursor.fetchone()
                if user['failed_attempts'] >= 3:
                    sql = "UPDATE users SET locked_until = %s WHERE phone = %s"
                    cursor.execute(sql, (datetime.now() + timedelta(minutes=5), phone))
            connection.commit()
    finally:
        connection.close()

# 登录
@app.route('/login', methods=['POST'])
def login():
    phone = request.form['phone']
    password = request.form['password']
    if is_account_locked(phone):
        return jsonify({'status': 'error', 'message': '账号已锁定，请稍后再试'})

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE phone = %s"
            cursor.execute(sql, (phone,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                session['logged_in'] = True
                session['real_name'] = user['real_name']
                return jsonify({'status': 'success'})
            else:
                increment_failed_attempts(phone)
                return jsonify({'status': 'error', 'message': '用户名或密码错误'})
    finally:
        connection.close()

# 上传信息
@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': '请先登录'})

    region_name = request.form['region_name']
    region_image_url = request.form.get('region_image_url', '')
    fertilizers_used = request.form['fertilizers_used']
    farming_activities = request.form['farming_activities']
    watering_fertilizing_pesticide_logs = request.form['watering_fertilizing_pesticide_logs']
    harvest_image_url = request.form.get('harvest_image_url', '')
    drying_image_url = request.form.get('drying_image_url', '')
    operation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查是否已生成防伪码
            sql = "SELECT anti_counterfeiting_code FROM regions WHERE region_name = %s"
            cursor.execute(sql, (region_name,))
            region = cursor.fetchone()
            if not region or not region['anti_counterfeiting_code']:
                anti_counterfeiting_code = generate_anti_counterfeiting_code()
            else:
                anti_counterfeiting_code = region['anti_counterfeiting_code']

            # 更新或插入数据
            sql = """
            INSERT INTO regions (region_name, region_image_url, operator, operation_time, fertilizers_used, farming_activities, watering_fertilizing_pesticide_logs, harvest_image_url, drying_image_url, anti_counterfeiting_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            region_image_url = VALUES(region_image_url),
            operator = VALUES(operator),
            operation_time = VALUES(operation_time),
            fertilizers_used = VALUES(fertilizers_used),
            farming_activities = VALUES(farming_activities),
            watering_fertilizing_pesticide_logs = VALUES(watering_fertilizing_pesticide_logs),
            harvest_image_url = VALUES(harvest_image_url),
            drying_image_url = VALUES(drying_image_url)
            """
            cursor.execute(sql, (
                region_name, region_image_url, session.get('real_name'), operation_time,
                fertilizers_used, farming_activities, watering_fertilizing_pesticide_logs,
                harvest_image_url, drying_image_url, anti_counterfeiting_code
            ))
            connection.commit()
            return jsonify({'status': 'success'})
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)