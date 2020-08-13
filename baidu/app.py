#coding: utf-8
import requests
import json
import time
import os
import pandas as pd
from transCoordinateSystem import bd09_to_wgs84

# TODO 1 查询关键字，只支持单个
KeyWord = "餐饮"

# TODO 2 POI关键词，只支持单个
baiduAk = '百度地图申请的密钥'

# TODO 3 爬取区域的左下角和右上角百度地图坐标(经纬度）
BigRect = {
    'left': {
        'x': 120.86099303837032,
        'y': 30.6607006997429
    },
    'right': {
        'x': 122.12725435186897,
        'y': 31.89735902287794
    }
}

# TODO 4 划分细分窗口的数量，横向X * 纵向Y
WindowSize = {
    'xNum': 5.0,
    'yNum': 5.0
}




def getSmallRect(bigRect, windowSize, windowIndex):
    """
    获取小矩形的左上角和右下角坐标字符串（百度坐标系）
    :param bigRect: 关注区域坐标信息
    :param windowSize:  细分窗口数量信息
    :param windowIndex:  Z型扫描的小矩形索引号
    :return: lat,lng,lat,lng
    """
    offset_x = (bigRect['right']['x'] - bigRect['left']['x'])/windowSize['xNum']
    offset_y = (bigRect['right']['y'] - bigRect['left']['y'])/windowSize['yNum']
    left_x = bigRect['left']['x'] + offset_x * (windowIndex % windowSize['xNum'])
    left_y = bigRect['left']['y'] + offset_y * (windowIndex // windowSize['yNum'])
    right_x = (left_x + offset_x)
    right_y = (left_y + offset_y)
    return str(left_y) + ',' + str(left_x) + ',' + str(right_y) + ',' + str(right_x)


def requestBaiduApi(keyWords, smallRect, baiduAk):
    pageNum = 0
    file = open(os.getcwd() + os.sep + "data/result.txt", 'a+', encoding='utf-8')
    pois = []
    while True:
        try:
            URL = "http://api.map.baidu.com/place/v2/search?query=" + keyWords + \
                "&bounds=" + smallRect + \
                "&output=json" +  \
                "&ak=" + baiduAk + \
                "&scope=2" + \
                "&page_size=20" + \
                "&page_num=" + str(pageNum)
            print(URL)
            resp = requests.get(URL)
            res = json.loads(resp.text)
            if len(res['results']) == 0:
                print('返回结果为0')
                break
            else:
                for r in res['results']:
                    pois.append(r)
                    file.writelines(str(r).strip() + '\n')
            pageNum += 1
            time.sleep(1)
        except Exception as e:
            print("爬取失败，请查看输出的错误信息：", resp.text.strip())
            break
    return pois

def check_params():
    '''
    判断输入的经纬度范围是否正确
    :return:
    '''

    min_lng = BigRect['left']['x']
    max_lng = BigRect['right']['x']

    min_lat = BigRect['left']['y']
    max_lat = BigRect['right']['y']

    if int(min_lng) > int(max_lng):
        print('输入经度有误!，右上角的经度应该大于左下角的经度值')
        exit(0)
    if int(min_lat) > int(max_lat):
        print('输入经度有误!，右上角的纬度应该大于左下角的纬度值')
        exit(0)

def main():
    #检查输入参数是否正确
    check_params()

    all_pois = []
    for index in range(int(WindowSize['xNum'] * WindowSize['yNum'])):
        smallRect = getSmallRect(BigRect, WindowSize, index)

        print(smallRect)
        pois = requestBaiduApi(keyWords=KeyWord, smallRect=smallRect, baiduAk=baiduAk)
        all_pois.extend(pois)
        time.sleep(1)

    data_csv = {}
    uids, names, provinces, citys, areas, addresses, lngs, lats = [], [], [], [], [], [], [], []
    for poi in all_pois:
        if poi == None:
            continue
        uids.append(poi.get('uid'))
        names.append(poi.get('name'))
        provinces.append(poi.get('province'))
        citys.append(poi.get('city'))
        areas.append(poi.get('area'))
        addresses.append(poi.get('address'))
        location = poi['location']
        lng = location['lng']
        lat = location['lat']

        result = bd09_to_wgs84(float(lng), float(lat))
        lng = result[0]
        lat = result[1]

        lngs.append(lng)
        lats.append(lat)
    data_csv['uid'] = uids
    data_csv['name'] = names
    data_csv['province'] = provinces
    data_csv['city'] = citys
    data_csv['area'] = areas
    data_csv['address'] = addresses
    data_csv['lng'] = lngs
    data_csv['lat'] = lats

    df = pd.DataFrame(data_csv)
    data_path = os.getcwd() + os.sep + "data" + os.sep
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    df.to_csv(data_path + "bmap-poi-" + KeyWord + '.csv', index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
