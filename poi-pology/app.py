from urllib.parse import quote
from urllib import request
import json
import xlwt
from xpinyin import Pinyin
import os
from transCoordinateSystem import gcj02_to_wgs84, gcj02_to_bd09
import area_boundary as  area_boundary
import city_grid as city_grid
import time

from requests.adapters import HTTPAdapter
import requests


## TODO 1.划分的网格距离，0.02-0.05最佳，建议如果是数量比较多的用0.01或0.02，如餐厅，企业。数据量少的用0.05或者更大，如大学
pology_split_distance = 2


## TODO 2. 城市编码，参见高德城市编码表
city_code = '440100'


## TODO 3. POI类型编码
type_code = '170200'

## TODO 4. 高德开放平台密钥
gaode_key = '3a3ccf69cf7b5bab75a68948d8fcad4b'


# TODO 5.输出数据坐标系,1为高德GCJ20坐标系，2WGS84坐标系，3百度BD09坐标系
coord = 1


poi_pology_search_url = 'https://restapi.amap.com/v3/place/polygon'


# 根据城市名称和分类关键字获取poi数据
def getpois(grids, keywords, key):
    i = 1
    poilist = []
    while True:  # 使用while循环不断分页获取数据
        result = getpoi_page(grids, keywords, i, key)
        print(result)
        if result != None:
            result = json.loads(result)  # 将字符串转换为json
            if result['count'] == '0':
                break

            hand(poilist, result)
        i = i + 1
    return poilist


# 数据写入excel
def write_to_excel(poilist, citycode, classfield, coord):
    # 一个Workbook对象，这就相当于创建了一个Excel文件
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet(classfield, cell_overwrite_ok=True)

    # 第一行(列标题)
    sheet.write(0, 0, 'lon')
    sheet.write(0, 1, 'lat')
    sheet.write(0, 2, 'name')
    sheet.write(0, 3, 'address')
    sheet.write(0, 4, 'pname')
    sheet.write(0, 5, 'cityname')
    sheet.write(0, 6, 'adcode')
    sheet.write(0, 7, 'adname')
    sheet.write(0, 8, 'business_area')
    sheet.write(0, 9, 'type')
    sheet.write(0, 10, 'id')

    index = 0
    for i in range(len(poilist)):
        location = poilist[i]['location']
        name = poilist[i]['name']
        address = poilist[i]['address']
        pname = poilist[i]['pname']
        cityname = poilist[i]['cityname']
        business_area =  poilist[i]['business_area']
        type = poilist[i]['type']
        id = poilist[i]['id']
        adcode = poilist[i]['adcode']
        adname = poilist[i]['adname']

        #根据adcode判断当前数据是否属于当前所需要的城市 根据城市编码前四位判断
        if adcode[:4] != citycode[:4]:
            continue
        lng = str(location).split(",")[0]
        lat = str(location).split(",")[1]


        if(coord == "2"):
            result = gcj02_to_wgs84(float(lng), float(lat))
            lng = result[0]
            lat = result[1]
        if(coord == "3"):
            result = gcj02_to_bd09(float(lng), float(lat))
            lng = result[0]
            lat = result[1]

        # 每一行写入
        sheet.write(index + 1, 0, lng)
        sheet.write(index + 1, 1, lat)
        sheet.write(index + 1, 2, name)
        sheet.write(index + 1, 3, address)
        sheet.write(index + 1, 4, pname)
        sheet.write(index + 1, 5, cityname)
        sheet.write(index + 1, 6, adcode)
        sheet.write(index + 1, 7, adname)
        sheet.write(index + 1, 8, business_area)
        sheet.write(index + 1, 9, type)
        sheet.write(index + 1, 10, id)

        index = index + 1


    # 最后，将以上操作保存到指定的Excel文件中
    p = Pinyin()
    p.get_pinyin(cityname)
    path = "data/poi/" + p.get_pinyin(cityname) + "-" + p.get_pinyin(classfield) + '.xls'
    book.save(r'' + os.getcwd() + "/" + path)
    #book.save(r'C:\\Users\\hgvgh\\Desktop\\chendahua\\rest.xls')
    return path


