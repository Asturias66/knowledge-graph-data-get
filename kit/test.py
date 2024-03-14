import json
import urllib

import requests

def similirity(word1,word2):
    token_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
    # 1.获取token
    api_key='mVgGzKyWGzGnROZbQoLYmGDY'
    api_secert='UIGRMcCUw8AaxLqvVNlQGGhGp7E7oS30'

    token_url = token_url % (api_key, api_secert)

    r_str = urllib.request.urlopen(token_url).read()
    r_str = str(r_str, encoding="utf-8")
    token_data = json.loads(r_str)
    token_str = token_data['access_token']

    url_all='https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim?access_token='+str(token_str)

    data2={'word_1': word1, 'word_2': word2}
    post_data = json.dumps(data2)
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko','Content-Type':'application/json'}
    req = urllib.request.Request(url=url_all, data=bytes(post_data,encoding="gbk"),headers=header_dict)
    res = urllib.request.urlopen(req).read()
    # print(res)
    r_data= str(res, encoding="GBK")
    # print(r_data)
    res=json.loads(r_data)
    print(res)
    print([word1,word2,res['score']])

if __name__ == '__main__':
    # APIKey = 'mVgGzKyWGzGnROZbQoLYmGDY'
    # SecretKey = 'UIGRMcCUw8AaxLqvVNlQGGhGp7E7oS30'
    #
    # word1 = "组织者"
    # word2 = "负责人"
    #
    # similirity(word1,word2)

    import synonyms

    synlst = synonyms.display('老婆')

    # # client_id 为官网获取的AK， client_secret 为官网获取的SK
    # host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={APIKey}&client_secret={SecretKey}'
    # response = requests.get(host)
    # if response:
    #     resp_json = response.json()
    #     # print(resp_json)
    #     token = resp_json['access_token']
    #     # print(token)
    #
    # url = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim?access_token=' + str(token)
    #
    # data2 = {'word_1': word1, 'word_2': word2}
    # post_data = json.dumps(data2)
    # header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    #                'Content-Type': 'application/json'}
    # # req = urllib.request.Request(url=url_all, data=bytes(post_data, encoding="gbk"), headers=header_dict)
    # # res = urllib.request.urlopen(req).read()
    # # # print(res)
    # # r_data = str(res, encoding="GBK")
    # # # print(r_data)
    # # res = json.loads(r_data)
    # # print([word1, word2, res['score']])
    #
    # # url = f'https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim?access_token={token}'
    # res = requests.get(url,headers = header_dict, params = data2)
    # val = res.json()
    # print(val)
    # # endpoint = 'https://aip.baidubce.com'
    # # ak = ''
    # # sk = ''
    # # config = bce_client_configuration.BceClientConfiguration(credentials=bce_credentials.BceCredentials(ak, sk),
    # #                                                          endpoint=endpoint)
    # # client = ApiCenterClient(config)
    # # res = client.demo()
    # # print(res.__dict__['raw_data'])