# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 15:15:56 2019
全国住建部 建筑业企业 (企业信息，企业资质)
运行环境：安装了 node.js环境 并安装了vue.js插件 (用于解密)
@author: 86158
"""
import time
import requests
import datetime
import json
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
import re
from datetime import datetime
import chardet
import sys
import math
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib import parse
from bson.objectid import ObjectId
import traceback
import chrome_proxy
import execjs
import math

conn=MongoClient("139.9.75.231",8635)

constructionDB_db=conn.get_database('constructionDB')
#用户名，密码，数据库
constructionDB_db.authenticate('constructionDB','ConstructionDB1408~','constructionDB')

countryWide=constructionDB_db.countryWideQual
headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
        }

publicHeaders={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
        }

def getProxy():
    proxyUrl="http://dps.kdlapi.com/api/getdps/?orderid=958321311484647&num=1&pt=1&sep=1"
    responce=requests.get(proxyUrl)
    print (responce.text)
    return responce.text
    #return '223.214.204.168:23181'

currentIP=getProxy()

def get_request(url,headers):
    global currentIP
    result_html=1
    while result_html==1:
        try:
            username = "1821359414"
            password = "mo08vvxq"
            proxies = {
                "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': currentIP},
            }
            headers['Accept-Encoding']="gzip" # 使用gzip压缩传输数据让访问更快
            detailResponce=requests.get(url,proxies=proxies,headers=headers,timeout=60)
            #detailResponce=requests.get(url,headers=headers,timeout=5)
            if detailResponce.status_code==200:
                result_html=detailResponce.text
            elif detailResponce.status_code==503 or detailResponce.status_code==400:
                print (url)
            elif detailResponce.status_code==408:#token失效
                result_html='token失效'
            else:
                print ('get---换代理ip')
                print ('当前时间：'+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                currentIP=getProxy()
                #换ip结束
                result_html=1
        except Exception:
            print ('请求的url：---'+url)
            traceback.print_exc()
            print ('get---换代理ip')
            currentIP=getProxy()
            result_html=1
    return result_html

def post_request(url,headers,condition):
    global currentIP
    result_html=1
    while result_html==1:
        try:
            username = "1821359414"
            password = "mo08vvxq"
            proxies = {
                "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': currentIP},
            }
            headers['Accept-Encoding'] = "Gzip",  # 使用gzip压缩传输数据让访问更快
            detailResponce=requests.post(url,proxies=proxies,headers=headers,data=condition,timeout=60)
            #detailResponce=requests.get(url,headers=headers,timeout=5)
            if detailResponce.status_code==200:
                result_html=detailResponce.text
            elif detailResponce.status_code==503 or detailResponce.status_code==400:
                print (url)
            elif detailResponce.status_code==408:#token失效
                result_html='token失效'
            else:
                print ('get---换代理ip')
                print ('当前时间：'+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                currentIP=getProxy()
                #换ip结束
                result_html=1
        except Exception:
            print ('请求的url：---'+url)
            traceback.print_exc()
            print ('get---换代理ip')
            currentIP=getProxy()
            result_html=1
    return result_html


def removeSymbol(companyName):
    return re.sub("[\s\\\.!/_$,%^*()（）:：+\"\'—！，。？?、~@#￥％…&“”‘’;；\|｛｝\{\}【】\[\]=\-《》<>]+", "",companyName)

#解密
def decryptRes(data):
    docjs = execjs.compile('''
    let CpytoJs=require('D:/Program Files/nodejs/node_global/node_modules/crypto-js')
    var u=CpytoJs.enc.Utf8.parse("jo8j9wGw%6HbxfFn"),
        d=CpytoJs.enc.Utf8.parse("0123456789ABCDEF");

    function Aes(data) {
        e = CpytoJs.enc.Hex.parse(data);
        n = CpytoJs.enc.Base64.stringify(e)
        return CpytoJs.AES.decrypt(n,u, {
            iv: d,
            mode: CpytoJs.mode.CBC,
            padding: CpytoJs.pad.Pkcs7
        }).toString(CpytoJs.enc.Utf8)
    }
    ''',cwd='D:/Program Files/nodejs/node_global/node_modules')
    result=docjs.call('Aes',data)
    return result

def getHttpStatus(browser):
    for responseReceived in browser.get_log('performance'):
        try:
            response = json.loads(responseReceived[u'message'])[u'message'][u'params'][u'response']
            #if response[u'url'] == browser.current_url:
            #print (response[u'status'])
            if response[u'status']==401:
                print ('ip属于被封!')
                return 401
            #elif response[u'status']==503 and '.css' not in response['url'] and '.js' not in response['url'] and '.png' not in response['url']:
            elif response[u'status']==503 or response[u'status']==400:
                return 503
        except:
            pass
    return 200

#检测ip是否可用！！
def is_use_proxyIp():
    global currentIP
    print ('检测---代理ip---'+currentIP+'---是否可用')
    # 用户名和密码(私密代理/独享代理)
    username = "1821359414"
    password = "mo08vvxq"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': currentIP},
    }
    headers = {
            "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
        }
    try:
        r=requests.get('http://httpbin.org/ip', proxies=proxies,headers=headers,timeout=60)
        print (r.status_code)
        return True
    except:
        return False

#对比两个结果
def comparison(old_result,new_result):
    #结果
    result=[]
    #得到当前时间
    current_time=int(time.time())
    
    #循环新资质
    for new in new_result:
        #颁发机构
        issu_organ=new['issu_organ']
        if "住房和城乡建设部" in issu_organ:
            new_qual_name=new['qual_name']
            #是否在老资质里出现
            is_old=False
            for old in old_result:
                old_qual_name=old['qual_name']
                
                if "住房和城乡建设部" in old['issu_organ']\
                    and old_qual_name==new_qual_name:
                    is_old=True
                    if "endTime" in old.keys():#需要看是否添加更新时间
                        #取最后一个endTime
                        fine_time=old['endTime'][-1]#时间戳
                        
                        if "newTime" not in old.keys():
                            new_list=[]
                            new_list.append(current_time)
                            new['newTime']=new_list
                            new['endTime']=old['endTime']
                        elif "newTime" in old.keys() and fine_time>old['newTime'][-1]:
                            old['newTime'].append(current_time)
                            new['newTime']=old['newTime']
                            new['endTime']=old['endTime']
                        else:
                            new['newTime']=old['newTime']
                            new['endTime']=old['endTime']
                    elif "newTime" in old.keys():
                        new['newTime']=old['newTime']
                    result.append(new)
                            
                    break
            if not is_old:
                new_list=[]
                new_list.append(current_time)
                new['newTime']=new_list
                result.append(new)
        else:
            result.append(new)
    
    for old in old_result:
        #颁发机构
        issu_organ=old['issu_organ']
        if "住房和城乡建设部" in issu_organ:
            old_qual_name=old['qual_name']
            is_new=False
            for new in new_result:
                new_qual_name=new['qual_name']
                #是否在新资质里出现
                if "住房和城乡建设部" in new['issu_organ']\
                    and old_qual_name==new_qual_name:
                    is_new=True
                    break
            if not is_new:
                if "endTime" in old.keys():
                    end_time=old['endTime'][-1]
                    if "newTime" in old.keys():
                        new_time=old['newTime'][-1]
                        if new_time>end_time:
                            old['endTime'].append(current_time)
                        
                    result.append(old)
                else:
                    end_list=[]
                    end_list.append(current_time)
                    old['endTime']=end_list
                    result.append(old)
    
    return result   

def verification_code(browser):

    #定义一个状态 标明是否出现验证码！！
    WebDriverWait(browser, 10, 1).until(
            # "//div[@class='hot-cat']" 就是我们要等待页面加载出来的元素
            # 判断某个元素中的 value 属性是否包含 了预期的字符串
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'captchaDilaog')]")))
    dialog_style=browser.find_element_by_class_name("el-dialog__wrapper").get_attribute('style')
    if 'display: none' not in dialog_style:
        red_but=browser.find_element_by_xpath("//div[contains(@class,'captchaDilaog')]//button[contains(@class,'el-button el-button--red')]")
        if is_use_proxyIp():
            red_but.click()
        else:
            raise Exception('抛出一个异常---ip不可用！')
        time.sleep(1)
        verification_code(browser)
    
    #给一个  状态 验证过程中 ip是否可用
    isnot_use_ip=True
    try:
        WebDriverWait(browser, 10, 1).until(
            # "//div[@class='hot-cat']" 就是我们要等待页面加载出来的元素
            # 判断某个元素中的 value 属性是否包含 了预期的字符串
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'yidun_popup')]")))
        
        '''WebDriverWait(browser, 10, 1).until_not(
            # "//div[@class='hot-cat']" 就是我们要等待页面加载出来的元素
            # 判断某个元素中的 value 属性是否包含 了预期的字符串
            EC.text_to_be_present_in_element_value((By.XPATH, "//div[@class='yidun_tips']"),u'加载中'))'''
        #yidun_popup--light
        dialog_style=browser.find_element_by_class_name("el-dialog__wrapper").get_attribute('style')
        yidun_style=browser.find_element_by_class_name("yidun_popup").get_attribute('style')
        
        print ('验证码的显示css:---'+yidun_style)
        if "display: block;"==yidun_style:
            #browser.maximize_window()
            yidun_controlText=browser.find_element_by_xpath("//div[@class='yidun_control']").text
            print (yidun_controlText)
            time.sleep(3)
            yidun_style=browser.find_element_by_class_name("yidun_popup").get_attribute('style')
            while "display: block;"==yidun_style or "/data/company/detail?id" not in browser.current_url:
                print ('还没验证通过！！重新验证')
                time.sleep(3)
                if getHttpStatus(browser)==401 or not is_use_proxyIp():
                    isnot_use_ip=False
                    break
                yidun_style=browser.find_element_by_class_name("yidun_popup").get_attribute('style')

            '''if '请依次点击' in yidun_controlText:
                print ('属于点击验证码！！！需手动验证！')
                time.sleep(5)
                while 'data/company/detail?id' not in browser.current_url:
                    print ('还没验证通过！！重新验证')
                    time.sleep(5)
            else:
                 print ('属于滑动验证码！！！需手动验证！')
                 if 'data/company/detail?id' not in browser.current_url:
                      print ('还没验证通过！！重新验证')'''
            
                #滑动验证码 代码进行验证！
            #browser.set_window_size(500,500)
        else:
            print ('无验证码')
            #browser.set_window_size(500,500)
    except Exception:
        print ('无验证码')
        #browser.set_window_size(500,500)
        #traceback.print_exc()
    if not isnot_use_ip:
        raise Exception('抛出一个异常--ip已经不能用了！')

#请求网页 得到新的tooken
def gain_token(url,verifiUrl):
    global currentIP
    Chrome_address="E:/chrome/chromedriver.exe"
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = { 'performance':'ALL' }
    proxyauth_plugin_path = chrome_proxy.create_proxyauth_extension(
        proxy_host=currentIP.split(':')[0],
        proxy_port=currentIP.split(':')[1],
        proxy_username="1821359414",
        proxy_password="mo08vvxq"
    )
    #设置代理ip
    co = Options()
    co.add_argument("--start-maximized")
    co.add_extension(proxyauth_plugin_path)
    while True:
        try:
            browser = webdriver.Chrome(executable_path=Chrome_address,desired_capabilities=d,chrome_options = co)
            browser.set_page_load_timeout(120)
            browser.set_script_timeout(120)
            break
        except Exception:
            try:
                browser.close()
                print ('重开浏览器！')
            except Exception:
                print ('浏览器关闭失败！')

    browser.get(url)
    time.sleep(1)
    while getHttpStatus(browser)==503:
        print ('请求503！')
        browser.get(url)
        time.sleep(1)
    
    if getHttpStatus(browser)==401:
        #换代理ip
        currentIP=getProxy()
        browser.close()
        gain_token(url,verifiUrl)
    
    #验证 验证码 
    try:
        verification_code(browser)
    except Exception:
        traceback.print_exc()
        currentIP=getProxy()
        browser.close()
        gain_token(url,verifiUrl)
    
    number_req=1
    while number_req<5:
        try:

            WebDriverWait(browser, 600, 2).until(
                # "//div[@class='hot-cat']" 就是我们要等待页面加载出来的元素
                # 当检测到这个元素时，等待结束，如果检测不到，直到我们设置的最长等待时间之后才会结束并报错
                EC.presence_of_all_elements_located((By.XPATH, "//table[@class='el-table__body']")))
            break
        except Exception:
            browser.refresh()
            number_req=number_req+1
    accessToken=''
    cookies=''
    for i in range(1,5):
        print ('循环获取tooken!!')
        #得到  accesstoken
        info=browser.get_log('performance')
        #验证通过 需要获取 accessToken
        for i in info:
            dic_info=json.loads(i['message'])
            info_le=dic_info['message']['params']
            if 'request' in info_le.keys():
                if 'headers' in info_le['request'].keys():
                    #print (info_le['request']['headers'])
                    if 'accessToken' in info_le['request']['headers'].keys():
                        accessToken=info_le['request']['headers']['accessToken']  
                        break
        if accessToken!="":
            break
        browser.refresh()
        time.sleep(1)
        
        
    #browser.close()
    for cook in browser.get_cookies():
        name=cook['name']
        value=cook['value']
        cookies=cookies+name+'='+value+';'
    cookies=cookies.rstrip(';')
    browser.close()
    print ('accessToken的值为：---'+accessToken)
    return cookies,accessToken

#时间戳转化为日期
def stampChangeDate(stamp):
    try:
        timeArray=time.localtime(int(stamp)/1000)
        otherStyleTime=time.strftime("%Y-%m-%d", timeArray)
        return otherStyleTime
    except Exception:
        return ''


'''#合同登记详细信息
htdjDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/contractRecordManageDetail?id='+
#招投标信息详情
ztbDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/tenderInfoDetail?id='+
#施工图审查详细信息
sgtscDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectCensorInfoDetail?id='+
#施工许可详细信息
sgxkDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/builderLicenceManageDetail?BuilderLicenceNum=3413001712119901-SX-001'

#竣工验收详细信息
jgysDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/finishManageRelation?PrjfinishNum=3305221902200001-JX-001'
'''

#处理一页招投标信息
def dealZtbData(ztbList):
    print ('处理一页招投标信息')
    for ztb in ztbList:
        print (ztb)

#处理一页合同登记信息
def dealHtdjData(htdjList):
    print ('处理一页合同登记信息')
    for htdj in htdjList:
        '''
'CONTRACTNUM':None
'CONTRACTORCORPID':'6F6F6E696F686D6D6F6F6A686C6F6A666967'
'CONTRACTORCORPNAME':'四川佳和建设工程有限公司'
'CONTRACTTYPENUM':'施工总包'
'CREATEDATE':1457280000000
'DATALEVEL':'D'
'DATASOURCE':None
'ID':'6C6F6D6D6B6F'
'LASTUPDATEDATE':1463389946000
'PRJCODE':None
'PRJNUM':5113031603079901
'PROPIETORCORPID':None
'PROPIETORCORPNAME':'四川高坪国家粮食储备库'
'PROVINCERECORDNUM':'5113032016000007'
'RECORDNUM':'5113031603079901-HZ-001'
'RN':1
'UNIONCORPID':None
        '''
        print (htdj)
        htdjDetailUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/contractRecordManageDetail?id='+htdj['PROVINCERECORDNUM']
        

#处理一页施工图审查信息
def dealSgtscData(sgtscList):
    print ('处理一页施工图审查信息')
    for sgtsc in sgtscList:
        print (sgtsc)

def dealSgxkData(sgxkList):
    print ('处理一页施工许可信息')
    for sgxk in sgxkList:
        print (sgxk)

def dealJgysData(jgysList):
    print ('处理一页竣工验收信息')
    for jgys in jgysList:
        print (jgys)

def analysisAchi(resList):
    for res in resList:
        '''
        'BUILDCORPNAME':None
        'CITY':'南充市'
        'COUNTY':'高坪区'
        'ID':'666F686867'
        'IS_FAKE':None
        'LASTUPDATEDATE':1463389838000
        'PRJNAME':'四川高坪国家粮食储备库5.5万吨原粮低温储备库升级改造项目'
        'PRJNUM':5113031603079901
        'PRJTYPENUM':'其他'
        'PROVINCE':'四川省'
        'RN':1
        '''
        #项目编号
        itemNum=res['PRJNUM']
        #项目名称
        itemName=res['PRJNAME']
        #项目属地
        province=""
        city=""
        county=""
        if res['PROVINCE']!=None:
            province=res['PROVINCE']
        if res['CITY']!=None:
            city=res['CITY']
        if res['COUNTY']!=None:
            county=res['COUNTY']
        ItemLocation=province+city+county
        ItemType=res['PRJTYPENUM']
        itemId=res['ID']
        #最后更新时间
        lastUpdate=res['LASTUPDATEDATE']
        lastUpdate=stampChangeDate(lastUpdate)
        
        #projectUrl  HTML
        proHtmlUrl="http://jzsc.mohurd.gov.cn/data/project/detail?id="+itemId
        #基本信息
        proDetailUrl="http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectDetail?id="+itemId
        
        
        #招投标信息
        ztbUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/tenderInfo?jsxmCode='+str(itemNum)+'&pg=0&pgsz=15'
       
        #处理招投标信息
        ztbRes=get_request(ztbUrl,publicHeaders)
        while ztbRes=='token失效':
            cookies,accessToken=gain_token(proHtmlUrl,ztbUrl)
            publicHeaders['Cookie']=cookies
            publicHeaders['accessToken']=accessToken
            #print (publicHeaders)
            ztbRes=get_request(ztbUrl,publicHeaders)
        ztbJson=json.loads(decryptRes(ztbRes))

        ztbList=ztbJson['data']['list']
        dealZtbData(ztbList)
        ztbToal=ztbJson['data']['total']
        ztbTotalPage=math.ceil(int(ztbToal)/15)
        print ('该业绩有---'+str(ztbTotalPage)+'---页招投标信息')
        if ztbTotalPage>1:
            for ztb in range(1,ztbTotalPage):
                print ('请求第---'+str(ztb)+'---页招投标信息')
                pageZtbUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/tenderInfo?jsxmCode='+str(itemNum)+'&pg='+str(ztb)+'&pgsz=15'
                pageZtbRes=get_request(pageZtbUrl,publicHeaders)
                while pageZtbRes=='token失效':
                    cookies,accessToken=gain_token(proHtmlUrl,pageZtbUrl)
                    publicHeaders['Cookie']=cookies
                    publicHeaders['accessToken']=accessToken
                    #print (publicHeaders)
                    pageZtbRes=get_request(pageZtbUrl,publicHeaders)
                pageZtbJson=json.loads(decryptRes(pageZtbRes))
                pageZtbList=pageZtbJson['data']['list']
                dealZtbData(pageZtbList)

        #合同登记信息
        htdjUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/contractRecordManage?jsxmCode='+str(itemNum)+'&pg=0&pgsz=15'
        
        #处理合同登记信息
        htdjRes=get_request(htdjUrl,publicHeaders)
        while htdjRes=='token失效':
            cookies,accessToken=gain_token(proHtmlUrl,htdjUrl)
            publicHeaders['Cookie']=cookies
            publicHeaders['accessToken']=accessToken
            #print (publicHeaders)
            htdjRes=get_request(htdjUrl,publicHeaders)
        htdjJson=json.loads(decryptRes(htdjRes))

        htdjList=htdjJson['data']['list']
        dealHtdjData(htdjList)
        htdjToal=htdjJson['data']['total']
        htdjTotalPage=math.ceil(int(htdjToal)/15)
        print ('该业绩有---'+str(htdjTotalPage)+'---页合同登记信息')
        if htdjTotalPage>1:
            for htdj in range(1,htdjTotalPage):
                print ('请求第---'+str(htdj)+'---页合同登记信息')
                pageHtdjUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/contractRecordManage?jsxmCode='+str(itemNum)+'&pg='+str(htdj)+'&pgsz=15'
                pageHtdjRes=get_request(pageHtdjUrl,publicHeaders)
                while pageHtdjRes=='token失效':
                    cookies,accessToken=gain_token(proHtmlUrl,pageHtdjUrl)
                    publicHeaders['Cookie']=cookies
                    publicHeaders['accessToken']=accessToken
                    #print (publicHeaders)
                    pageHtdjRes=get_request(pageHtdjUrl,publicHeaders)
                pageHtdjJson=json.loads(decryptRes(pageHtdjRes))
                pageHtdjList=pageHtdjJson['data']['list']
                dealHtdjData(pageHtdjList)

        #施工图审查信息
        sgtscUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectCensorInfo?jsxmCode='+str(itemNum)+'&pg=0&pgsz=15'
        
        #处理施工图审查
        sgtscRes=get_request(sgtscUrl,publicHeaders)
        while sgtscRes=='token失效':
            cookies,accessToken=gain_token(proHtmlUrl,sgtscUrl)
            publicHeaders['Cookie']=cookies
            publicHeaders['accessToken']=accessToken
            #print (publicHeaders)
            sgtscRes=get_request(sgtscUrl,publicHeaders)
        sgtscJson=json.loads(decryptRes(sgtscRes))

        sgtscList=sgtscJson['data']['list']
        dealSgtscData(sgtscList)
        sgtscToal=sgtscJson['data']['total']
        sgtscTotalPage=math.ceil(int(sgtscToal)/15)
        print ('该业绩有---'+str(sgtscTotalPage)+'---页施工图审查信息')
        if sgtscTotalPage>1:
            for sgtsc in range(1,sgtscTotalPage):
                print ('请求第---'+str(sgtsc)+'---页施工图审查信息')
                pageSgtscUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectCensorInfo?jsxmCode='+str(itemNum)+'&pg='+str(sgtsc)+'&pgsz=15'
                pageSgtscRes=get_request(pageSgtscUrl,publicHeaders)
                while pageSgtscRes=='token失效':
                    cookies,accessToken=gain_token(proHtmlUrl,pageSgtscUrl)
                    publicHeaders['Cookie']=cookies
                    publicHeaders['accessToken']=accessToken
                    #print (publicHeaders)
                    pageSgtscRes=get_request(pageSgtscUrl,publicHeaders)
                pageSgtscJson=json.loads(decryptRes(pageSgtscRes))
                pageSgtscList=pageSgtscJson['data']['list']
                dealSgtscData(pageSgtscList)

        
        #施工许可
        sgxkUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/builderLicenceManage?jsxmCode='+str(itemNum)+'&pg=0&pgsz=15'
        #处理施工许可
        sgxkRes=get_request(sgxkUrl,publicHeaders)
        while sgxkRes=='token失效':
            cookies,accessToken=gain_token(proHtmlUrl,sgxkUrl)
            publicHeaders['Cookie']=cookies
            publicHeaders['accessToken']=accessToken
            #print (publicHeaders)
            sgxkRes=get_request(sgxkUrl,publicHeaders)
        sgxkJson=json.loads(decryptRes(sgxkRes))

        sgxkList=sgxkJson['data']['list']
        dealSgxkData(sgxkList)
        sgxkToal=sgxkJson['data']['total']
        sgxkTotalPage=math.ceil(int(sgxkToal)/15)
        print ('该业绩有---'+str(sgxkTotalPage)+'---页施工许可信息')
        if sgxkTotalPage>1:
            for sgtxk in range(1,sgxkTotalPage):
                print ('请求第---'+str(sgtxk)+'---页施工许可信息')
                pageSgxkUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/builderLicenceManage?jsxmCode='+str(itemNum)+'&pg='+str(sgtxk)+'&pgsz=15'
                pageSgxkRes=get_request(pageSgxkUrl,publicHeaders)
                while pageSgxkRes=='token失效':
                    cookies,accessToken=gain_token(proHtmlUrl,pageSgxkUrl)
                    publicHeaders['Cookie']=cookies
                    publicHeaders['accessToken']=accessToken
                    #print (publicHeaders)
                    pageSgxkRes=get_request(pageSgxkUrl,publicHeaders)
                pageSgxkJson=json.loads(decryptRes(pageSgxkRes))
                pageSgxkList=pageSgxkJson['data']['list']
                dealSgxkData(pageSgxkList)

        #竣工验收
        jgysUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectFinishManage?jsxmCode='+str(itemNum)+'&pg=0&pgsz=15'
        #处理竣工验收
        jgysRes=get_request(jgysUrl,publicHeaders)
        while jgysRes=='token失效':
            cookies,accessToken=gain_token(proHtmlUrl,jgysUrl)
            publicHeaders['Cookie']=cookies
            publicHeaders['accessToken']=accessToken
            #print (publicHeaders)
            jgysRes=get_request(jgysUrl,publicHeaders)
        jgysJson=json.loads(decryptRes(jgysRes))

        jgysList=jgysJson['data']['list']
        dealJgysData(jgysList)
        jgysToal=jgysJson['data']['total']
        jgysTotalPage=math.ceil(int(jgysToal)/15)
        print ('该业绩有---'+str(jgysTotalPage)+'---页竣工验收信息')
        if jgysTotalPage>1:
            for jgys in range(1,jgysTotalPage):
                print ('请求第---'+str(jgys)+'---页竣工验收信息')
                pageJgysUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/project/projectFinishManage?jsxmCode='+str(itemNum)+'&pg='+str(jgys)+'&pgsz=15'
                pageJgysRes=get_request(pageJgysUrl,publicHeaders)
                while pageJgysRes=='token失效':
                    cookies,accessToken=gain_token(proHtmlUrl,pageJgysUrl)
                    publicHeaders['Cookie']=cookies
                    publicHeaders['accessToken']=accessToken
                    #print (publicHeaders)
                    pageJgysRes=get_request(pageJgysUrl,publicHeaders)
                pageJgysJson=json.loads(decryptRes(pageJgysRes))
                pageJgysList=pageJgysJson['data']['list']
                dealJgysData(pageJgysList)


#根据企业名称 查询是否有该企业的数据
def isExist(companyName):
    global publicHeaders
    companyName=companyName.replace('造价企业','').replace('(','（').replace(')','）')
    basicUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/comp/list?complexname='+companyName+'&pg=0&pgsz=15&total=0'
    encryptResult=get_request(basicUrl,headers)
    
    decryptResult=decryptRes(encryptResult)
    resultJson=json.loads(decryptResult)
    if resultJson['data']==None or ( resultJson['data']!=None and resultJson['data']['total']==0):
        print ('全国住建部没有该企业的数据！！---属于没结果---'+companyName)
        time.sleep(3)
    else:
        #定义一个下标  表示企业出现在第几行
        offet=-1
        resList=resultJson['data']['list']
        for data in resList:
            offet=offet+1
            htmlcompanyName=data['QY_NAME']
            if htmlcompanyName==companyName:
                break
            
        if offet!=-1:
            print ('企业名称为：---'+companyName)
            com_qy_id=resList[offet]['QY_ID']
            organizationCode=resList[offet]['QY_ORG_CODE']
            print ('企业对应的ID为：---'+com_qy_id)
            detailUrl='http://jzsc.mohurd.gov.cn/data/company/detail?id='+com_qy_id

            #得到企业各类总数信息的url
            each_totalUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/comp/getTotal?qyId='+com_qy_id+'&qyCode='+organizationCode
            totalRes=get_request(each_totalUrl,publicHeaders)
            while totalRes=='token失效':
                cookies,accessToken=gain_token(detailUrl,each_totalUrl)
                publicHeaders['Cookie']=cookies
                publicHeaders['accessToken']=accessToken
                #print (publicHeaders)
                totalRes=get_request(each_totalUrl,publicHeaders)
            totalJson=json.loads(decryptRes(totalRes))
            if totalJson['data']==None:
                print ('请求结果有问题！')
                return
            #得到业绩总数
            achiTotal=totalJson['data']['proTotal']
            print ('该企业的业绩总数为---'+str(achiTotal))
            if int(achiTotal)<1:
                return 
            
            #得到企业的业绩信息url
            achievementUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/comp/compPerformanceListSys?qy_id='+com_qy_id+'&pg=0&pgsz=15'
            achieveRes=get_request(achievementUrl,publicHeaders)
            while achieveRes=='token失效':
                cookies,accessToken=gain_token(detailUrl,achievementUrl)
                publicHeaders['Cookie']=cookies
                publicHeaders['accessToken']=accessToken
                #print (publicHeaders)
                achieveRes=get_request(achievementUrl,publicHeaders)
            achieveJson=json.loads(decryptRes(achieveRes))
            #print (qualJson['data']['pageList'])
            resList=achieveJson['data']['list']
            totalPage=math.ceil(int(achiTotal)/15)
            print ('该企业有---'+str(totalPage)+'---页企业业绩')
            if totalPage>1:
                for pa in range(1,totalPage):
                    print ('请求第---'+str(pa)+'---页业绩信息')
                    pageachiUrl='http://jzsc.mohurd.gov.cn/api/webApi/dataservice/query/comp/compPerformanceListSys?qy_id='+com_qy_id+'&pg='+str(pa)+'&pgsz=15'
                    pageachiRes=get_request(pageachiUrl,publicHeaders)
                    while pageachiRes=='token失效':
                        cookies,accessToken=gain_token(detailUrl,pageachiUrl)
                        publicHeaders['Cookie']=cookies
                        publicHeaders['accessToken']=accessToken
                        #print (publicHeaders)
                        pageachiRes=get_request(pageachiUrl,publicHeaders)
                    pageachiJson=json.loads(decryptRes(pageachiRes))
                    resList.extend(pageachiJson['data']['list'])
            print (len(resList))
            #解析业绩
            analysisAchi(resList)
           
        else:
            print ('全国住建部没有该企业的数据！！')

def main():
    global conn,countryWide
    count=0
    while True:
        try:
            #countryWide.update_many({'count':{"$lte":398500,"$gte":398250}},{"$set":{"is_spider":False}})
            count_one=countryWide.find_one({"is_spider":False})
            if count_one:
                count=count_one['count']
            break
        
        except Exception:
            conn.close()
            is_suc=True
            while is_suc:   
                try:
                    conn=MongoClient("139.9.75.231",8635)

                    constructionDB_db=conn.get_database('constructionDB')
                    #用户名，密码，数据库
                    constructionDB_db.authenticate('constructionDB','ConstructionDB1408~','constructionDB')
                    
                    countryWide=constructionDB_db.countryWideQual
                    is_suc=False
                except Exception:
                    conn.close()

    empty_total=0
    while True:
        try:
            if countryWide.find_one({"count":count}):
                empty_total=0
                print (count)
                while True:
                    try:
                        count_must=countryWide.find_and_modify({"count":count,"is_spider":False},{"$set":{"is_spider":True}},safe=True,new=True)
                        if isinstance(count_must,dict):
                            companyNameNoTag=count_must['companyNameNoTag']
                            companyName=count_must['companyName']
                            try:
                                whitestartTime=time.time()
                                isExist(companyName)
                                whiteendTime=time.time()
                                print ("操作一家企业耗时时间为："+str(whiteendTime-whitestartTime)+"秒")
                            except Exception:
                                traceback.print_exc()
                                countryWide.update_one({"count":count,"companyNameNoTag":companyNameNoTag},{"$set":{"is_spider":False}})
                        else:
                            print ("没有该编号对应的！")
                            break
                    except Exception:
                        conn.close()
                        is_suc=True
                        while is_suc:
                            try:
                                conn=MongoClient("139.9.75.231",8635)

                                constructionDB_db=conn.get_database('constructionDB')
                                #用户名，密码，数据库
                                constructionDB_db.authenticate('constructionDB','ConstructionDB1408~','constructionDB')
                                
                                countryWide=constructionDB_db.countryWideQual

                                is_suc=False
                            except Exception:
                                conn.close()
                count=count+1
            else:
                empty_total=empty_total+1
                count=count+1
                if empty_total>999:
                    break
        except Exception:
            conn.close()
            is_suc=True
            while is_suc:
                try:
                    conn=MongoClient("139.9.75.231",8635)

                    constructionDB_db=conn.get_database('constructionDB')
                    #用户名，密码，数据库
                    constructionDB_db.authenticate('constructionDB','ConstructionDB1408~','constructionDB')
                    
                    countryWide=constructionDB_db.countryWideQual

                    is_suc=False
                except Exception:
                    conn.close()

isExist('四川佳和建设工程有限公司')

'''while True:
    main()
    print ("全国资质爬取！！！，休息一个小时")
    time.sleep(60)
    while True:
        try:
            countryWide.update_many({},{"$set":{"is_spider":False}})
            break
        except Exception:
            conn.close()
            is_suc=True
            while is_suc:
                try:
                    
                    conn=MongoClient("139.9.75.231",8635)

                    constructionDB_db=conn.get_database('constructionDB')
                    #用户名，密码，数据库
                    constructionDB_db.authenticate('constructionDB','ConstructionDB1408~','constructionDB')
                    
                    countryWide=constructionDB_db.countryWideQual
                    is_suc=False
                except Exception:
                    conn.close()'''

'''conn_wide=MongoClient("139.9.75.231",8635)

constructionDB_db_wide=conn_wide.get_database('constructionDB')
#用户名，密码，数据库
constructionDB_db_wide.authenticate('constructionDB','ConstructionDB1408~','constructionDB')

updateComWide=constructionDB_db_wide.updateComWideName

while True:
    try:
        count_must=updateComWide.find_and_modify({"is_clean":False},{"$set":{"is_clean":True}},safe=True,new=True)
        if isinstance(count_must,dict):
            companyName=count_must['companyName']
            try:
                whitestartTime=time.time()
                isExist(companyName)
                whiteendTime=time.time()
                print ("操作一家企业耗时时间为："+str(whiteendTime-whitestartTime)+"秒")
            except Exception:
                traceback.print_exc()
                updateComWide.update_one({"companyName":companyName},{"$set":{"is_clean":False}})
        else:
            print ("没有该编号对应的！")
            break
    except Exception:
        conn_wide.close()
        is_suc=True
        while is_suc:
            try:
                conn_wide=MongoClient("139.9.75.231",8635)

                constructionDB_db_wide=conn_wide.get_database('constructionDB')
                #用户名，密码，数据库
                constructionDB_db_wide.authenticate('constructionDB','ConstructionDB1408~','constructionDB')

                updateComWide=constructionDB_db_wide.updateComWideName

                is_suc=False
            except Exception:
                conn_wide.close()'''

