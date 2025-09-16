from typing import Any, Dict, Union, Type

# 处理返回字段步骤

class ExtraFieldsHandler:
    """处理额外字段的通用类"""

    def __init__(self, obj: Any, session, extra_field_handlers):
        self.obj = obj
        self.session = session
        self.extra_field_handlers = extra_field_handlers

    async def handle(self):
        """处理额外字段逻辑"""
        for field_name, handler in self.extra_field_handlers.items():
            setattr(self.obj, field_name, await handler(self.obj, self.session))

# 生成需要返回的实例
# 示例：
async def create_instance(obj_or_class: Union[Type[Any], Any], method_name: str, method_args: Dict[str, Any], session, extra_field_handlers=None, return_type=None):
    if isinstance(obj_or_class, type):
        obj = obj_or_class(session=session)
    else:
        obj = obj_or_class
    # 动态调用 obj 上的方法
    res = await getattr(obj, method_name)(**method_args)

    if extra_field_handlers:
        handler = ExtraFieldsHandler(obj, session, extra_field_handlers)
        await handler.handle()

    # 如果指定了返回类型，并且类型不是原始对象的类型，并且动态方法返回值不为空
    # 如果指定了返回类型，必须在指定类型的__init__方法写具体的转换逻辑
    new_res = None
    if return_type and return_type != type(res) and res is not None:
        # 创建新类型的实例
        new_res = return_type(res)

    return new_res if return_type else res