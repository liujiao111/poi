from urllib.parse import quote
from urllib import request
import json
import os
import collections
import pandas as pd
from xpinyin import Pinyin
from transCoordinateSystem import gcj02_to_wgs84, gcj02_to_bd09
import random
#from shp import trans_point_to_shp

'''
版本更新说明：
2019.10.05：
    1. 数据导出格式支持CSV、shp格式以及XLS格式;
    2. 支持同时采集多个城市的POI数据;
    3. 支持同时采集多个POI分类数据
    
2020.06.19:
    1.清除了poi数据写入shp文件相关操作
'''

#################################################需要修改###########################################################

# TODO 1.替换为上面申请的密钥,支持多个，如果单个失效了，会自动切换密钥
amap_web_key = ['高德秘钥1', '高德秘钥2']

# TODO 2.分类关键字,最好对照<<高德地图POI分类关键字以及编码.xlsx>>来填写对应编码，多个用逗号隔开
keyword = ['010600', '010700']


# TODO 3.省名，最好单个爬，比较耗时
province = ['云南']

# TODO 4.输出数据坐标系,1为高德GCJ20坐标系，2WGS84坐标系，3百度BD09坐标系
coord = 2

# TODO 5. 输出数据文件格式,1为默认xls格式，2为csv+shp格式
data_file_format = 2


############################################以下不需要动#######################################################################


print('总的有', len(keyword), '个待爬POI')

poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://ditu.amap.com/detail/get/detail"


buffer_keys = collections.deque(maxlen=len(amap_web_key))
def init_queen():
    for i in range(len(amap_web_key)):
        buffer_keys.append(amap_web_key[i])
    print('当前可供使用的高德密钥：', buffer_keys)

def get_districthtml(province):#province的html

    if buffer_keys.maxlen == 0:
        print('密钥已经用尽，程序退出！！！！！！！！！！！！！！！')
        exit(0)
    amap_key = buffer_keys[0] #总是获取队列中的第一个密钥
    print('获取到的队列中的密钥：', amap_key)
    url = "https://restapi.amap.com/v3/config/district?subdistrict=1&extensions=all&key=" + amap_key
    req_url = url + "&keywords=" + quote(str(province))
    print(req_url)

    with request.urlopen(req_url) as f:
        HTML = f.read()
        HTML = HTML.decode('utf-8')
        print(province, HTML)
        HTML = json.loads(HTML)

        districts = HTML['districts'][0]['districts']
        city_codes = []
        city_names = []
        for district in districts:
            name = district['name']
            adcode = district['adcode']
            city_codes.append(adcode)
            city_names.append(name)
        return city_codes, city_names


def get_random_key():
    return amap_web_key[random.randint(0, len(amap_web_key) - 1)]

# 根据城市名称/area名称和分类关键字获取poi数据
def getpois(area, keywords, poilist, city, area_name): #输入city或者area均可 本文是area
    i = 1
    while True:  # 使用while循环不断分页获取数据
        result = getpoi_page(area, keywords, i)
        print(result)

        if result['count'] == '0':
            break
        hand(poilist, result, city, area_name)
        i = i + 1
    return poilist


# 将返回的poi数据装入集合返回
def hand(poilist, result, city, area_name):

    print('result:', result)
    # result = json.loads(result)  # 将字符串转换为json
    pois = result['pois']
    for i in range(len(pois)):
        pois
        poilist.append(pois[i])
# 单页获取pois
def getpoi_page(cityname, keywords, page):
    if buffer_keys.maxlen == 0:
        print('密钥已经用尽，程序退出！！！！！！！！！！！！！！！')
        exit(0)
    amap_key = buffer_keys[0] #总是获取队列中的第一个密钥
    print('获取到的队列中的密钥：', amap_key)

    req_url = poi_search_url + "?key=" + amap_key + '&extensions=all&types=' + quote(
        keywords) + '&city=' + quote(cityname) + '&citylimit=true' + '&offset=25' + '&page=' + str(
        page) + '&output=json'
    '''
    http: // restapi.amap.com / v3 / place / text?keywords = 北京大学 & city = beijing & output = xml
    & offset = 20 & page = 1 & key = < 用户的key > & extensions = all
    '''
    try:
        with request.urlopen(req_url, timeout=3, ) as f:
            data = f.read()
            data = data.decode('utf-8')
    except Exception as e:
        print('请求异常')
        return getpoi_page(cityname, keywords, page)

    data = json.loads(data)

    print('当前密钥：', amap_key, '请求url :', req_url, '返回结果：', data)
    print('返回结果：', data)
    if data['status'] == '0':  # 请求成功，但是返回数据失败
        if data['infocode'] == '10001':
            print('无效的密钥！！！！！！！！！！！！！，重新切换密钥进行爬取')
            buffer_keys.remove(buffer_keys[0])
            return getpoi_page(cityname, keywords, page)
        if data['infocode'] == '10003':
            print('当前key访问已超出日访问量！！！！！！！！！！！！！')
            buffer_keys.remove(buffer_keys[0])
            return getpoi_page(cityname, keywords, page)
        print('其他错误:', data['info'])

    return data




def get_distrinctNoCache(city):#city的html
    if buffer_keys.maxlen == 0:
        print('密钥已经用尽，程序退出！！！！！！！！！！！！！！！')
        exit(0)
    amap_key = buffer_keys[0] #总是获取队列中的第一个密钥
    print('获取到的队列中的密钥：', amap_key)
    url = "https://restapi.amap.com/v3/config/district?subdistrict=2&extensions=all&key=" + amap_key
    req_url = url + "&keywords=" + quote(city)
    print(req_url)
    with request.urlopen(req_url) as f:
        data = f.read()
        data = data.decode('utf-8')
    print(city, data)
    return data


