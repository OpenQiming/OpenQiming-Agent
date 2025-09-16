from enum import Enum


class AppStatus(Enum):
    # 草稿
    DRAFT = 'draft'

    # 已发布
    PUBLISHED = 'published'

    # 待审核
    PENDING = 'pending'

    # 上架 Deprecated
    INSTALLED = 'installed'

    # 禁用
    DISABLED = 'disabled'

    @classmethod
    def value_of(cls, value: str) -> 'AppStatus':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid mode value {value}')
