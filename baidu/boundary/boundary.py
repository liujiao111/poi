import requests
import json
from requests.adapters import HTTPAdapter
import math


'''
根据UID获取百度地图POI数据的边界坐标
'''


# POI ID
uid = '2ada94567663a7e1f1193724'

#百度地图服务端密钥
bmap_key = '1QkdIjutWv0jBDZEKqy9TH4O3divaRcS'

def get_boundary_by_uid(uid):
    bmap_boundary_url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&uid=' + uid + '&c=340&ext_ver=new&tn=B_NORMAL_MAP&nn=0&auth=fw9wVDQUyKS7%3DQ5eWeb5A21KZOG0NadNuxHNBxBBLBHtxjhNwzWWvy1uVt1GgvPUDZYOYIZuEt2gz4yYxGccZcuVtPWv3GuxNt%3DkVJ0IUvhgMZSguxzBEHLNRTVtlEeLZNz1%40Db17dDFC8zv7u%40ZPuxtfvSulnDjnCENTHEHH%40NXBvzXX3M%40J2mmiJ4Y&ie=utf-8&l=19&b=(12679382.095,2565580.38;12679884.095,2565907.38)&t=1573133634785'


    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    data = s.get(url=bmap_boundary_url, timeout=5, headers={"Connection": "close"})
    data = data.text
    data = json.loads(data)
    content = data['content']
    if not 'geo' in content:
        return None
    geo = content['geo']
    i = 0
    strsss = ''
    for jj in str(geo).split('|')[2].split('-')[1].split(','):
        jj = str(jj).strip(';')
        if i % 2 == 0:
            strsss = strsss + str(jj) + ','
        else:
            strsss = strsss + str(jj) + ';'
        i = i + 1
    return strsss.strip(";")

def transform_coordinate_batch(coordinates):
    cooed_count = math.ceil(len(coordinates) / 100)

    coords = ''


    for i in range(cooed_count):
        one_coords = coordinates.split(";")[i * 100: i * 100 + 100]
        one_coords_str = ''
        for point in one_coords:
            one_coords_str = one_coords_str + point + ";"

        one_coords_str = one_coords_str.strip(";")
        print(one_coords_str.strip(";"))


        req_url = 'http://api.map.baidu.com/geoconv/v1/?coords='+one_coords_str+'&from=6&to=5&ak=' + bmap_key

        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        print(req_url)

        data = s.get(req_url, timeout=5, headers={"Connection": "close"})  # , proxies=proxies
        data = data.text
        try:
            data = json.loads(data)
        except Exception as e:
            print('发送异常，当前坐标：', coordinates)
            return ' '

        if data['status'] == 0:
            result = data['result']
            if len(result) > 0:
                for res in result:
                    lng = res['x']
                    lat = res['y']
                    coords = coords + ";" + str(lng) + "," + str(lat)
    print(coords.strip(";"))
    return coords.strip(";")

#coordinates = get_boundary_by_uid(uid)
#coords = transform_coordinate_batch(coordinates)
#print(coords)



