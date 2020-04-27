
import pandas as pd
from boundary import get_boundary_by_uid, transform_coordinate_batch
import os
import uuid
from transCoordinateSystem import bd09_to_wgs84

#TODO 带有UID字段的CSV格式的百度POI数据文件地址，最终爬取的边界数据位于data目录下，文件命名：result-xxx.csv,坐标经纬度为WGS84
file_path = 'data/bmap-poi--park-shanghai.csv'

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

boundary_result_file_name = 'data' + os.sep + str(uuid.uuid4()).replace("-", "")

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

boundary_result_file_name = 'data' + os.sep + 'result-' + str(uuid.uuid4()).replace("-", "")
df.to_csv(boundary_result_file_name, index=False, encoding='gbk')