def get_areas(city): #根据city以及获取到的html，处理得到area---后的POI键值对
    print('获取城市: ' + str(city).strip())
    data = get_distrinctNoCache(city)
    print('城市的HTML:' + data)
    data = json.loads(data)
    print(data)

    if len(data['districts']) == 0:
        return city

    districts = data['districts'][0]['districts'] #根据POI键值对获取？？
    # 判断是否是直辖市
    # 北京市、上海市、天津市、重庆市。
    if (str(city).startswith('重庆') or str(city).startswith('上海') or str(city).startswith('北京') or str(city).startswith('天津')):
        districts =data ['districts'][0]['districts'][0]['districts']
    i = 0
    areas = []
    names = []
    for district in districts:
        name = district['name']
        adcode = district['adcode']
        i = i + 1
        areas.append(adcode)
        names.append(name)
    return areas, names


def get_data(province, classfield):
    poi_list = []

    #获取省下面的所有城市
    city_codes, city_names = get_districthtml(province)

    print(city_codes)
    print(city_names)


    for i in range(len(city_codes)):
        city = city_codes[i]
        name = city_names[i]
        print(city, name)
        areas, area_names = get_areas(city)
        for i  in range(len(areas)):
            area = areas[i]
            area_name = area_names[i]
            poi_list = getpois(area, classfield, poi_list, city, area_name)

    return poi_list



# 数据写入csv文件中
def write_to_csv(poilist, provincename, classfield):
    data_csv = {}
    lons, lats, names, addresss, pnames, business_areas,citynames, adnames, types, typecodes\
        , type_1s, type_2s, type_3s, type_4s, ids = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

    for i in range(len(poilist)):
        location = poilist[i].get('location')
        name = poilist[i].get('name')
        address = poilist[i].get('address')
        pname = poilist[i].get('pname')
        #provincename = poilist[i]['provincename']
        business_area = poilist[i].get('business_area')
        cityname = poilist[i].get('cityname')
        adname = poilist[i].get('adname')
        type = poilist[i].get('type')
        typecode = poilist[i].get('typecode')
        lng = str(location).split(",")[0]
        lat = str(location).split(",")[1]
        id = poilist[i].get('id')
        type = str(type)
        type_1 = ''
        type_2 = ''
        type_3 = ''
        type_4 = ''
        if str(type) != None and str(type) != '':
            type_strs = type.split(';')
            for i in range(len(type_strs)):
                ty = type_strs[i]
                if i == 0:
                    type_1 = ty
                elif i == 1:
                    type_2 = ty
                elif i == 2:
                    type_3 = ty
                elif i == 3:
                    type_4 = ty

        if (coord == 2):
            result = gcj02_to_wgs84(float(lng), float(lat))
            lng = result[0]
            lat = result[1]
        if (coord == 3):
            result = gcj02_to_bd09(float(lng), float(lat))
            lng = result[0]
            lat = result[1]
        lons.append(lng)
        lats.append(lat)
        names.append(name)
        addresss.append(address)
        citynames.append(cityname)
        adnames.append(adname)
        pnames.append(pname)
        #provincenames.append(provincename)
        if business_area == []:
            business_area = ''
        business_areas.append(business_area)
        types.append(type)
        typecodes.append(typecode)
        type_1s.append(type_1)
        type_2s.append(type_2)
        type_3s.append(type_3)
        type_4s.append(type_4)
        ids.append(id)
    data_csv['lon'], data_csv['lat'], data_csv['name'], data_csv['address'], data_csv['pname'], \
    data_csv['business_area'], data_csv['cityname'], data_csv['adname'], data_csv['type'], data_csv['typecode'], \
    data_csv['type1'], data_csv['type2'], data_csv['type3'], data_csv['type4'], data_csv['id'] = \
        lons, lats, names, addresss, pnames, business_areas, citynames, adnames, types, typecodes, type_1s, type_2s, type_3s, type_4s, ids

    pin = Pinyin()
    provincename_pinyin = pin.get_pinyin(provincename)  # 默认分割符为-

    df = pd.DataFrame(data_csv)
    folder_name_full = 'data' + os.sep + provincename_pinyin + os.sep #+ classfield + os.sep
    if os.path.exists(folder_name_full) is False:
        os.makedirs(folder_name_full)


    file_name = 'poi-' + provincename_pinyin + "-" + classfield + ".csv"


    file_path = folder_name_full + file_name
    df.to_csv(file_path, index=False, encoding='utf_8_sig')

    print('写入地址：', folder_name_full, file_name)
    return folder_name_full, file_name


if __name__ == '__main__':  # 函数运行的入口，直接print('hello, world')也可以运行。


    #初始化密钥队列
    init_queen()

    one_pro_type_poi_list = []
    for pro in province:  # 循环获取每个省份的POI
        print('=====================当前省：', pro, '爬取开始...............')
        for type in keyword:  # 循环获取每个编码的POI
            print('=====================当前POI类型：', type, '爬取开始...............')
            #一个省一个类型的数据总和
            #try:
            one_pro_type_poi_list = get_data(pro, type)  # 最先要读，和最先调用的函数

            print('当前省：', pro, '分类：', type, '爬取完成，总共', len(one_pro_type_poi_list), '条数据')

            # 写入文件中
            file_folder, file_name = write_to_csv(one_pro_type_poi_list, pro, type)

            # 写入shp
            #trans_point_to_shp(file_folder, file_name, 0, 1)
                
            #except Exception as e:
                #print('===================================爬取失败，当前省：', pro, '分类：', type, '...........................')
                #print(e)

    print('总的', len(province), '个省份, ', len(keyword), '个分类数据全部爬取完成!')  # 最后打印

