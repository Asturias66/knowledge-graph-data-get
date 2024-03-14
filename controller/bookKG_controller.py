import datetime
import json
import os
from flask import request
from flask import Blueprint,url_for,render_template,session,redirect
from model.KG_tramsformer import textTramsformer, txtTransfer2JSON
from werkzeug.utils import secure_filename

# 创建了一个蓝图对象
bookKGModule = Blueprint('bookKG',__name__)

"""
    GET请求，带参数
"""
@bookKGModule.route("/fileUpload",methods=["POST"])
def upload():
    """处理上传文件"""
    # 接收post请求上传的文件
    file = request.files['file']
    file_content = file.read()
    file_content = file_content.decode("utf-8")
    print('答案内容为：', file_content)

    if file is None:
        # 表示没有发送文件
        return "error"

    return file_content


"""
    GET请求，带参数
"""
@bookKGModule.route("/txtExtraction",methods=["GET"])
def write():
    # 默认返回内容
    return_dict = {'return_code': '200', 'return_info': '抽取成功', 'result': None}
    # 判断入参是否为空
    if len(request.args) == 0:
        return_dict['return_code'] = '5004'
        return_dict['return_info'] = '请求参数为空'
        return json.dumps(return_dict, ensure_ascii=False)
    # 获取传入的params参数
    get_data = request.args.to_dict()
    txt = get_data.get('content')
    dataDic = textTramsformer(txt)
    return_dict['result'] = dataDic
    return json.dumps(return_dict, ensure_ascii=False)