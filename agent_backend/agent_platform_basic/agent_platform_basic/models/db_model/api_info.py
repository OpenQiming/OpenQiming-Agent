from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

Base = declarative_base()

class APIInfo(Base):
    __tablename__ = 'api_info'
    __table_args__ = (
        UniqueConstraint('api_id', name='api_info_api_id_key'),
        Index('api_info_is_public_idx', 'is_public'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
    interface_name_zh = Column(String(255), nullable=False)  # 接口中文名
    interface_name_en = Column(String(255))  # 接口英文名
    api_id = Column(String(100), unique=True, nullable=False)  # APIID，唯一标识
    interface_type = Column(String(50), nullable=False)  # 接口类型
    eop_protocol = Column(String(50))  # EOP协议
    eop_call_address = Column(Text)  # EOP调用地址
    service_protocol = Column(String(50))  # 服务协议
    interface_description = Column(Text)  # 接口说明
    auth_policy = Column(String(100))  # 认证策略
    timeout = Column(Integer)  # 超时时长，单位秒
    open_scope = Column(String(100))  # 开放范围
    is_public = Column(Boolean, nullable=False)  # 是否公网
    system_belonged_to = Column(String(255))  # 所属系统
    region = Column(String(100))  # 区域
    application_scenario = Column(Text)  # 应用场景
    headers = Column(Text)  # 请求头
    request_script = Column(Text)  # 请求脚本
    input_params = Column(Text)  # 输入参数
    request_example = Column(Text)  # 请求示例
    output_params = Column(Text)  # 输出参数
    response_example = Column(Text)  # 返回示例
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))  # 创建时间，默认为当前时间
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))  # 更新时间，默认为当前时间，并且在记录更新时自动更新
    created_by = Column(String(255))  # 创建人
    updated_by = Column(String(255))  # 更新人