from app import create_app
from app.models import db
from app.models.payment import MembershipFee
from app.models.user import User

app = create_app()

with app.app_context():
    # 删除所有表
    db.drop_all()

    # 重新创建所有表
    db.create_all()

    # 创建T-Admin账户
    tadmin = User(
        email="tadmin@edba.example.com",
        role="T-Admin"
    )
    tadmin.set_password("admin123")  # 默认密码，建议上线前修改
    db.session.add(tadmin)

    # 创建会员费设置
    membership_fees = [
        MembershipFee(access_level=1, fee_type='flat_rate', fee_amount=1000),  # 级别1：公共数据访问
        MembershipFee(access_level=2, fee_type='per_person', fee_amount=100),  # 级别2：私有数据消费
        MembershipFee(access_level=3, fee_type='flat_rate', fee_amount=0)  # 级别3：私有数据提供（免费）
    ]

    for fee in membership_fees:
        db.session.add(fee)

    db.session.commit()

    print("数据库初始化完成!")