这是一个爬取互联网开放的POI数据以及POI边界坐标代码集，包括高德和百度地图，可以爬取指定经纬度范围或者指定城市/省份的POI数据以及POI边界坐标(目前仅限百度)。

## 相关网站
- 百度地图开放平台：http://lbsyun.baidu.com/
- 百度地图开放平台-POI地点检索接口文档：http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
- 高德地图开放平台：https://lbs.amap.com/
- 高德地图开放平台-POI地点检索接口文档：https://lbs.amap.com/api/webservice/guide/api/search
- Uber小姐姐开发的一个超级炫酷的地图可视化平台：https://kepler.gl/   (也欢迎访问我的网站上的地址：http://www.mapboxx.cn:8080/ ，功能一样的)
- 开放路网地图：https://www.openstreetmap.org/

## 代码目录介绍
#### baidu
百度地图POI数据爬取(WGS84坐标系)

- app.py 程序入口文件
- data 存放爬取的POI数据目录
- boundary 百度POI边界坐标爬取目录
   - POI边界爬取结果存放目录

#### gaode
高德地图POI数据爬取

- poi-city 划分行政区划来爬取指定城市范围内的POI数据
- poi-pology 划分矩形网格来爬取指定城市的POI数据
- poi-province 爬取指定省份内的POI数据
- 高德地图POI分类编码表.xlsx 
- 高德地图城市编码表.xlsx


## 公共约定
- app.py均为程序入口文件，修改配置以及执行都只需要关注该文件即可
- transCoordinateSystem.py 为坐标转换代码，支持高德、百度、WGS84三种坐标系互转
- POI分类可以用编码，也可以用对应的中文关键字

## 运行步骤

##### 运行环境安装

- 开发语言：python 3+     推荐安装anaconda，集成了许多常用的第三方库
- 开发工具：pycharm，其他的开发工具也行，看自己爱好
- 一些可能需要安装的第三方库：
    - pandas
    - urllib
    - xpinyin
    - requests

具体可以先运行看缺少哪些库，然后使用pip install进行安装。




##### 修改配置
在各个目录下的app.py中修改爬取参数配置，需要修改的地方均以TODO 标识，各个参数在代码前的注释均有介绍，最主要是需要设置需要爬取的POI类型、爬取的范围（城市/省/经纬度范围）、对应的AK密钥。   其中AK密钥可在百度开放平台（
http://lbsyun.baidu.com/）或者高德地图开放平台(
https://lbs.amap.com/)上申请。



##### 启动
执行命令`python app.py` 即可开始爬取数据，不过由于范围大小、以及POI数量多少不一样，爬取花费的时间也不一样，范围越大，POI数量越多，花费的时间越长。比如爬取省的花费时间比爬一个城市花费的要长，爬取餐厅比爬图书馆花费的时间长。  



#### 常见问题：
- 启动后报错："no module named xxxxx",这是因为你的Python环境里面没有相应的第三方模块，可以使用命令"pip install XXX"安装相应的模块，安装成功后重启即可，特别需要注意的是在`gaode/poi-province`中的代码需要安装`shapefile`模块，其安装命令名为`pip install pyshp`，如果仍然不懂，可以把报错信息粘贴到百度搜索。

##### 附录
有什么优化建议或者发现问题欢迎向我提问，POI，宜出行都可以，qq：917961898












   