import json
import re
import copy
import time
import os

import hanlp
from pyhanlp import HanLP as pyHanlp
from hanlp_restful import HanLPClient
HanLP_rest = HanLPClient('https://www.hanlp.com/api', auth="NTcxQGJicy5oYW5scC5jb206dFJHcUFSNHpWRmNsWmw0bQ==", language='zh') # auth不填则匿名，zh中文，mul多语种
from tqdm import tqdm
from informationExtract import query, get_processNum

def bookContent_List(book_url):
    # 读取文件，消除换行，并按句号切句
    try:
        f = open(book_url, encoding='utf-8',errors='ignore')
    except:
        f = open(book_url, encoding='utf-8',errors='ignore')

    data = f.read().strip().replace('','').replace('\r','').replace(".", "。")
    # 按换行来做切分
    dataList = re.split('\n',data)
    f.close()
    return dataList

    # f2 = open(book_url[0:-4]+"modified"+book_url[-4:],"w",encoding='utf-8')
    # for i in tqdm(dataList):
    #     f2.write(i)
    #     f2.write("\n")
    # f2.close()

def summaryExtract(content,text):
    # 自动摘要
    return content+":"+ str(pyHanlp.extractSummary(text, 1)[0])

def textProcess(txt):
    data = txt.strip().replace('', '').replace('\r', '').replace(".", "。")
    # 按换行来做切分
    dataList = re.split('\n', data)
    print(dataList)
    return dataList


def bookContentProcess(book_url):
    textList = bookContent_List(book_url)  # 拿到文章list
    # txtList = []
    # for sentence in tqdm(textList):
    #     try:
    #         e = HanLP_rest.coreference_resolution(sentence)
    #         time.sleep(1)
    #         ference = e['clusters']
    #         tokens = e['tokens']
    #         # print(len(ference))
    #         for i in ference:
    #             word = i[0][0]
    #             # print(word)
    #             for j in i:
    #                 if ("他" == j[0] or "她" == j[0] or "我" == j[0] or "你" == j[0]):
    #                     # print(j[0])
    #                     tokens[j[1]] = word
    #             # print(i)
    #         # 打印代词替换后的txt
    #         content_txt = ""
    #         for i in tokens:
    #             content_txt += i
    #         txtList.append(content_txt)
    #     except:
    #         pass
    return textList

def nerProcess(txt):
    HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 世界最大中文语料库
    # 命名实体识别ner
    hanLPResult = HanLP(txt, tasks=["ner/msra", "ner/ontonotes", "pos"])  # "srl"
    nerMsra = hanLPResult.to_dict()["ner/msra"]
    nerMsra = [item for item in nerMsra]
    nerOntonotes = hanLPResult.to_dict()["ner/ontonotes"]
    nerOntonotes = [item for item in nerOntonotes]
    # print("nerMsra:{}".format(nerMsra))
    # print("nerOntonotes:{}".format(nerOntonotes))
    ner = list(set(nerMsra + nerOntonotes))
    ner = [list(item) for item in ner]

    # 候选ner清洗
    pNer = []
    for entity in ner:
        # 过滤长度小于等于1的实体
        if (len(entity[0]) <= 1):
            # print(entity)
            pass
        # 去除'ORG'标签实体
        elif (entity[1] == 'ORG' or entity[1] == 'AREA' or entity[1] == 'FAC'):
            pass
        # GPE并入LOCATION
        elif (entity[1] == 'GPE' or entity[1] == 'LOC'):
            entity[1] = 'LOCATION'
        # 过滤DATE无用的实体
        elif (entity[1] == "DATE"):
            if ("年" not in entity[0]):
                # print(entity)
                pass
            else:
                pNer.append(entity)
        # 过滤无用类别实体
        elif (entity[1] in ["AGE", "MONEY", "CARDINAL", "INTEGER", "QUANTITY", "TIME", "PERCENT", "DURATION",
                            "FREQUENCY", "ORDINAL", 'LENGTH', 'NORP', 'WORK_OF_ART',"FRACTION",  "WEIGHT", "TEMPERATURE", "PRODUCT"]):
            # print(entity)
            pass
        else:
            pNer.append(entity)
    return pNer

