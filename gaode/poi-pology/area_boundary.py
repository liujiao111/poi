# -*- coding:utf-8 -*-
# 第一行必须有，否则报中文字符非ascii码错误
import urllib.request
from urllib.parse import quote
import json


url = 'http://restapi.amap.com/v3/config/district?'
def getlnglat(address, key):

    uri = url + 'keywords=' + quote(address) + '&key=' + key + '&subdistrict=1' + '&extensions=all'

    print(uri)

    # 访问链接后，api会回传给一个json格式的数据
    temp = urllib.request.urlopen(uri)

    temp = json.loads(temp.read())


    # polyline是坐标，name是区域的名字
    Data = temp["districts"][0]['polyline']

    lngs = []
    lats = []
    points = []
    for line in str(Data).split(";"):
        if len(line.split("|")) > 1:
            for uu in line.split("|"):
                if float(uu.split(",")[0]) != None:
                    lngs.append(float(uu.split(",")[0]))
                    lats.append(float(uu.split(",")[1]))
                    points.append([float(uu.split(",")[0]), float(uu.split(",")[1])])
        else:
            if float(line.split(",")[0]) != None:
                lngs.append(float(line.split(",")[0]))
                lats.append(float(line.split(",")[1]))
                points.append([float(line.split(",")[0]), float(line.split(",")[1])])

    print(points)
    print(max(lngs), min(lngs), max(lats), min(lats))
    return max(lngs), min(lngs), max(lats), min(lats)



'''
num = 0
#ad = getSubName(addr_name)  # 得到福州下属区域的城市代码
add = getlnglat(addr_name)  # 得到福州整个的边界数据

while num < len(ad):
    add = pd.concat([add, getlnglat(ad[num].encode("utf-8"))])  # 得到福州下属的全部区域的边界数据
    num += 1
add.to_csv('{0}.csv'.format(addr_name), encoding='gbk')
'''
