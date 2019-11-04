#-*-coding:utf-8-*-
import shapefile as shp
import csv
import codecs
import os

def trans_point_to_shp(folder, fn, idlng, idlat, delimiter=','):

    w = shp.Writer(folder)
    w.field('lon', 'F', 10, 8)
    w.field('lat', 'F', 10, 8)
    w.field('name', 'C', 100)
    w.field('pname', 'C', 10, 8)  # float
    w.field('cityname', 'C', 10, 8)  # float
    w.field('business_area', 'C', 100)  # string, max-length
    w.field('type', 'C', 100)  # string, max-length

    with codecs.open(folder + fn, 'rb', 'utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # skip the header
        next(reader, None)
        # loop through each of the rows and assign the attributes to variables
        for row in reader:
            name = row[2]
            address = row[3]
            pname = row[4]
            cityname = row[5]
            business_area = row[6]
            type = row[7]
            lng = float(row[idlng])
            lat = float(row[idlat])
            w.point(lng, lat)
            w.record(lng, lat, name, address, pname, cityname, business_area, type)

    w.close()


if __name__ == '__main__':
    folder = 'C:\\study\\python\\studyws\\poi-根据分类编码爬取-20191005\\data' + os.sep
    fn = 'poi-重庆市-160600.csv'
    idlng = 0
    idlat = 1
    trans_point_to_shp(folder, fn, idlng, idlat)

    idlng = 0
    idlat = 1

    # trans_point_to_shp(folder, fn, idlng, idlat)

    '''
    path = folder + fn.split(".")[0] + os.sep
    print(path)

    delimiter = ','

    w = shp.Writer(path)
    w.field('lon', 'F', 10, 8)
    w.field('lat', 'F', 10, 8)
    w.field('name', 'C', 100)
    w.field('pname', 'C', 10, 8)  # float
    w.field('cityname', 'C', 10, 8)  # float
    w.field('business_area', 'C', 100)  # string, max-length
    w.field('type', 'C', 100)  # string, max-length

    with codecs.open(folder + fn.split(".")[0] + os.sep + fn, 'rb', 'gbk') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # skip the header
        next(reader, None)
        #loop through each of the rows and assign the attributes to variables
        for row in reader:
            name = row[2]
            address = row[3]
            pname = row[4]
            cityname = row[5]
            business_area = row[6]
            type = row[7]
            lng = float(row[idlng])
            lat = float(row[idlat])
            w.point(lng, lat)
            w.record(lng, lat, name, address, pname, cityname, business_area, type)

    w.close()
    '''