def getTimeLine(entitiesDic,txt):
    # 时空线抽取
    lineList = []
    print(entitiesDic.keys())
    dateList = entitiesDic["DATE"]
    locationList = entitiesDic["LOCATION"]
    textList = txt.split("。")
    for text in textList:
        for date in dateList:
            if (date in text):
                Lastlocation = ""
                for location in locationList:
                    if (location in text):
                        Lastlocation = Lastlocation + location + "、"
                if ("" == Lastlocation):
                    lineList.append([date, "未知", text])
                    break
                else:
                    lineList.append([date, Lastlocation[0:len(Lastlocation) - 1], text])
                    break
            else:
                pass

    personLineListDic = {}
    eventLineListDic = {}
    organizationLineListDic = {}
    for item in lineList:
        for people in entitiesDic["PERSON"]:
            if people in item[2]:
                summary = summaryExtract(people, item[2])
                peopleItem = copy.deepcopy(item)
                peopleItem.append(summary)
                if (people in personLineListDic.keys()):
                    personLineListDic[people].append(peopleItem)
                else:
                    personLineListDic.update({people: [peopleItem]})
                continue
        for event in entitiesDic["EVENT"]:
            if event in item[2]:
                summary = summaryExtract(event, item[2])
                peopleItem = copy.deepcopy(item)
                peopleItem.append(summary)
                if (event in personLineListDic.keys()):
                    eventLineListDic[event].append(peopleItem)
                else:
                    eventLineListDic.update({event: [peopleItem]})
                continue
        for organization in entitiesDic["ORGANIZATION"]:
            if organization in item[2]:
                summary = summaryExtract(organization, item[2])
                organizationItem = copy.deepcopy(item)
                organizationItem.append(summary)
                if (organization in organizationLineListDic.keys()):
                    organizationLineListDic[organization].append(organizationItem)
                else:
                    organizationLineListDic.update({organization: [organizationItem]})
                continue
    return personLineListDic,eventLineListDic,organizationLineListDic

def fileTramsformer(book_url):
    entitiesDic = {"ORGANIZATION":[], "PERSON":[], "LOCATION":[], "DATE":[], "EVENT":[]}
    personLineDic = {}
    eventLineDic = {}
    organizationLineDic = {}
    print("正在文本清洗....请稍等")
    txtList = bookContentProcess(book_url)
    print("正在实体抽取....请稍等")
    for txt in tqdm(txtList):
        try:
            pNer = nerProcess(txt)
            # print(pNer)
            for entity in pNer:
                if (entity[1] in entitiesDic.keys()):
                    if (entity[0] not in entitiesDic[entity[1]]):
                        entitiesDic[entity[1]].append(entity[0])
                        dataDic = query(entity[0])
                        if dataDic == None:
                            continue
                        dataDic['type'] = entity[1]
                        transfer2JSON(entity[1],entity[0],dataDic)
                else:
                    entitiesDic.update({entity[1]: [entity[0]]})
                    dataDic = query(entity[0])
                    if dataDic == None:
                        continue
                    dataDic['type'] = entity[1]
                    transfer2JSON(entity[1],entity[0], dataDic)

            personLineListDic, eventLineListDic, organizationLineListDic = getTimeLine(entitiesDic, txt)
            personLineDic.update(personLineListDic)
            eventLineDic.update(eventLineListDic)
            organizationLineDic.update(organizationLineListDic)
        except:
            pass

    print("全部类别实体entitiesDic:{}".format(entitiesDic))
    print("实体抽取完毕，共抽取ORGANIZATION:{}，PERSON：{}，LOCATION：{}，DATE：{}，EVENT:{}"
          .format(len(entitiesDic["ORGANIZATION"]),len(entitiesDic["PERSON"]),len(entitiesDic["LOCATION"]),len(entitiesDic["DATE"]),len(entitiesDic["EVENT"])))
    print("personLineDic:{}".format(personLineDic))
    print("人物时空线抽取完毕，共涉及:{}个人物实体，{}条时空线".format(len(personLineDic.keys()),len(personLineDic.items())))
    print("eventLineDic:{}".format(eventLineDic))
    print("大事件时空线抽取完毕，共涉及:{}个大事件实体，{}条时空线".format(len(eventLineDic.keys()),len(eventLineDic.items())))
    print("organizationLineDic:{}".format(organizationLineDic))
    print("组织机构时空线抽取完毕，共涉及:{}个组织机构实体，{}条时空线".format(len(organizationLineDic.keys()),len(eventLineDic.items())))
    dataDic = {"entitiesDic":entitiesDic,
               "personLineDic":personLineDic,
               "eventLineDic":eventLineDic,
               "organizationLineDic":organizationLineDic}
    return dataDic

