
import pandas as pd
import os
import uuid
from transCoordinateSystem import bd09_to_wgs84
import requests,json,math
from requests.adapters import HTTPAdapter


#TODO 1.带有UID字段的CSV格式的百度POI数据文件地址，最终爬取的边界数据位于data目录下，文件命名：result-xxx.csv,坐标经纬度为WGS84
file_path = 'data/bmap-poi--park-shanghai.csv'


#TODO 2.百度地图服务端密钥
bmap_key = '百度密钥'



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

csv_file = pd.read_csv(file_path, encoding='utf-8')
a_col = []
data_csv = {}

uids,  boundarys = [], []
for i in range(len(csv_file)):
    uid = csv_file['uid'][i]
    uids.append(uid)

    coordinates = get_boundary_by_uid(uid)
    if coordinates is not None:
        coords = transform_coordinate_batch(coordinates)
        print('成功返回边界：', uid + ',' + coords)
        boundarys.append(coords)
    else:
        boundarys.append(' ')

data_csv['uid'] = uids

data_csv['boundary'] = boundarys
df = pd.DataFrame(data_csv)

boundary_result_file_name = 'data' + os.sep + 'temp-' + str(uuid.uuid4()).replace("-", "") + '.csv'

df.to_csv(boundary_result_file_name, index=False, encoding='gbk')


# 将数据处理为ARCGIS能展示多边形的数据格式
csv_file = pd.read_csv(boundary_result_file_name, encoding='gbk')

a_col = []
data_csv = {}
numbers, xs, ys, uids = [], [], [], []
index = 1
for i in range(len(csv_file)):
    boundary = str(csv_file['boundary'][i])

    uid = str(csv_file['uid'][i])

    if boundary != ' ' and boundary != 'nan' and boundary != None:
        for point in boundary.split(";"):
            print(boundary)
            lng = point.split(",")[0]
            lat = point.split(",")[1]


            #转换为WGS84坐标系
            coord_wgs84 = bd09_to_wgs84(float(lng), float(lat))
            lng = coord_wgs84[0]
            lat = coord_wgs84[1]

            xs.append(lng)
            ys.append(lat)
            numbers.append(index)
            uids.append(uid)

            index = index + 1
data_csv['number'] = numbers
data_csv['x'] = xs
data_csv['y'] = ys
data_csv['uid'] = uids

df = pd.DataFrame(data_csv)

boundary_result_file_name = 'data' + os.sep + 'result-' + str(uuid.uuid4()).replace("-", "") + '.csv'
df.to_csv(boundary_result_file_name, index=False, encoding='gbk')