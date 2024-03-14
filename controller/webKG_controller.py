import json
import datetime
from flask import Blueprint,url_for,request,render_template,session,redirect
from model.informationExtract import query, get_processNum

# 创建了一个蓝图对象
webKGModule = Blueprint('webKG',__name__)

"""
    GET请求，带参数
"""
@webKGModule.route("/informationExaction",methods=["GET"])
def get_information():
    # 默认返回内容
    return_dict = {'return_code': '200', 'return_info': '抽取成功', 'result': None}
    # 判断入参是否为空
    if len(request.args) == 0:
        return_dict['return_code'] = '5004'
        return_dict['return_info'] = '请求参数为空'
        return json.dumps(return_dict, ensure_ascii=False)
    # 获取传入的params参数
    get_data = request.args.to_dict()
    entity = get_data.get('entity')
    dataDic = query(entity)
    return_dict['result'] = dataDic
    return json.dumps(return_dict, ensure_ascii=False)

@webKGModule.route("/getProcess",methods=["GET"])
def get_process():
    # 默认返回内容
    return_dict = {'return_code': '200', 'return_info': 'success', 'result': None}
    # 判断入参是否为空
    if len(request.args) == 0:
        return_dict['return_code'] = '5004'
        return_dict['return_info'] = '请求参数为空'
        return json.dumps(return_dict, ensure_ascii=False)
    # 获取传入的params参数
    get_data = request.args.to_dict()
    entity = get_data.get('entity')
    num = get_processNum(entity)
    return_dict['result'] = num
    return json.dumps(return_dict, ensure_ascii=False)