from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginator(data, page: int, limit: int):
    pagi = Paginator(data, int(limit))
    try:
        pg = pagi.page(int(page))
    except PageNotAnInteger:
        pg = pagi.page(1)
    except EmptyPage:
        pg = pagi.page(pagi.num_pages)
    # print(pg.object_list)
    # Page obj转回list
    # data_list = [data for data in pg]
    # return data_list
    return pg.object_list
