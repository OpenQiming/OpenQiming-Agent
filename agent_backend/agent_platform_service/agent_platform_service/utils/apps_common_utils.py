def result_page(datas,total,page,limit):
    if total == 0:
        return {'data': [], 'total': 0, 'page': page, 'limit': limit, 'has_more': False}
    if (len(datas) < limit and page > 1) or total < limit:
        return {'data': datas, 'total': total, 'page': page, 'limit': limit, 'has_more': False}
    else:
        return {'data': datas, 'total': total, 'page': page, 'limit': limit, 'has_more': True}


def get_values_from_json(json, *keys):
    result = {}
    for key in keys:
        result[key] = json[key]
    return result