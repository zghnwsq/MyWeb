from django.db import connection


def dict_fetch_all(sql, params):
    """
    https://docs.djangoproject.com/zh-hans/3.1/topics/db/sql/#django.db.models.Manager.raw
    :param params: sql params
    :param sql: raw sql
    :return: list of dict
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def raw_sql_fetch_one(sql, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()




