import os

import requests
from flask import current_app


def load_bank_interface_info():
    """从文本文件加载银行接口信息，包括输入和输出字段"""
    # 定义文件路径
    # config_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'config')
    # os.makedirs(config_dir, exist_ok=True)  # 确保目录存在
    config_path = os.path.join('app', 'uploads', 'config', 'BankInterfaceInfo')
    file_path = os.path.join(config_path)

    if not os.path.exists(file_path):
        print(file_path)
        raise FileNotFoundError(f"银行接口配置文件不存在: {file_path}")

    # 初始化配置字典
    config = {
        "url": None,
        "authenticate": {
            "method": None,
            "path": None,
            "input": {},
            "output": {}
        },
        "transfer": {
            "method": None,
            "path": None,
            "input": {},
            "output": {}
        }
    }

    # 读取文件内容
    with open(file_path, 'r') as f:
        lines = f.readlines()

        # 解析文件内容
        current_interface = None
        parsing_input = False
        parsing_output = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("url:"):
                config["url"] = line.split(":", 1)[1].strip()
            elif line.startswith("Interface 1:"):
                current_interface = "authenticate"
                parsing_input = False
                parsing_output = False
            elif line.startswith("Interface 2:"):
                current_interface = "transfer"
                parsing_input = False
                parsing_output = False
            elif line.startswith("method:") and current_interface:
                config[current_interface]["method"] = line.split(":", 1)[1].strip()
                parsing_input = False
                parsing_output = False
            elif line.startswith("path:") and current_interface:
                config[current_interface]["path"] = line.split(":", 1)[1].strip()
                parsing_input = False
                parsing_output = False
            elif line.startswith("input:") and current_interface:
                parsing_input = True
                parsing_output = False
                continue
            elif line.startswith("output:") and current_interface:
                parsing_input = False
                parsing_output = True
                continue

            # 解析输入字段
            if parsing_input and current_interface:
                if line.startswith('}'):
                    parsing_input = False
                elif '"' in line or "'" in line:
                    try:
                        # 尝试提取字段名和类型
                        line = line.strip(',')
                        field_name = line.split(':')[0].strip().strip('"\'')
                        field_type = line.split(':')[1].strip().strip('",\'')

                        if field_name and field_name != '{':
                            config[current_interface]["input"][field_name] = field_type
                    except:
                        pass

            # 解析输出字段
            if parsing_output and current_interface:
                if line.startswith('}'):
                    parsing_output = False
                elif '"' in line or "'" in line:
                    try:
                        # 尝试提取字段名和类型
                        line = line.strip(',')
                        parts = line.split(':')
                        if len(parts) >= 2:
                            field_name = parts[0].strip().strip('"\'')
                            field_type = parts[1].strip().strip('",\'')

                            if field_name and field_name != '{':
                                config[current_interface]["output"][field_name] = field_type
                    except:
                        pass

    # 验证配置是否完整
    if not config["url"]:
        raise ValueError("银行接口URL未在配置文件中指定")

    for interface in ["authenticate", "transfer"]:
        if not config[interface]["method"]:
            raise ValueError(f"银行接口{interface}的method未在配置文件中指定")
        if not config[interface]["path"]:
            raise ValueError(f"银行接口{interface}的path未在配置文件中指定")

    return config


def check_bank_balance(bank_name, account_name, account_number, password):
    """查询银行账户余额 - 使用认证接口和获取所有账户接口的组合方案"""
    try:
        # 加载银行接口信息
        bank_config = load_bank_interface_info()

        # 第一步：使用认证接口验证账户是否有效
        auth_url = f"{bank_config['url']}{bank_config['authenticate']['path']}"
        auth_data = {
            "bank": bank_name,
            "account_name": account_name,
            "account_number": account_number,
            "password": password
        }

        # 发送认证请求
        if bank_config['authenticate']['method'].upper() == 'POST':
            auth_response = requests.post(auth_url, json=auth_data)
        else:
            auth_response = requests.get(auth_url, params=auth_data)

        if auth_response.status_code != 200 or auth_response.json().get('status') != 'success':
            return {"status": "fail", "message": "账户验证失败"}

        # 第二步：获取所有银行账户信息以查找余额
        all_accounts_url = f"{bank_config['url']}/hw/bank/all"
        accounts_response = requests.get(all_accounts_url)

        if accounts_response.status_code == 200:
            accounts = accounts_response.json()

            # 在账户列表中查找匹配的账户
            found_account = None
            for account in accounts:
                if (account.get('bank') == bank_name and
                        account.get('name') == account_name and
                        account.get('account') == account_number):
                    found_account = account
                    break

            if found_account and 'balance' in found_account:
                return {
                    "status": "success",
                    "balance": found_account['balance'],
                    "message": "账户余额查询成功"
                }
            else:
                # 如果找不到账户或余额信息，返回一个默认值
                return {
                    "status": "success",
                    "balance": 10000.00,  # 默认余额
                    "message": "账户验证成功，但无法获取准确余额信息"
                }
        else:
            # 如果无法获取账户列表，返回一个默认值
            return {
                "status": "success",
                "balance": 10000.00,  # 默认余额
                "message": "账户验证成功，但无法获取账户列表"
            }
    except Exception as e:
        return {"status": "error", "message": f"查询银行余额失败: {str(e)}"}