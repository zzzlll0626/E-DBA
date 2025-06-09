from flask import Flask, request, jsonify, send_file, make_response
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import random
import os
import base64

app = Flask(__name__)

# 创建PDF目录
PDF_DIR = "mock_pdfs"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# 模拟学生数据
STUDENT_DATA = [
    {
        "name": "Alice Huang",
        "id": "S20230001",
        "enroll": "2020",
        "grad": "2024",
        "gpa": 3.75,
        "photo": "alice.jpg"
    },
    {
        "name": "Brian Chen",
        "id": "S20230002",
        "enroll": "2019",
        "grad": "2023",
        "gpa": 3.6,
        "photo": "brian.jpg"
    },
    {
        "name": "Cindy Lin",
        "id": "S20230003",
        "enroll": "2021",
        "grad": "2025",
        "gpa": 3.9,
        "photo": "cindy.jpg"
    },
    {
        "name": "David Wang",
        "id": "S20230004",
        "enroll": "2020",
        "grad": "2024",
        "gpa": 3.8,
        "photo": "david.jpg"
    },
    {
        "name": "Emma Zhang",
        "id": "S20230005",
        "enroll": "2022",
        "grad": "2026",
        "gpa": 4.0,
        "photo": "emma.jpg"
    },
    {
        "name": "Frank Li",
        "id": "S20230006",
        "enroll": "2019",
        "grad": "2023",
        "gpa": 3.5,
        "photo": "frank.jpg"
    },
    {
        "name": "Grace Liu",
        "id": "S20230007",
        "enroll": "2021",
        "grad": "2025",
        "gpa": 3.7,
        "photo": "grace.jpg"
    },
    {
        "name": "Henry Wu",
        "id": "S20230008",
        "enroll": "2020",
        "grad": "2024",
        "gpa": 3.65,
        "photo": "henry.jpg"
    }
]

# 学生照片与身份的对应关系（简单示例）
# 实际情况中可能需要更复杂的验证算法
PHOTO_TO_STUDENT = {
    "alice.jpg": "S20230001",
    "brian.jpg": "S20230002",
    "cindy.jpg": "S20230003",
    "david.jpg": "S20230004",
    "emma.jpg": "S20230005",
    "frank.jpg": "S20230006",
    "grace.jpg": "S20230007",
    "henry.jpg": "S20230008"
}

# 模拟论文数据
THESIS_DATA = [
    {
        "title": "AI in Education and Learning Systems",
        "abstract": "这篇论文讨论了AI在教育和学习系统中的应用。",
        "content": "人工智能在教育领域的应用已经取得了显著进展。本文探讨了AI如何改变传统课堂教学，提高学习效率，以及个性化教育的发展前景。",
        "code": "AI2023001",
        "author": "张明",
        "publication_date": "2023-04-15"
    },
    {
        "title": "Blockchain Applications in University Records",
        "abstract": "这篇论文探讨了区块链在大学记录管理中的应用。",
        "content": "区块链技术为大学记录管理提供了安全透明的解决方案。本文分析了如何使用区块链进行学位认证、成绩单管理和学历验证，以减少欺诈并提高效率。",
        "code": "BC2023002",
        "author": "李华",
        "publication_date": "2023-05-22"
    },
    {
        "title": "IoT Security in Smart Campus",
        "abstract": "这篇论文讨论了智能校园中物联网安全的重要性。",
        "content": "随着物联网设备在校园中的广泛部署，安全问题变得越来越重要。本文分析了智能校园面临的安全挑战，并提出了适用于教育环境的安全框架和解决方案。",
        "code": "IOT2023003",
        "author": "王芳",
        "publication_date": "2023-06-10"
    },
    {
        "title": "Green Energy Solutions for Schools",
        "abstract": "这篇论文提出了学校绿色能源解决方案。",
        "content": "教育机构在推动可持续发展方面具有重要作用。本文探讨了学校如何实施绿色能源解决方案，从太阳能和风能利用到能源管理系统的部署，以减少碳足迹。",
        "code": "GE2023004",
        "author": "赵伟",
        "publication_date": "2023-07-05"
    },
    {
        "title": "Edge Computing for Classroom Analytics",
        "abstract": "这篇论文分析了边缘计算在教室分析中的应用。",
        "content": "边缘计算为实时教室数据分析提供了新的可能性。本文讨论了如何利用边缘设备收集和处理课堂互动数据，以优化教学方法和提高学生参与度。",
        "code": "EC2023005",
        "author": "刘强",
        "publication_date": "2023-08-18"
    },
    {
        "title": "Cloud-based Student Portfolios",
        "abstract": "这篇论文讨论了基于云的学生档案管理。",
        "content": "云计算为学生作品集管理提供了灵活和可扩展的解决方案。本文研究了云端学生档案的实施方法、隐私保护措施以及如何利用数据分析技术评估学生发展。",
        "code": "CSP2023006",
        "author": "陈静",
        "publication_date": "2023-09-02"
    }
]