# 将返回的poi数据装入集合返回
def hand(poilist, result):
    # result = json.loads(result)  # 将字符串转换为json
    pois = result['pois']
    for i in range(len(pois)):
        poilist.append(pois[i])


# 单页获取pois
def getpoi_page(grids, types, page, key):
    polygon = str(grids[0]) + "," + str(grids[1]) + "|" + str(grids[2]) + "," + str(grids[3])
    req_url = poi_pology_search_url + "?key=" + key + '&extensions=all&types=' + quote(
        types) + '&polygon=' + polygon + '&offset=25' + '&page=' + str(
        page) + '&output=json'
    print('请求url：', req_url)

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=5))
    s.mount('https://', HTTPAdapter(max_retries=5))
    try:
        data = s.get(req_url, timeout = 5)
        return data.text
    except requests.exceptions.RequestException as e:
        data = s.get(req_url, timeout=5)
        return data.text
    return None


def get_drids(min_lng, max_lat, max_lng, min_lat, keyword, key, pology_split_distance, all_grids):
    grids_lib = city_grid.generate_grids(min_lng, max_lat, max_lng, min_lat, pology_split_distance)

    print('划分后的网格数：', len(grids_lib))
    print(grids_lib)

    # 3. 根据生成的网格爬取数据，验证网格大小是否合适，如果不合适的话，需要继续切分网格
    for grid in grids_lib:
        one_pology_data = getpoi_page(grid, keyword, 1, key)
        data = json.loads(one_pology_data)
        print(data)

        if int(data['count']) > 890:
            get_drids(grid[0], grid[1], grid[2], grid[3], keyword, key, pology_split_distance / 2, all_grids)
        else:
            all_grids.append(grid)
        all_grids.append(grid)
    return all_grids




def get_data(city, keyword, coord, key):

    # 1. 获取城市边界的最大、最小经纬度
    max_lng, min_lng, max_lat, min_lat = area_boundary.getlnglat(city, key)

    print('当前城市：', city, "max_lng, min_lng, max_lat, min_lat：", max_lng, min_lng, max_lat, min_lat)

    # 2. 生成网格切片格式：
    '''
    [[112.23, 23.23, 112.24, 23.22], [112.23, 23.22, 112.24, 23.21]]
    '''

    '''
    grids_lib = []
    grids_lib = get_drids(min_lng, max_lat, max_lng, min_lat, '170200', '4188efb67360681f89110ccdb11e563b',
                          pology_split_distance, grids_lib)
                          '''



    grids_lib = city_grid.generate_grids(min_lng, max_lat, max_lng, min_lat, pology_split_distance)

    print('划分后的网格数：', len(grids_lib))
    print(grids_lib)

    all_data = []
    begin_time = time.time()

    print('==========================正式开始爬取啦！！！！！！！！！！！================================')

    for grid in grids_lib:
        # grid格式：[112.23, 23.23, 112.24, 23.22]
        one_pology_data = getpois(grid, keyword, key)


        print('===================================当前矩形范围：', grid, '总共：',
              str(len(one_pology_data)) + "条数据.............................")

        all_data.extend(one_pology_data)

    end_time = time.time()
    print('全部：', str(len(grids_lib)) + '个矩形范围', '总的', str(len(all_data)), '条数据, 耗时：', str(end_time - begin_time), '正在写入EXCEL中')
    return write_to_excel(all_data, city, keyword, coord)




get_data(city_code, type_code, coord, gaode_key)


'''
all_grids = []
all_grids = get_drids(112.23, 23.33, 113.22, 22.33, '170200', '4188efb67360681f89110ccdb11e563b', pology_split_distance, all_grids)

print(all_grids)
print(len(all_grids))'''
