import json
import re

from agent_platform_basic.extensions.ext_database import db

"""
@Date    ：2024/7/15 9:29 
@Version: 1.0
@Description:

"""


class Bigmodel(db.Model):
    __tablename__ = 'big_model'

    id = db.Column(db.Integer, primary_key=True)  # 主键
    description = db.Column(db.String(255))
    model_param = db.Column(db.String(5000))
    model_name = db.Column(db.String(255))
    status = db.Column(db.String(255))
    model_id = db.Column(db.String(255))
    base_model_name = db.Column(db.String(255))
    space_id = db.Column(db.String(255))
    create_by = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))