def textTramsformer(txt):
    entitiesDic = {"ORGANIZATION":[], "PERSON":[], "LOCATION":[], "DATE":[], "EVENT":[]}
    personLineDic = {}
    eventLineDic = {}
    organizationLineDic = {}
    print("正在文本清洗....请稍等")
    txtList = textProcess(str(txt))
    print("正在实体抽取....请稍等")
    for txt in tqdm(txtList):
        try:
            pNer = nerProcess(txt)
            for entity in pNer:
                if (entity[1] in entitiesDic.keys()):
                    if (entity[0] not in entitiesDic[entity[1]]):
                        entitiesDic[entity[1]].append(entity[0])
                else:
                    entitiesDic.update({entity[1]: [entity[0]]})

            personLineListDic, eventLineListDic, organizationLineListDic = getTimeLine(entitiesDic, txt)
            personLineDic.update(personLineListDic)
            eventLineDic.update(eventLineListDic)
            organizationLineDic.update(organizationLineListDic)
        except:
            pass

    print("全部类别实体entitiesDic:{}".format(entitiesDic))
    print("实体抽取完毕，共抽取ORGANIZATION:{}，PERSON：{}，LOCATION：{}，DATE：{}，EVENT:{}"
          .format(len(entitiesDic["ORGANIZATION"]),len(entitiesDic["PERSON"]),len(entitiesDic["LOCATION"]),len(entitiesDic["DATE"]),len(entitiesDic["EVENT"])))
    print("personLineDic:{}".format(personLineDic))
    print("人物时空线抽取完毕，共涉及:{}个人物实体，{}条时空线".format(len(personLineDic.keys()),len(personLineDic.items())))
    print("eventLineDic:{}".format(eventLineDic))
    print("大事件时空线抽取完毕，共涉及:{}个大事件实体，{}条时空线".format(len(eventLineDic.keys()),len(eventLineDic.items())))
    print("organizationLineDic:{}".format(organizationLineDic))
    print("组织机构时空线抽取完毕，共涉及:{}个组织机构实体，{}条时空线".format(len(organizationLineDic.keys()),len(eventLineDic.items())))
    dataDic = {"entitiesDic":entitiesDic,
               "personLineDic":personLineDic,
               "eventLineDic":eventLineDic,
               "organizationLineDic":organizationLineDic}
    return dataDic

def bookTransfer2JSON(bookName, dataDic):
    json_str = json.dumps(dataDic, indent=4, ensure_ascii=False)
    path = r"E:\projects\2022computer-design\AutoKG_Flask_DEV1.0-master\json\\" + bookName+ '_BookData.json'
    with open(path, 'w', encoding='utf-8',errors='ignore') as json_file:

        json_file.write(json_str)
    print("{}知识数据已持久化为json，路径为：{}".format(bookName,path))

def txtTransfer2JSON(dataDic):
    json_str = json.dumps(dataDic, indent=4, ensure_ascii=False)
    print("返回的json：{}".format(json_str))
    return json_str
    # path = r"D:\AutoKG\BOOK2KG\JsonCenter\\" + bookName+ '_BookData.json'
    # with open(path, 'w', encoding='utf-8') as json_file:
    #     json_file.write(json_str)
    # print("{}知识数据已持久化为json，路径为：{}".format(bookName,path))

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
    while (True):
        bookName = input('文本名字：') # D:\AutoKG\BOOK2KG\温情的毛泽东.content_txt
        book_url = r"E:\projects\2022computer-design\AutoKG_Flask_DEV1.0-master\txt\\" + bookName
        dataDic = fileTramsformer(book_url)
        bookTransfer2JSON(bookName, dataDic)

    # while (True):
    #     bookContent = input('请输入要抽取的文本：')  # D:\AutoKG\BOOK2KG\温情的毛泽东.content_txt
    #     dataDic = textTramsformer(bookContent)
    #     txtTransfer2JSON(dataDic)

