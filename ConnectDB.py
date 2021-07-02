#!/usr/bin/python
# -*- coding: UTF-8 -*-


import pymysql


def getDataFromDB(sql):
    # 连接
    conn = pymysql.connect(
        host='172.16.19.151',
        port=3306,
        user='root',
        password='hpp20190319Qw',
        db='stock',
        charset='utf8')
    cursor = conn.cursor()
    cursor.execute(sql)
    # result = cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def insertDataToDB(sql):
    # 连接
    conn = pymysql.connect(
        host='172.16.19.151',
        port=3306,
        user='root',

        password='hpp20190319Qw',
        db='stock',
        charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception:
        conn.rollback()
    cursor.close()
    conn.close()
