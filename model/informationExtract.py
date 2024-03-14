# coding:utf-8
import json
import urllib.request
import urllib.parse
from lxml import etree
import hanlp
import re
from time import sleep
import os
from kit import locationKit

from pyhanlp import HanLP
from tqdm import tqdm

AK = "yO4YYt4iKSRxORH4Ubpt5NYQP8GnXWO1"

def query(content):
    # 请求地址
    url = 'https://baike.baidu.com/item/' + urllib.parse.quote(content)
    html = getHtml(url)
    if(html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[1]/a[1]//text()')):
        if("多义词" in ''.join([item.strip('\n') for item in html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[1]/a[1]//text()')])):
            print("该词为多义词")
            # 选取第一个为抽取对象
            paramUrl = html.xpath('/html/body/div[3]/div[2]/div/div[1]/ul/li[1]/div/a/@href')[0]
            url = 'https://baike.baidu.com' + str(paramUrl)
            html = getHtml(url)
    # 获得实体百度百科图片
    img_link = imgExtract(html)
    # 获得实体简介
    introduction = introductionExtract(html)
    if introduction == '':
        return
    print("实体简介：%s" % introduction)
    # 获得实体属性
    attributes = attributesExtract(html)
    print("实体属性：%s" % str(attributes))
    print("实体属性个数：%s" % len(attributes))
    # 获得实体关系
    relation = relationExtract(html)
    print("实体关系：%s" % str(relation))
    print("实体关系个数：%s" % len(relation))
    # 获得时空线
    timeline = ''
    if introduction != '':
        print("开始抽取时空线......请耐心等待")
        timeline = timeLineExtract(html, content)
        for node in timeline:
            if node[1] != '未知':
                # print(node[1])
                if '、' in node[1]:
                    lo, la = locationKit.get_position(node[1].split('、')[0], AK)
                else:
                    lo, la = locationKit.get_position(node[1], AK)
                location = str(lo) + ',' + str(la)
            else:
                location = str(0) + ',' + str(0)
            node.append(location)
        print("时空线：%s" % str(timeline))
        print("时空节点个数：%s" % len(timeline))
    dataDic = {"introduction":introductionExtract(html),
               "attributes":attributesExtract(html),
               "relation":relationExtract(html),
               "timeLine":timeline}
    attributesSet = dataDic['attributes']
    dicPerson = ['知名校友','创办人','主编','社长','司令员','师长','现任总书记','总指挥','领导者','相关人物', '主要指挥官', '主要人物', '主要人员', '总设计师', '主要领导人', '领导人', '相关领导人', '指挥官','代表人物','总书记','开创者']
    dicLocation = ['成立地点','举行地点','发生地点','出生地','出生地点', '籍贯', '地点','爆发地点','创建地点']
    dicDate = ['举行时间','召开时间','创刊时间','改编时间','成立日期','成立','出生日期', '逝世日期','发生时间','开始时间', '结束时间','发起时间','成立时间','召开时间','创建时间','创办时间']
    dicOrganization = ['所属党派','所属组织','隶属','所属']
    dicEvent = ['大事件']

    relationSet = dataDic['relation'].copy()
    dataDic['relation'].clear()
    dataDic['relation']['person'] = {}
    dataDic['relation']['person'].update(relationSet)
    # dataDic['relation']['person'] = dataDic['relation']
    dataDic['relation']['location'] = {}
    dataDic['relation']['date'] = {}
    dataDic['relation']['organization'] = {}
    dataDic['relation']['event'] = {}
    for key in list(attributesSet.keys()):
        if key in dicPerson:
            value = attributesSet.get(key).strip('等')
            if key not in dataDic['relation']['person'].keys():
                if '、' in value:
                    for i in range(0, len(value.split('、'))):
                        dataDic['relation']['person'][key + str(i)] = value.split('、')[i]
                elif ',' in value:
                    for i in range(0, len(value.split(','))):
                        dataDic['relation']['person'][key + str(i)] = value.split(',')[i]
                else:
                    dataDic['relation']['person'][key] = value
                # dataDic['relation'][key] = attributesSet.get(key)
            del dataDic['attributes'][key]

        if key in dicLocation:
            value = attributesSet.get(key).strip('等')
            if key not in dataDic['relation']['location'].keys():
                if '、' in value:
                    for i in range(0, len(value.split('、'))):
                        dataDic['relation']['location'][key + str(i)] = value.split('、')[i]
                elif ',' in value:
                    for i in range(0, len(value.split(','))):
                        dataDic['relation']['location'][key + str(i)] = value.split(',')[i]
                else:
                    dataDic['relation']['location'][key] = value
                # dataDic['relation'][key] = attributesSet.get(key)
            del dataDic['attributes'][key]

        if key in dicDate:
            value = attributesSet.get(key).strip('等')
            if key not in dataDic['relation']['date'].keys():
                if '-' in value:
                    dataDic['relation']['date'][key] = value.split('-')[0]
                elif '至' in value:
                    dataDic['relation']['date'][key] = value.split('至')[0]
                else:
                    dataDic['relation']['date'][key] = value
                # dataDic['relation'][key] = attributesSet.get(key)
            del dataDic['attributes'][key]

        if key in dicOrganization:
            value = attributesSet.get(key).strip('等')
            if key not in dataDic['relation']['organization'].keys():
                if '、' in value:
                    for i in range(0, len(value.split('、'))):
                        dataDic['relation']['organization'][key + str(i)] = value.split('、')[i]
                elif ',' in value:
                    for i in range(0, len(value.split(','))):
                        dataDic['relation']['organization'][key + str(i)] = value.split(',')[i]
                else:
                    dataDic['relation']['organization'][key] = value
                # dataDic['relation'][key] = attributesSet.get(key)
            del dataDic['attributes'][key]

        if key in dicEvent:
            value = attributesSet.get(key).strip('等')
            if key not in dataDic['relation']['event'].keys():
                if '、' in value:
                    for i in range(0, len(value.split('、'))):
                        dataDic['relation']['event'][key + str(i)] = value.split('、')[i]
                elif ',' in value:
                    for i in range(0, len(value.split(','))):
                        dataDic['relation']['event'][key + str(i)] = value.split(',')[i]
                else:
                    dataDic['relation']['event'][key] = value
                # dataDic['relation'][key] = attributesSet.get(key)
            del dataDic['attributes'][key]

    return dataDic

def getHtml(url):
    # 请求头部
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 利用请求地址和请求头部构造请求对象
    req = urllib.request.Request(url=url, headers=headers, method='GET')
    # 发送请求，获得响应
    response = urllib.request.urlopen(req)
    # 读取响应，获得文本
    text = response.read().decode('utf-8')
    # 构造 _Element 对象
    html = etree.HTML(text)
    return html

def summaryExtract(content,text):
    # 自动摘要
    return content+":"+ str(HanLP.extractSummary(text, 1)[0])

def removeReference(text):
    # 正则去引用
    pattern = r'\[[^()]*\]'
    text = re.sub(pattern, '', ''.join(text.strip('\n').replace('\xa0', '').replace('\n', '')))
    return text

def introductionExtract(html):
    # 使用 xpath 匹配数据，得到匹配字符串列表
    introduction_list = html.xpath(
        '//div[contains(@class,"lemma-summary") or contains(@class,"lemmaWgt-lemmaSummary")]//text()')
    # 过滤数据，去掉空白
    introduction_list_after_filter = [item.strip('\n') for item in introduction_list]
    # 正则去引用
    pattern = r'\[[^()]*\]'
    introductionSentence = re.sub(pattern, '', ''.join(introduction_list_after_filter))
    # 将字符串列表连成字符串并返回
    return introductionSentence

def imgExtract(html):
    # 使用 xpath 匹配数据，得到匹配字符串列表
    img_list = html.xpath(
        '//div[contains(@class,"summary-pic")]//a//img//@src')
    # 过滤数据，去掉空白
    # / html / body / div[3] / div[2] / div / div[2] / div[1] / a / img
    img_list_after_filter = [item.strip('\n') for item in img_list]
    # 正则去引用
    pattern = r'\[[^()]*\]'
    img_link = re.sub(pattern, '', ''.join(img_list_after_filter))
    # 将字符串列表连成字符串并返回
    return img_link

def attributesExtract(html):
    # 使用 xpath 匹配数据，得到匹配字符串列表
    attributes_list = html.xpath(
        '//div[contains(@class,"basic-info J-basic-info cmn-clearfix")]/*')
    attributes_dict = {}
    for attributes_list_side in attributes_list:
        for i in range(0, len(attributes_list_side)):
            if('dt' == attributes_list_side[i].tag and 'dd' == attributes_list_side[i+1].tag):
                key = [item.strip('\n').replace('\xa0','') for item in attributes_list_side[i].xpath('.//text()')]
                value = [item.strip('\n').replace('\xa0','') for item in attributes_list_side[i+1].xpath('.//text()')]
                attributes_dict.update({''.join(key): removeReference(''.join(value))})
    # 过滤数据，去掉空白
    # attributes_list_after_filter = [item.strip('\n').replace('&nbsp','') for item in attributes_list]
    # 将字符串列表连成字符串并返回
    return attributes_dict

def relationExtract(html):
    # 使用 xpath 匹配数据，得到匹配字符串列表
    relation_list = html.xpath('//div[@class="lemma-relation-module viewport"]/ul/li')
    relation_dict = {}
    for relation_item in relation_list:
        a = relation_item.xpath('./a/div/span[1]//text()')
        key = [item for item in relation_item.xpath('./a/div/span[1]//text()')]
        value = [item for item in relation_item.xpath('./a/div/span[2]//text()')]
        relation_dict.update({''.join(key): ''.join(value)})
    return relation_dict

def timeLineExtract(html,content):
    lineList = []
    pageList = html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[@class="para"]')
    for page_item in tqdm(pageList):
        timeItemList = [item for item in page_item.xpath('.//text()')]
        timeItem = ''
        for i in timeItemList:
            timeItem += i
        # 正则去引用
        pattern = r'\[[^()]*\]'
        lineItem = removeReference(timeItem)

        HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 世界最大中文语料库
        hanLPResult = HanLP(lineItem, tasks="ner/ontonotes")
        nerResult = hanLPResult.to_dict()["ner/ontonotes"]
        dateList = []
        locationList = []
        for nerItem in nerResult:
            if ('DATE' == list(nerItem)[1]):
                dateList.append(list(nerItem)[0])
            elif ('GPE' == list(nerItem)[1]):
                locationList.append(list(nerItem)[0])
        locationList = list(set(locationList))
        textList = lineItem.split("。")
        for text in textList:
            if (content in text or len(content)>3):
                for date in dateList:
                    if (date in text and "年" in date):
                        Lastlocation = ""
                        for location in locationList:
                            if (location in text):
                                Lastlocation = Lastlocation + location + "、"
                        summary = summaryExtract(content,text)
                        if ("" == Lastlocation):
                            lineList.append([date, "未知", text, summary])
                            break
                        else:
                            lineList.append([date, Lastlocation[0:len(Lastlocation) - 1], text, summary])
                            break
                    else:
                        pass
            else:
                pass
        sleep(0.01)

    return lineList

def get_processNum(content):
    # 请求地址
    url = 'https://baike.baidu.com/item/' + urllib.parse.quote(content)
    html = getHtml(url)
    if (html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[1]/a[1]//text()')):
        if ("多义词" in ''.join(
                [item.strip('\n') for item in html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[1]/a[1]//text()')])):
            print("该词为多义词")
            # 选取第一个为抽取对象
            paramUrl = html.xpath('/html/body/div[3]/div[2]/div/div[1]/ul/li[1]/div/a/@href')[0]
            url = 'https://baike.baidu.com' + str(paramUrl)
            html = getHtml(url)
    # 获得时空线Num
    pageList = html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[@class="para"]')
    return len(pageList)

def transfer2JSON(directory,content, dataDic):
    json_str = json.dumps(dataDic, indent=4, ensure_ascii=False)
    os.makedirs(r"E:\projects\2022computer-design\AutoKG_Flask_DEV1.0-master\json\history\\" + directory,exist_ok=True)
    path = r"E:\projects\2022computer-design\AutoKG_Flask_DEV1.0-master\json\history\\" + directory + "\\" + content +'_BaiduData.json'
    with open(path, 'w',encoding='utf-8',errors='ignore') as json_file:
        print("开始写入内容")
        json_file.write(json_str)
        print("写入结束")
    print("{}爬虫数据已持久化为json，路径为：{}".format(content,path))

if __name__ == '__main__':
    # 问答
    while (True):
        content = input('查询词语：')
        dataDic = query(content)
        print(dataDic)
        transfer2JSON('test',content,dataDic)
    # 测试
    # query("孙中山")
    # print(summaryExtract("孙中山", "1905年（光绪三十一年）在比、德、法等国的留学生中建立了革命团体，在此期间也与国内的革命团体和革命志士建立了联系。"))
