from urllib.parse import quote
from urllib import request
import json
import os
import collections
import pandas as pd
from xpinyin import Pinyin
from transCoordinateSystem import gcj02_to_wgs84, gcj02_to_bd09
import random
from shp import trans_point_to_shp

'''
版本更新说明：
2019.10.05：
    1. 数据导出格式支持CSV、shp格式以及XLS格式;
    2. 支持同时采集多个城市的POI数据;
    3. 支持同时采集多个POI分类数据
'''

# TODO 1.替换为上面申请的密钥,支持多个，如果单个失效了，会自动切换密钥
amap_web_key = ['高德密钥1', '高德密钥2']

# TODO 2.分类关键字,最好对照<<高德地图POI分类关键字以及编码.xlsx>>来填写对应编码，多个用逗号隔开
keyword = ['010600', '010700']

#下面是高德提供的800多个POI分类代码
#keyword = ['010000', '010100', '010101', '010102', '010103', '010104', '010105', '010107', '010108', '010109', '010110', '010111', '010112', '010200', '010300', '010400', '010401', '010500', '010600', '010700', '010800', '010900', '010901', '011000', '011100', '020000', '020100', '020101', '020102', '020103', '020104', '020105', '020106', '020200', '020201', '020202', '020203', '020300', '020301', '020400', '020401', '020402', '020403', '020404', '020405', '020406', '020407', '020408', '020600', '020601', '020602', '020700', '020701', '020702', '020703', '020800', '020900', '020904', '020905', '021000', '021001', '021002', '021003', '021004', '021100', '021200', '021201', '021202', '021203', '021300', '021301', '021400', '021401', '021500', '021501', '021600', '021601', '021602', '021700', '021701', '021702', '021800', '021802', '021803', '021804', '021900', '022000', '022100', '022200', '022300', '022301', '022400', '022500', '022501', '022502', '022600', '022700', '022800', '022900', '023000', '023100', '023200', '023300', '023301', '023400', '023500', '025000', '025100', '025200', '025300', '025400', '025500', '025600', '025700', '025800', '025900', '026000', '026100', '026200', '026300', '029900', '030000', '030100', '030200', '030201', '030202', '030203', '030204', '030205', '030206', '030300', '030301', '030302', '030303', '030400', '030401', '030500', '030501', '030502', '030503', '030504', '030505', '030506', '030507', '030508', '030700', '030701', '030702', '030800', '030801', '030802', '030803', '030900', '031000', '031004', '031005', '031100', '031101', '031102', '031103', '031104', '031200', '031300', '031301', '031302', '031303', '031400', '031401', '031500', '031501', '031600', '031601', '031700', '031701', '031702', '031800', '031801', '031802', '031900', '031902', '031903', '031904', '032000', '032100', '032200', '032300', '032400', '032401', '032500', '032600', '032601', '032602', '032700', '032800', '032900', '033000', '033100', '033200', '033300', '033400', '033401', '033500', '033600', '035000', '035100', '035200', '035300', '035400', '035500', '035600', '035700', '035800', '035900', '036000', '036100', '036200', '036300', '039900', '040000', '040100', '040101', '040200', '040201', '050000', '050100', '050101', '050102', '050103', '050104', '050105', '050106', '050107', '050108', '050109', '050110', '050111', '050112', '050113', '050114', '050115', '050116', '050117', '050118', '050119', '050120', '050121', '050122', '050123', '050200', '050201', '050202', '050203', '050204', '050205', '050206', '050207', '050208', '050209', '050210', '050211', '050212', '050213', '050214', '050215', '050216', '050217', '050300', '050301', '050302', '050303', '050304', '050305', '050306', '050307', '050308', '050309', '050310', '050311', '050400', '050500', '050501', '050502', '050503', '050504', '050600', '050700', '050800', '050900', '060000', '060100', '060101', '060102', '060103', '060200', '060201', '060202', '060300', '060301', '060302', '060303', '060304', '060305', '060306', '060307', '060308', '060400', '060401', '060402', '060403', '060404', '060405', '060406', '060407', '060408', '060409', '060411', '060413', '060414', '060415', '060500', '060501', '060502', '060600', '060601', '060602', '060603', '060604', '060605', '060606', '060700', '060701', '060702', '060703', '060704', '060705', '060706', '060800', '060900', '060901', '060902', '060903', '060904', '060905', '060906', '060907', '061000', '061001', '061100', '061101', '061102', '061103', '061104', '061200', '061201', '061202', '061203', '061204', '061205', '061206', '061207', '061208', '061209', '061210', '061211', '061212', '061213', '061214', '061300', '061301', '061302', '061400', '061401', '070000', '070100', '070200', '070201', '070202', '070203', '070300', '070301', '070302', '070303', '070304', '070305', '070306', '070400', '070401', '070500', '070501', '070600', '070601', '070603', '070604', '070605', '070606', '070607', '070608', '070609', '070610', '070700', '070701', '070702', '070703', '070704', '070705', '070706', '070800', '070900', '071000', '071100', '071200', '071300', '071400', '071500', '071600', '071700', '071800', '071801', '071900', '071901', '071902', '071903', '072000', '072001', '080000', '080100', '080101', '080102', '080103', '080104', '080105', '080106', '080107', '080108', '080109', '080110', '080111', '080112', '080113', '080114', '080115', '080116', '080117', '080118', '080119', '080200', '080201', '080202', '080300', '080301', '080302', '080303', '080304', '080305', '080306', '080307', '080308', '080400', '080401', '080402', '080500', '080501', '080502', '080503', '080504', '080505', '080600', '080601', '080602', '080603', '090000', '090100', '090101', '090102', '090200', '090201', '090202', '090203', '090204', '090205', '090206', '090207', '090208', '090209', '090210', '090211', '090300', '090400', '090500', '090600', '090601', '090602', '090700', '090701', '090702', '100000', '100100', '100101', '100102', '100103', '100104', '100105', '100200', '100201', '110000', '110100', '110101', '110102', '110103', '110104', '110105', '110106', '110200', '110201', '110202', '110203', '110204', '110205', '110206', '110207', '110208', '110209', '120000', '120100', '120200', '120201', '120202', '120203', '120300', '120301', '120302', '120303', '120304', '130000', '130100', '130101', '130102', '130103', '130104', '130105', '130106', '130107', '130200', '130201', '130202', '130300', '130400', '130401', '130402', '130403', '130404', '130405', '130406', '130407', '130408', '130409', '130500', '130501', '130502', '130503', '130504', '130505', '130506', '130600', '130601', '130602', '130603', '130604', '130605', '130606', '130700', '130701', '130702', '130703', '140000', '140100', '140101', '140102', '140200', '140201', '140300', '140400', '140500', '140600', '140700', '140800', '140900', '141000', '141100', '141101', '141102', '141103', '141104', '141105', '141200', '141201', '141202', '141203', '141204', '141205', '141206', '141207', '141300', '141400', '141500', '150000', '150100', '150101', '150102', '150104', '150105', '150106', '150107', '150200', '150201', '150202', '150203', '150204', '150205', '150206', '150207', '150208', '150209', '150210', '150300', '150301', '150302', '150303', '150304', '150400', '150500', '150501', '150600', '150700', '150701', '150702', '150703', '150800', '150900', '150903', '150904', '150905', '150906', '150907', '150908', '150909', '151000', '151100', '151200', '151300', '160000', '160100', '160101', '160102', '160103', '160104', '160105', '160106', '160107', '160108', '160109', '160110', '160111', '160112', '160113', '160114', '160115', '160117', '160118', '160119', '160120', '160121', '160122', '160123', '160124', '160125', '160126', '160127', '160128', '160129', '160130', '160131', '160132', '160133', '160134', '160135', '160136', '160137', '160138', '160139', '160140', '160141', '160142', '160143', '160144', '160145', '160146', '160147', '160148', '160149', '160150', '160151', '160152', '160200', '160300', '160301', '160302', '160303', '160304', '160305', '160306', '160307', '160308', '160309', '160310', '160311', '160312', '160314', '160315', '160316', '160317', '160318', '160319', '160320', '160321', '160322', '160323', '160324', '160325', '160326', '160327', '160328', '160329', '160330', '160331', '160332', '160333', '160334', '160335', '160336', '160337', '160338', '160339', '160340', '160341', '160342', '160343', '160344', '160345', '160346', '160347', '160348', '160349', '160400', '160401', '160402', '160403', '160404', '160405', '160406', '160407', '160408', '160500', '160501', '160600', '170000', '170100', '170200', '170201', '170202', '170203', '170204', '170205', '170206', '170207', '170208', '170209', '170300', '170400', '170401', '170402', '170403', '170404', '170405', '170406', '170407', '170408', '180000', '180100', '180101', '180102', '180103', '180104', '180200', '180201', '180202', '180203', '180300', '180301', '180302', '180400', '180500', '190000', '190100', '190101', '190102', '190103', '190104', '190105', '190106', '190107', '190108', '190109', '190200', '190201', '190202', '190203', '190204', '190205', '190300', '190301', '190302', '190303', '190304', '190305', '190306', '190307', '190308', '190309', '190310', '190311', '190400', '190401', '190402', '190403', '190500', '190600', '190700', '200000', '200100', '200200', '200300', '200301', '200302', '200303', '200304', '200400', '220000', '220100', '220101', '220102', '220103', '220104', '220105', '220106', '220107', '220200', '220201', '220202', '220203', '220204', '220205', '970000', '990000', '991000', '991001', '991400', '991401', '991500']


