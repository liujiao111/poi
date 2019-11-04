#-*-coding:utf-8-*-
import csv
import codecs
import os

import osgeo.ogr as ogr
import osgeo.osr as osr
import osgeo.gdal as gdal

'''
shp.py要能正常运行的话需要做如下处理：
1. 下载gata-data.rar文件夹，地址：https://github.com/wudawxb1995/ForLearn，当前文件夹下也有，并解压到随意一个目录下(没有中文的目录)
2. 配置环境变量：GDAL_DATA 值为第一步解压后的文件路径
3.为了解决读取CSV中存在中文的问题，需要设置环境变量：SHAPE_ENCODING    UTF-8
设置完成后重启pycharm工具方可生效 



参考文章：https://blog.csdn.net/zsc201825/article/details/90112302
'''

def trans_point_to_shp(folder, fn, idlng, idlat, delimiter=','):
    data = []
    with codecs.open(folder + fn, 'rb', 'gbk') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # skip the header
        next(reader, None)
        # loop through each of the rows and assign the attributes to variables
        for row in reader:
            name = row[2]
            address = row[3]
            pname = row[4]
            business_area = row[5]
            cityname = row[6]
            adname = row[7]
            type = row[8]
            typecode = row[9]

            type1 = row[10]
            type2 = row[11]
            type3 = row[12]
            type4 = row[13]
            id = row[14]
            try:
                lng = float(row[0])
                lat = float(row[1])
            except Exception:
                continue

            data.append([lng, lat, name, address, pname, business_area, cityname, adname, type, typecode, type1, type2, type3, type4])

    # set up the shapefile driver

    gdal.SetConfigOption('GDAL_FILENAME_IS_UTF8', 'NO')  # 解决中文路径
    gdal.SetConfigOption('SHAPE_ENCODING', 'utf-8')  # 解决SHAPE文件的属性值

    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    #data_source = driver.CreateDataSource(folder +"sss.shp")
    data_source = driver.CreateDataSource(folder + fn.split(".")[0] + ".shp")
    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # create the layer
    layer = data_source.CreateLayer("volcanoes", srs, ogr.wkbPoint)

    # Add the fields we're interested in
    layer.CreateField(ogr.FieldDefn("lng", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("lat", ogr.OFTReal))

    field_name = ogr.FieldDefn("name", ogr.OFTString)
    field_name.SetWidth(24)
    layer.CreateField(field_name)
    layer.CreateField(ogr.FieldDefn("adress", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("pname", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("cityname", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("adname", ogr.OFTString))

    layer.CreateField(ogr.FieldDefn("type", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("typecode", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("type1", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("type2", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("type3", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("type4", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("id", ogr.OFTString))


    # Process the text file and add the attributes and features to the shapefile



    for row in data:
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("lng", row[0])
        feature.SetField("lat", row[1])
        feature.SetField("name", row[2])
        feature.SetField("adress", row[3])
        feature.SetField("pname", row[4])

        feature.SetField("cityname", row[5])
        feature.SetField("adname", row[6])
        feature.SetField("type", row[7])
        feature.SetField("typecode", row[8])
        feature.SetField("type1", row[9])
        feature.SetField("type2", row[10])
        feature.SetField("type3", row[11])
        feature.SetField("type4", row[12])
        feature.SetField("id", row[13])


        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (float(row[0]), float(row[1]))

        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)

        # Set the feature geometry using the point
        feature.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        # Dereference the feature
        feature = None

    # Save and close the data source
    data_source = None



if __name__ == '__main__':
    folder = 'C:\\study\\python\\studyws\\code_20191103\\data\\si-chuan-sheng\\010103' + os.sep

    #folder = 'C:\\study\\python\\studyws\\poi-根据分类编码爬取-导出可选CSV并生成shp\\data\\四川省\\010000' + os.sep
    fn = 'poi-si-chuan-sheng-010103.csv'
    #fn = 'poi-四川省-010000.csv'
    idlng = 0
    idlat = 1
    trans_point_to_shp(folder, fn, idlng, idlat)

