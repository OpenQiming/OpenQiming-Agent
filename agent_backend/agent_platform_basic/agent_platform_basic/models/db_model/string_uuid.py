from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID


class StringUUID(TypeDecorator):
    impl = CHAR  # 底层数据库类型选择 char
    cache_ok = True  # 允许缓存此类型的实例

    def process_bind_param(self, value, dialect):
        """
        将值绑定到 SQL 语句之前调用。
        如果值为 None，返回 None。
        如果数据库是 PostgreSQL，返回字符串形式的 UUID。
        否则，返回十六进制字符串形式的 UUID。
        """
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            return value.hex

    def load_dialect_impl(self, dialect):
        """
        加载特定数据库的类型实现。
        如果数据库是 PostgreSQL，使用 UUID 类型描述符。
        否则，使用 CHAR(36) 类型描述符。
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_result_value(self, value, dialect):
        """
        从数据库检索值时调用。
        如果值为 None，返回 None。
        否则，将值转换为字符串。
        """
        if value is None:
            return value
        return str(value)