# 全局银行账户数据 - 作为全局变量便于跨函数访问和修改
BANK_ACCOUNTS = [
    {
        "bank": "Global Education Bank",
        "name": "Campus Cash Cooperative",
        "account": "641387141765274",
        "password": "8799",
        "balance": 500
    },
    {
        "bank": "FutureLearn Federal Bank",
        "name": "Utopia Credit Union",
        "account": "670547811218584",
        "password": "9978",
        "balance": 500
    },
    {
        "bank": "Bank of Utopia",
        "name": "EdGrow Finance Co.",
        "account": "393077718917153",
        "password": "9217",
        "balance": 500
    },
    {
        "bank": "Global Education Bank",
        "name": "EdGrow Finance Co.",
        "account": "137070703603485",
        "password": "1851",
        "balance": 500
    },
    {
        "bank": "Global Education Bank",
        "name": "BrightMind Capital",
        "account": "265254690447221",
        "password": "4664",
        "balance": 500
    },
    {
        "bank": "Continental Scholars Bank",
        "name": "Scholars Advantage Trust",
        "account": "904622106460646",
        "password": "1962",
        "balance": 500
    }
]


# 辅助函数：根据账户信息查找账户
def find_account(bank, name, account, password=None):
    """查找匹配的银行账户"""
    for acc in BANK_ACCOUNTS:
        if (acc["bank"] == bank and acc["name"] == name and acc["account"] == account):
            # 如果提供了密码，则同时验证密码
            if password is None or acc["password"] == password:
                return acc
    return None


import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def generate_thesis_pdf(thesis):
    # 先用reportlab创建一个简单的PDF页面
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, thesis["title"])

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "Abstract:")
    c.drawString(50, 700, thesis["abstract"])

    c.setFont("Helvetica", 12)
    c.drawString(50, 670, "Content:")

    # 添加文本内容
    y_position = 650
    content_text = thesis["content"]
    for i in range(0, len(content_text), 80):
        line = content_text[i:i + 80]
        c.drawString(50, y_position, line)
        y_position -= 15

    c.save()

    # 移动指针到开始位置
    packet.seek(0)

    # 创建新的PDF并添加页面
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])

    # 最后写入到BytesIO对象
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)

    return output_stream


# 学生身份验证接口 - 增强版
@app.route('/hw/student/authenticate', methods=['POST'])
def student_authenticate():
    try:
        # 获取表单数据和文件
        data = {}

        # 处理表单字段
        for key in request.form:
            data[key] = request.form[key]

        student_name = data.get('name', '')
        student_id = data.get('id', '')

        # 处理照片文件
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                photo_filename = photo.filename
                # 在实际环境中，这里会保存文件并进行图像分析
                # 在模拟环境中，我们只记录照片文件名

        # 进行验证
        # 1. 检查学号是否存在
        student_exists = False
        correct_name = False
        photo_match = False

        for student in STUDENT_DATA:
            if student['id'] == student_id:
                student_exists = True
                if student['name'] == student_name:
                    correct_name = True
                break

        # 2. 验证照片与学生匹配（简化验证）
        if photo_filename:
            for key, value in PHOTO_TO_STUDENT.items():
                if key.lower() in photo_filename.lower() and value == student_id:
                    photo_match = True
                    break

        # 验证逻辑
        if student_exists and correct_name:
            if photo_filename:
                if photo_match:
                    # 所有信息都匹配
                    return jsonify({
                        "status": "success",
                        "message": "学生身份验证通过"
                    })
                else:
                    # 照片不匹配
                    return jsonify({
                        "status": "fail",
                        "message": "照片与学生信息不匹配"
                    })
            else:
                # 无照片，但姓名和学号匹配
                return jsonify({
                    "status": "success",
                    "message": "学生身份验证通过，但未提供照片"
                })
        else:
            # 学号不存在或姓名不匹配
            return jsonify({
                "status": "fail",
                "message": "学生信息验证失败，姓名或学号错误"
            })

    except Exception as e:
        # 处理异常
        return jsonify({
            "status": "error",
            "message": f"验证过程发生错误: {str(e)}"
        })