#keyword = ['010100']
# TODO 3.省，最好单个爬，比较耗时
province = ['云南']

# TODO 4.输出数据坐标系,1为高德GCJ20坐标系，2WGS84坐标系，3百度BD09坐标系
coord = 2

# TODO 5. 输出数据文件格式,1为默认xls格式，2为csv+shp格式
data_file_format = 2



print('总的有', len(keyword), '个待爬POI')

poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://ditu.amap.com/detail/get/detail"

poi_xingzheng_distrinct_url = "https://restapi.amap.com/v3/config/district?subdistrict=1&key=4188efb67360681f89110ccdb11e563b"


buffer_keys = collections.deque(maxlen=len(amap_web_key))
def init_queen():
    for i in range(len(amap_web_key)):
        buffer_keys.append(amap_web_key[i])
    print('当前可供使用的高德密钥：', buffer_keys)

def get_districthtml(province):#province的html
    url = "https://restapi.amap.com/v3/config/district?subdistrict=1&extensions=all&key=4188efb67360681f89110ccdb11e563b"
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
        getpoi_page(cityname, keywords, page)

    data = json.loads(data)

    print('当前密钥：', amap_key, '请求url :', req_url, '返回结果：', data)
    print('返回结果：', data)
    if data['status'] == '0':  # 请求成功，但是返回数据失败
        if data['infocode'] == '10001':
            print('无效的密钥！！！！！！！！！！！！！，重新切换密钥进行爬取')
            # TODO 重新更换密钥
            buffer_keys.remove(buffer_keys[0])
            return getpoi_page(cityname, keywords, page)
        if data['infocode'] == '10003':
            print('当前key访问已超出日访问量！！！！！！！！！！！！！')
            buffer_keys.remove(buffer_keys[0])
            return getpoi_page(cityname, keywords, page)
        print('其他错误:', data['info'])

    return data




def get_distrinctNoCache(city):#city的html
    url = "https://restapi.amap.com/v3/config/district?subdistrict=2&extensions=all&key=4188efb67360681f89110ccdb11e563b"
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
        location = poilist[i]['location']
        name = poilist[i]['name']
        address = poilist[i]['address']
        pname = poilist[i]['pname']
        #provincename = poilist[i]['provincename']
        business_area = poilist[i]['business_area']
        cityname = poilist[i]['cityname']
        adname = poilist[i]['adname']
        type = poilist[i]['type']
        typecode = poilist[i]['typecode']
        lng = str(location).split(",")[0]
        lat = str(location).split(",")[1]
        id = poilist[i]['id']
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
    df.to_csv(file_path, index=False, encoding='gbk')

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
            trans_point_to_shp(file_folder, file_name, 0, 1)
                
            #except Exception as e:
                #print('===================================爬取失败，当前省：', pro, '分类：', type, '...........................')
                #print(e)

    print('总的', len(province), '个省份, ', len(keyword), '个分类数据全部爬取完成!')  # 最后打印

