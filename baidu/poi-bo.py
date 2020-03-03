#coding: utf-8
import requests
import json
import time
import os
import pandas as pd
import transCoordinateSystem


# TODO 1 查询关键字，只支持单个
keywords = ['美食','酒店','购物','生活服务','丽人','旅游景点','休闲娱乐','运动健身','教育培训','文化传媒','医疗','汽车服务','交通设施','金融','房地产','公司企业','政府机构','出入口','自然地物']
# 类别大全：(一级分类)：
'''
美食
酒店
购物
生活服务
丽人
旅游景点
休闲娱乐
运动健身
教育培训
文化传媒
医疗
汽车服务
交通设施
金融
房地产
公司企业
政府机构
出入口
自然地物
'''

# TODO 2 POI关键词，只支持单个
baiduAk = '1QkdIjutWv0jBDZEKqy9TH4O3divaRcS'


# TODO 3 爬取区域的左下角和右上角百度地图坐标(经纬度）
#地块
bounds = ['41.74550354,123.39628307,41.75664375,123.42075291', '41.75282293,123.42409461,41.76444612,123.44328241']

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
            print(pageNum)
            print(URL)
            resp = requests.get(URL)
            res = json.loads(resp.text)
            # print(resp.text.strip())
            if len(res['results']) == 0:
                print('返回结果为0')
                break
            else:
                for r in res['results']:
                    pois.append(r)
                    file.writelines(str(r).strip() + '\n')
            pageNum += 1
            time.sleep(1)
        except:
            print("except")
            break
    return pois


def main():
    index = 0
    for boun in bounds:
        for key in keywords:
            all_pois = requestBaiduApi(keyWords=key, smallRect=boun, baiduAk=baiduAk)
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

                coords = transCoordinateSystem.bd09_to_wgs84(float(lng), float(lat))

                lngs.append(coords[0])
                lats.append(coords[1])
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
            df.to_csv(data_path + "bmap-poi-" + str(index) + key + '.csv', index=False, encoding='utf_8_sig')
        index += 1

if __name__ == '__main__':
    main()
