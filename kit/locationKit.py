import pandas as pd
import requests

AK = "yO4YYt4iKSRxORH4Ubpt5NYQP8GnXWO1"  # 将刚刚获取到的AK复制到这里


def get_position(name, AK):
    url = f'http://api.map.baidu.com/geocoding/v3/?address={name}&output=json&ak={AK}'
    res = requests.get(url)
    val = res.json()
    # print(val)
    if val['status'] != 0:
        return 0,0
    retval = {'地址': name,
              '经度': val['result']['location']['lng'],
              '维度': val['result']['location']['lat'],
              '地区标签': val['result']['level'],
              '是否精确查找': val['result']['precise']}
    # print(val)
    longitude = retval['经度']
    latitude = retval['维度']
    return longitude, latitude

# lo,la = get_position('武汉',AK)
# print("经度" + str(lo))
# print("纬度" + str(la))