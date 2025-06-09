from app import create_app
from app.models import db
from app.models.user import User
app = create_app()

# 当直接运行此脚本时
if __name__ == "__main__":
    # 创建数据库表
    with app.app_context():
        db.create_all()

        # 检查是否需要创建T-Admin

        tadmin = User.query.filter_by(email="tadmin@edba.example.com").first()
        if not tadmin:
            print("创建初始T-Admin账户...")
            tadmin = User(
                email="tadmin@edba.example.com",
                role="T-Admin"
            )
            tadmin.set_password("admin123")  # 默认密码，建议上线前修改
            db.session.add(tadmin)
            db.session.commit()
            print("T-Admin账户创建成功!")

    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)