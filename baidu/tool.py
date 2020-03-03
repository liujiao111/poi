class Point:
    lng = ''
    lat = ''

    def __init__(self, lng, lat):
        self.lng = lng
        self.lat = lat


    # 求外包矩形
    def get_polygon_bounds(points):
        length = len(points)
        top = down = left = right = points[0]
        for i in range(1, length):
            if points[i].lng > top.lng:
                top = points[i]
            elif points[i].lng < down.lng:
                down = points[i]
            else:
                pass
            if points[i].lat > right.lat:
                right = points[i]
            elif points[i].lat < left.lat:
                left = points[i]
            else:
                pass
        top_left = Point(top.lng, left.lat)
        top_right = Point(top.lng, right.lat)
        down_right = Point(down.lng, right.lat)
        down_left = Point(down.lng, left.lat)
        return [top_left, top_right, down_right, down_left]


    # 判断点是否在外包矩形外
    def is_point_in_rect(point, polygon_bounds):
        top_left = polygon_bounds[0]
        top_right = polygon_bounds[1]
        down_right = polygon_bounds[2]
        down_left = polygon_bounds[3]
        return (down_left.lng <= point.lng <= top_right.lng
                and top_left.lat <= point.lat <= down_right.lat)


    def is_point_in_polygon(self,point, points):
        polygon_bounds = self.get_polygon_bounds(points)
        if not self.is_point_in_rect(point, polygon_bounds):
            return False
        length = len(points)
        point_start = points[0]
        flag = False
        for i in range(1, length):
            point_end = points[i]
            # 点与多边形顶点重合
            if (point.lng == point_start.lng and point.lat == point_start.lat) or (
                    point.lng == point_end.lng and point.lat == point_end.lat):
                return True
            # 判断线段两端点是否在射线两侧
            if (point_end.lat < point.lat <= point_start.lat) or (
                    point_end.lat >= point.lat > point_start.lat):
                # 线段上与射线 Y 坐标相同的点的 X 坐标
                if point_end.lat == point_start.lat:
                    x = (point_start.lng + point_end.lng) / 2
                else:
                    x = point_end.lng - (point_end.lat - point.lat) * (
                            point_end.lng - point_start.lng) / (
                                point_end.lat - point_start.lat)
                # 点在多边形的边上
                if x == point.lng:
                    return True
                # 射线穿过多边形的边界
                if x > point.lng:
                    flag = not flag
                else:
                    pass
            else:
                pass

            point_start = point_end
        return flag


    def test(self, input_lng=116.732617, input_lat=39.722676):
        # polyline 是多个坐标点，形如
        # ['116.732617,39.722676', '116.732617,39.722676', '116.732617,39.722676',
        # '116.732617,39.722676', '116.732617,39.722676']
        polyline = ['116.732617,39.722676', '116.732617,39.722676', '116.732617,39.722676','116.732617,39.722676', '116.732617,39.722676']

        points = []
        for line in polyline:
            if line:
                try:
                    lng, lat = line.split(',')
                    points.append(Point(float(lng), float(lat)))
                except ValueError:
                    pass
        if points:
            self.is_point_in_polygon(Point(float(input_lng), float(input_lat)), points)

if __name__ == '__main__':
            Point(116.732617,39.722676).test()