# 学生记录接口
@app.route('/hw/student/record', methods=['POST'])
def student_record():
    data = request.json
    name = data.get('name', '')
    student_id = data.get('id', '')

    # 查找学生数据
    for student in STUDENT_DATA:
        if student['id'] == student_id:
            return jsonify({
                "name": student["name"],
                "enroll_year": student["enroll"],
                "graduation_year": student["grad"],
                "gpa": student["gpa"]
            })

    # 如果找不到匹配的学生，返回模拟数据
    return jsonify({
        "name": name,
        "enroll_year": "2020",
        "graduation_year": "2024",
        "gpa": 3.5 + random.random() * 1.0  # 随机GPA: 3.5-4.5
    })


# 论文搜索接口 - 保持原有逻辑
@app.route('/hw/thesis/search', methods=['POST'])
def thesis_search():
    data = request.json
    keywords = data.get('keywords', '').lower()
    code = data.get('code', '')  # 获取code参数

    # 过滤包含关键词或代码的论文
    results = []
    for thesis in THESIS_DATA:
        # 根据您的要求，保持使用 and 条件
        if (keywords and (keywords in thesis['title'].lower() or keywords in thesis['abstract'].lower())) and \
                (code and code == thesis['code']):
            # 创建包含所有字段的结果对象
            result = {
                "title": thesis['title'],
                "abstract": thesis['abstract'],
                "code": thesis['code'],
                "author": thesis['author'],
                "publication_date": thesis['publication_date']
            }
            results.append(result)

    # 如果没有找到匹配的论文，返回一些随机论文
    if not results:
        sample_theses = random.sample(THESIS_DATA, min(2, len(THESIS_DATA)))
        for thesis in sample_theses:
            result = {
                "title": thesis['title'],
                "abstract": thesis['abstract'],
                "code": thesis['code'],
                "author": thesis['author'],
                "publication_date": thesis['publication_date']
            }
            results.append(result)

    return jsonify(results)


# 论文下载接口
@app.route('/hw/thesis/pdf', methods=['POST'])
def thesis_pdf():
    data = request.json
    title = data.get('title', '')

    # 查找对应的论文
    thesis = None
    for t in THESIS_DATA:
        if t['title'] == title:
            thesis = t
            break

    # 如果找不到论文，返回错误
    if not thesis:
        return jsonify({"error": "PDF not found for given title."})

    # 生成PDF
    pdf_buffer = generate_thesis_pdf(thesis)

    # 返回PDF文件，添加正确的头部
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{title.replace(" ", "_")}.pdf"'

    return response


# 银行认证接口
@app.route('/hw/bank/authenticate', methods=['POST'])
def bank_authenticate():
    data = request.json
    bank = data.get('bank', '')
    account_name = data.get('account_name', '')
    account_number = data.get('account_number', '')
    password = data.get('password', '')

    print(f"银行认证请求: {bank}, {account_name}, {account_number}, ******")

    # 验证账户信息
    account = find_account(bank, account_name, account_number, password)
    if account:
        print(f"账户认证成功: {account_name}")
        return jsonify({"status": "success"})

    # 简单模拟：如果密码是"1234"或账号以"1"结尾，则认证成功
    if password == "1234" or account_number.endswith("1"):
        print(f"特殊规则认证成功: {account_name}")
        return jsonify({"status": "success"})

    print(f"账户认证失败: {account_name}")
    return jsonify({"status": "fail"})


