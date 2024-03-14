# coding:utf-8
import json
import urllib.request
import urllib.parse
from lxml import etree
import hanlp
import re
from time import sleep
from sys import argv

from pyhanlp import HanLP
from tqdm import tqdm

procressNum = 0

def QAnalysis(question):
    HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 世界最大中文语料库
    # 命名实体识别ner
    hanLPResult = HanLP(question, tasks=["tok/coarse","ner/msra", "pos/ctb"])  # "srl"
    tok = hanLPResult.to_dict()["tok/coarse"]
    nerMsra = hanLPResult.to_dict()["ner/msra"]
    ner = [item for item in nerMsra]
    ctb = hanLPResult.to_dict()["pos/ctb"]
    print(tok)
    print(ner)
    print(ctb)
    QClassify(question,tok,ctb,ner)

def QClassify(question,tok,ctb,ner):
    # 是否多意图
    if(question.count("？")==0):
        print("未检测到问题")
    elif(question.count("？")==1):
        print("单意图问题")
        if(len(ner)==1):
            print("查实体")
            if(ctb.count("NN") == 1):
                print("单跳查询")
                try:
                    index = ctb.index("NN")
                    node = list(ner[0])[0]
                    relax = tok[index]
                    print("要查询的内容为:<{},{},?>".format(node,relax))

                    #添加查询语句，node为中心节点的名称，relax为关系的名称，查询之后返回
                except:
                    print("无法识别出要检索的关系")
            elif(ctb.count("NN")>1):
                print("多跳链式查询")
                indexList = [i for i in range(len(ctb)) if ctb[i] == "NN"]
                node = list(ner[0])[0]
                text = "要查询的内容为:"+ node
                for i in  indexList:
                    text += str(("的" + tok[i]))
                    # 添加查询语句，node为中心节点的名称，indexList为关系的名称，需做多层级的子节点关系查询之后返回
                print(text)
        elif(len(ner)==2):
            if(("P" in ctb) or ("VC" in ctb)):
                if("VV" in ctb):
                    if(ctb.index("NN")):
                        relax = tok[ctb.index("NN")]
                    else:
                        relax = "未知关系"
                    print("查两个实体的关系/属性交集")
                    print("要查询的内容为:<{},{},?> 交集<{},{},?>".format(ner[0], relax, ner[1], relax))
                    # 添加查询语句，ner[0]为中心节点1的名称，ner[1]中心节点2的名称，查询之后返回二者共有的关系relax所对应的节点
                else:
                    print("查两个实体的关系/属性")
                    print("要查询的内容为:<{},?,{}>".format(ner[0], ner[1]))
                    # 添加查询语句，ner[0]为中心节点1的名称，ner[1]中心节点2的名称，查询之后返回二者关系的名称

            elif("CC" in ctb):
                index = ctb.index("NN")
                relax = tok[index]
                if(tok[index] == "关系"):
                    print("查两个实体的关系/属性")
                    print("要查询的内容为:<{},{},{}>".format(ner[0], relax, ner[1]))
                    # 添加查询语句，ner[0]为中心节点1的名称，ner[1]中心节点2的名称，查询之后返回二者关系的名称
                else:
                    print("查两个实体的关系/属性交集")
                    print("要查询的内容为:<{},{},?> 交集<{},{},?>".format(ner[0], relax, ner[1], relax))
                    # 添加查询语句，ner[0]为中心节点1的名称，ner[1]中心节点2的名称，查询之后返回二者共有的关系relax所对应的节点
        else:
            print("未知问题类型")
    else:
        print("多意图问题")


if __name__ == '__main__':
    # 问答
    while (True):
        question = input('用户问题：')
        QAnalysis(question)

    # #
    # answer = QAnalysis(argv[1])  # sys.argv[0]表示当前运行的.py文件的名字，sys.arg[1]才是从外面传进来的参数，如果有需要，可以增加sys.arg[2]，sys.arg[3].......，以此类推
    # print(answer)


