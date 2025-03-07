import pymysql
from datetime import datetime
import qrcode
import os
import hashlib

# 数据库连接参数
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'chili_wx',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 连接到数据库
connection = pymysql.connect(**db_config)

# 生成防伪码（哈希值）
def generate_anti_counterfeiting_code(data):
    data_str = str(data)
    hash_object = hashlib.sha256(data_str.encode())
    return hash_object.hexdigest()

try:
    with connection.cursor() as cursor:
        # 查询表中的数据（这里假设只有一条记录作为示例）
        sql = "SELECT * FROM chili_6pq LIMIT 1"
        cursor.execute(sql)
        record = cursor.fetchone()

        # 提取记录中的关键信息
        region_name = record['region_name'] if record else '第六片区'
        region_image_url = record['region_image_url'] if record else ''
        operator = record['operator'] if record else '刘十三'
        operation_time = record['operation_time'] if record else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        region_leader = record['region_leader'] if record else '高十四'
        fertilizers_used = record['fertilizers_used'] if record else '尿素,钙镁磷肥'
        farming_activities = record['farming_activities'] if record else '修剪枝叶'
        watering_fertilizing_pesticide_logs = record['watering_fertilizing_pesticide_logs'] if record else '2023-04-15 09:00 刘十三修剪; 2023-04-30 15:00 高十四清理落叶'
        harvest_time = record.get('harvest_time', '未知')
        drying_time = record.get('drying_time', '未知')

        # 生成防伪码（哈希值）
        anti_counterfeiting_code = generate_anti_counterfeiting_code(record)

        # 生成HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>椒口称赞-防伪溯源查询中心</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    width: 90%;
                    max-width: 400px; /* 调整为适合手机屏幕的宽度 */
                    margin: 50px auto;
                    background-color: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                }}
                .info-section {{
                    margin-bottom: 20px;
                }}
                .info-section label, .info-section span {{
                    display: block;
                }}
                .info-section label {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .highlight {{
                    font-size: 20px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                    word-wrap: break-word; /* 自动换行 */
                    overflow-wrap: break-word; /* 自动换行 */
                }}
                .info-section .boxed {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 5px 0;
                    background-color: #ffe4e6;
                    border: 1px solid #ffcccc;
                    border-radius: 10px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                .image-button {{
                    display: block;
                    text-align: right;
                    margin-top: -20px; /* 调整按钮位置 */
                }}
                .image-button button {{
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    cursor: pointer;
                }}
                .hidden-image {{
                    display: none;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- 突出显示防伪码 -->
                <div class="highlight">防伪码: {anti_counterfeiting_code}</div>
                <h1>椒口称赞-防伪溯源查询中心</h1>
                <div class="info-section">
                    <img src="https://pic.vjshi.com/2023-05-26/cdbd0139cf4b4cbe87c6f89d46741446/online/main.jpg?x-oss-process=style/w342_h192_center" alt="辣椒图片" style="width:100%;">
                </div>
                <div class="info-section">
                    <label>所属片区:</label>
                    <span>{region_name} </span>
                    <div class="image-button">
                        <button onclick="toggleImage()">点击查看片区图片</button>
                    </div>
                    <div class="hidden-image" id="regionImage">
                        <img src="{region_image_url}" alt="{region_name} 图片">
                    </div>
                </div>
                <div class="info-section">
                    <label>负责人:</label>
                    <span>{operator}</span>
                </div>
                <div class="info-section">
                    <label>操作时间:</label>
                    <span>{operation_time}</span>
                </div>
                <div class="info-section">
                    <label>区域负责人:</label>
                    <span>{region_leader}</span>
                </div>
                <div class="info-section">
                    <label>使用的肥料:</label>
                    <span class>{fertilizers_used}</span>
                </div>
                <div class="info-section">
                    <label>农事活动:</label>
                    <span class>{farming_activities}</span>
                </div>
                <div class="info-section">
                    <label>浇水施肥打药记录:</label>
                    <div>
                    {(', ').join([f'<span class=>{log}</span>' for log in watering_fertilizing_pesticide_logs.split('; ')])}
                    </div>
                </div>
                <div class="info-section">
                    <label>收割时间:</label>
                    <span>{harvest_time}</span>
                </div>
                <div class="info-section">
                    <label>晾晒时间:</label>
                    <span>{drying_time}</span>
                </div>
            </div>

            <script>
                function toggleImage() {{
                    var img = document.getElementById('regionImage');
                    if (img.style.display === 'none' || img.style.display === '') {{
                        img.style.display = 'block';
                    }} else {{
                        img.style.display = 'none';
                    }}
                }}
            </script>
        </body>
        </html>
        """

        # 生成HTML文件名
        html_file_name = "../templates/sixth_chili.html"
        html_file_path = os.path.join(os.getcwd(), html_file_name)

        # 将HTML内容保存到文件中
        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"HTML 文件已生成: {html_file_path}")

        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"http://110.41.56.99/{html_file_name}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_file_name = "sixth_chili_qr.png"
        qr_file_path = os.path.join(os.getcwd(), qr_file_name)
        qr_img.save(qr_file_path)
        print(f"二维码已生成: {qr_file_path}")

finally:
    connection.close()