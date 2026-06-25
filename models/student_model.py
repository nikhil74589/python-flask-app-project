from db import db

class Student(db.Model):
    __tablename__="students"
    id=db.Column(db.Integer,primary_key=True)
    stu_name=db.Column(db.String(100),nullable=False)
    stu_age=db.Column(db.Date,nullable=False)        # DateTime → Date
    stu_email=db.Column(db.String(100),unique=True)
    stu_phone=db.Column(db.String(10),nullable=False,unique=True)
    stu_password=db.Column(db.String(200),nullable=False)
    stu_address=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(20),nullable=False)