# db_update.py
from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 添加 config_name 字段
        db.session.execute(
            text("ALTER TABLE api_configs ADD COLUMN config_name VARCHAR(100) NOT NULL DEFAULT '默认配置'"))
        print("添加 config_name 字段成功")

        # 添加 is_active 字段
        db.session.execute(text("ALTER TABLE api_configs ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))
        print("添加 is_active 字段成功")

        # 提交修改
        db.session.commit()
        print("数据库表修改完成!")

        # 更新现有数据
        db.session.execute(text("UPDATE api_configs SET config_name = '默认配置', is_active = TRUE"))
        db.session.commit()
        print("现有数据更新完成!")

    except Exception as e:
        db.session.rollback()
        print(f"错误: {str(e)}")