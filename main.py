import requests
import re
import json
import ConnectDB
import time
from pyquery import PyQuery
import numpy as np
import pandas as pd
from  MyTT import *


# for i in range(1,229):
#     url="http://10.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407824012565122109_1625099562514&pn=%s&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1625099562537" % i
# headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
#     r = requests.get(url, headers=headers)
#     content=str(r.content, encoding = "utf-8")
#     json_data= content[content.find('{'):len(content)-2]
#     j = json.loads(json_data)
#     data=j['data']['diff']
#     print(data)
#     for stock in data:
#         code=stock['f12']
#         code_name=stock['f14']
#         print('code=',code,'code_name=',code_name)
#         sql="SELECT `code` from code where code='%s'" % code
#         result =ConnectDB.getDataFromDB(sql)
#         if result is None or result.__len__()==0:
#             sql="INSERT INTO `stock`.`code` (`code`, `code_name`) VALUES ('%s', '%s');" % (code,code_name)
#             ConnectDB.insertDataToDB(sql)
#     time.sleep(3)

def get_day_line(code):
    url="http://10.push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery112400000593624755986788_1625127558868&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20500101&lmt=120&_=1625127558895" % ("0."+code[1])
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
    r = requests.get(url, headers=headers)
    content=str(r.content, encoding = "utf-8")
    json_data= content[content.find('{'):len(content)-2]
    j = json.loads(json_data)
    if j['data'] is None:
        return
    data=j['data']['klines']
    code = j['data']['code']
    code_name = j['data']['name']
    print(data)
    for value in data:
        day_data = value.split(',')
        date_time=day_data[0]
        start=float(day_data[1])
        end=float(day_data[2])
        hight=float(day_data[3])
        low=float(day_data[4])
        quantity=float(day_data[5])
        amount=float(day_data[6])
        swing=float(day_data[7])
        limit=float(day_data[8])
        limit_value=float(day_data[9])
        rate=float(day_data[10])
        sql="SELECT `code` from day_lines where code='%s' and date_time='%s'" % (code,date_time)
        result =ConnectDB.getDataFromDB(sql)
        if result is None or result.__len__()==0:
            sql="INSERT INTO stock.day_lines ( `code`, `code_name`, `date_time`, `start`, `end`, `hight`, `low`, `quantity`, `amount`, `swing`, `limit`, `limit_value`, `rate`) VALUES ('%s','%s', '%s', %f,%f, %f, %f, %f, %f, %f, %f, %f, %f);" \
                % (code,code_name,date_time,start,end,hight,low,quantity,amount,swing,limit,limit_value,rate)
            ConnectDB.insertDataToDB(sql)
# def get_stock_list(stockListURL):
#     r =requests.get(stockListURL, headers = headers)
#     doc = PyQuery(r.text)
#     list = []
#     # 获取所有 section 中 a 节点，并进行迭代
#     for i in doc('.stockTable a').items():
#         try:
#             href = i.attr.href
#             list.append(re.findall(r"\d{6}", href)[0])
#         except:
#             continue
#     list = [item.lower() for item in list]  # 将爬取信息转换小写
#     return list
# stock_list_url = 'https://hq.gucheng.com/gpdmylb.html'
# list = get_stock_list(stock_list_url)
# for item in list:
#     sql="SELECT `code` from code where code='%s'" % item
#     result =ConnectDB.getDataFromDB(sql)
#     if result is None or result.__len__()==0:
#         sql="INSERT INTO `stock`.`code` (`code`, `code_name`) VALUES ('%s', '%s');" % (item,"")
#         ConnectDB.insertDataToDB(sql)
#         print(item)

def EMA(S,N):     #为了精度 S>4*N  EMA至少需要120周期
    return pd.Series(S).ewm(span=N, adjust=False).mean().values

def SMA(S, N, M=1):    #中国式的SMA,至少需要120周期才精确
    K = pd.Series(S).rolling(N).mean()    #先求出平均值
    for i in range(N+1, len(S)):  K[i] = (M * S[i] + (N -M) * K[i-1]) / N  # 因为要取K[i-1]，所以 range(N+1, len(S))
    return K

def MACD(CLOSE, SHORT=12, LONG=26, M=9):  # EMA的关系，S取120日，和雪球小数点2位相同
    DIF = EMA(CLOSE, SHORT) - EMA(CLOSE, LONG);
    DEA = EMA(DIF, M);
    MACD = (DIF - DEA) * 2
    return DIF, DEA, MACD


def RSI(CLOSE, N=24):
    DIF = CLOSE - REF(CLOSE, 1)
    return SMA(MAX(DIF, 0), N) / SMA(ABS(DIF), N) * 100

sql="select * from day_lines where `code`='002273'"
data_list= ConnectDB.getDataFromDB(sql)
CLOSE=[]
OPEN=[]
HIGH=[]
LOW=[]
for item in data_list:
    OPEN.append(item[4])
    CLOSE.append(item[5])
    HIGH.append(item[6])
    LOW.append(item[7])
N=5
var1=4*SMA((CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100,5,1)-3*SMA(SMA((CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100,5,1),3.2,1)


# sql="select * from code where id>3313"
# code_list= ConnectDB.getDataFromDB(sql)
# for code in code_list:
#     get_day_line(code)
