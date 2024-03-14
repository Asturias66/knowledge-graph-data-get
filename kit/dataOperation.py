import json
import os
import urllib

from model.informationExtract import getHtml, imgExtract

fileDirectoryPath = "E:\\projects\\2022computer-design\\dataGet\\data\\history"

def getAllFiles(folder):
    filepath_list = []
    for root,folder_names, file_names in os.walk(folder):
        for file_name in file_names:
            file_path = root + os.sep + file_name
            filepath_list.append(file_path)
    # file_path = sorted(file_path, key=str.lower)
    return filepath_list

def query(content):
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
    # 获得实体百度百科图片
    img_link = imgExtract(html)
    return img_link

def operation():
    fileList = getAllFiles(fileDirectoryPath)
    for filePath in fileList:
        print(filePath)
        fileName = filePath.split("\\")[-1].split("_")[0]
        file_object = open(filePath, encoding='utf-8')
        try:
            all_the_text = file_object.read()
            # print(all_the_text)
            imgLink = query(fileName)
            jsonData = json.loads(all_the_text)
            print(jsonData['attributes'])
            jsonData['attributes']['img'] = imgLink
            json_str = json.dumps(jsonData, indent=4, ensure_ascii=False)
        finally:
            file_object.close()
            with open(filePath, 'w', encoding='utf-8', errors='ignore') as json_file:
                json_file.write(json_str)




if __name__ == '__main__':
    operation()