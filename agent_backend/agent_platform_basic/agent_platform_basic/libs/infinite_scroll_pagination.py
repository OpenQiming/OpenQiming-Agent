"""
@Date    ：2024/7/8 15:34 
@Version: 1.0
@Description:
    Scroll Pagination
"""


class InfiniteScrollPagination:
    def __init__(self, data, limit, has_more):
        self.data = data
        self.limit = limit
        self.has_more = has_more
