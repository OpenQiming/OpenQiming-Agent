class StringUtils:

    @staticmethod
    def is_blank(s: str) -> bool:
        if s is None:
            return True
        return s.strip() == ""

    @staticmethod
    def is_not_blank(s: str) -> bool:
        if s is None:
            return False
        return s.strip() != ""

    @staticmethod
    def equal(s1: str, s2: str) -> bool:
        str1 = s1 if s1 is not None else ""
        str2 = s2 if s2 is not None else ""
        return str1 == str2

    @staticmethod
    def not_equal(s1: str, s2: str) -> bool:
        str1 = s1 if s1 is not None else ""
        str2 = s2 if s2 is not None else ""
        return str1 != str2