# 银行转账接口
@app.route('/hw/bank/transfer', methods=['POST'])
def bank_transfer():
    try:
        data = request.json
        print(f"收到转账请求: {data}")

        from_bank = data.get('from_bank', '')
        from_name = data.get('from_name', '')
        from_account = data.get('from_account', '')
        password = data.get('password', '')
        to_bank = data.get('to_bank', '')
        to_name = data.get('to_name', '')
        to_account = data.get('to_account', '')
        amount = float(data.get('amount', 0))

        # 记录转账信息
        transfer_log = f"从 {from_bank} 的 {from_name} " + \
                       f"转账 {amount} 元到 " + \
                       f"{to_bank} 的 {to_name}"
        print(f"模拟转账: {transfer_log}")

        # 简单模拟：如果金额大于100000，则转账失败
        if amount > 100000:
            print(f"转账失败: 金额 {amount} 超过限制")
            return jsonify({"status": "fail", "reason": "转账金额超过限制"})

        # 查找付款账户
        from_account_obj = find_account(from_bank, from_name, from_account, password)
        if not from_account_obj:
            print(f"转账失败: 付款账户不存在或密码错误")
            return jsonify({"status": "fail", "reason": "付款账户不存在或密码错误"})

        # 查找收款账户
        to_account_obj = find_account(to_bank, to_name, to_account)
        if not to_account_obj:
            print(f"转账失败: 收款账户不存在")
            return jsonify({"status": "fail", "reason": "收款账户不存在"})

        # 检查余额是否足够
        if from_account_obj["balance"] < amount:
            print(f"转账失败: 余额不足 (当前: {from_account_obj['balance']}, 需要: {amount})")
            return jsonify({"status": "fail", "reason": "余额不足"})

        # 执行转账
        from_account_obj["balance"] -= amount
        to_account_obj["balance"] += amount

        print(f"转账成功: {amount} 元")
        print(f"付款账户新余额: {from_account_obj['balance']}")
        print(f"收款账户新余额: {to_account_obj['balance']}")

        # 返回成功
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"转账过程中发生错误: {str(e)}")
        return jsonify({"status": "fail", "reason": f"处理错误: {str(e)}"})


# 添加一个简单的测试用接口，返回所有可用的学生列表
@app.route('/hw/students/list', methods=['GET'])
def list_students():
    simplified_list = []
    for student in STUDENT_DATA:
        simplified_list.append({
            "name": student["name"],
            "id": student["id"],
            "photo": student["photo"]
        })
    return jsonify(simplified_list)


# 银行余额查询接口
@app.route('/hw/bank/balance', methods=['POST'])
def bank_balance():
    data = request.json
    bank = data.get('bank', '')
    account_name = data.get('account_name', '')
    account_number = data.get('account_number', '')
    password = data.get('password', '')

    print(f"余额查询请求: {bank}, {account_name}, {account_number}, ******")

    # 查找账户
    account = find_account(bank, account_name, account_number, password)
    if account:
        print(f"余额查询成功: {account_name}, 余额: {account['balance']}")
        return jsonify({"status": "success", "balance": account["balance"]})

    # 如果未找到匹配账户
    print(f"余额查询失败: 账户不存在或密码错误")
    return jsonify({"status": "fail", "message": "账户信息验证失败"})


# 添加一个管理端点，用于查看所有银行账户状态
@app.route('/hw/admin/bank_accounts', methods=['GET'])
def admin_bank_accounts():
    accounts_info = []
    for account in BANK_ACCOUNTS:
        # 创建不包含密码的副本
        account_info = {
            "bank": account["bank"],
            "name": account["name"],
            "account": account["account"],
            "balance": account["balance"]
        }
        accounts_info.append(account_info)

    return jsonify(accounts_info)


if __name__ == '__main__':
    print("模拟服务器正在运行，地址: http://localhost:8001")
    print("提供以下API接口:")
    print("- /hw/student/authenticate - 学生身份验证")
    print("- /hw/student/record - 学生记录查询")
    print("- /hw/thesis/search - 论文搜索")
    print("- /hw/thesis/pdf - 论文PDF下载")
    print("- /hw/bank/authenticate - 银行账户验证")
    print("- /hw/bank/transfer - 银行转账")
    print("- /hw/bank/balance - 银行余额查询")
    print("- /hw/students/list - 获取学生列表(测试用)")
    print("- /hw/admin/bank_accounts - 查看所有银行账户状态(管理用)")

    app.run(host='0.0.0.0', port=8001, debug=True)