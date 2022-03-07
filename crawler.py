# coding=gbk
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

#import packge 


#headrs伪装，模拟人工浏览
headers={
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
		}
url_header="http://www.tianqihoubao.com/"[:-1]


#获取html页面，使用BeautifulSoup处理
def get_html_soup(url):
    url=url.replace('\r','').replace('\n','')#去除影响爬取的字符
    print("request:", url)
    r=requests.get(url,headers=headers)#发起GET请求
    r.encoding='gb2312' #设置页面编码
    print("status_code:",r.status_code)
    html_text=r.text
    soup = BeautifulSoup(html_text, 'html.parser') #BeautifulSoup
    return soup

#一级页面，获取城市和对应的链接
def get_city_link_list():
    soup=get_html_soup("http://www.tianqihoubao.com/aqi/")
    all_dl=soup.find_all('dl')
    city_link_list=[]   #解析页面
    for dl in all_dl:
        item=dl.find_all('a')  
        for i in range(len(item)): 
            if not (dl==all_dl[0] and item[i].text.strip() in ['广州','深圳','成都','杭州','全国空气质量排名']):
                city_link_list.append([item[i].text.strip(),item[i]['href']])
    return city_link_list

#获取城市的历史数据链接
def get_city_historical_link_list(city_link_list):
    href_month_list=[]  #解析页面数据
    for  city_link_item in city_link_list:
        url=url_header+city_link_item[1]
        soup=get_html_soup(url)
        all_div=soup.find_all('div',{'class','box p'})#发现对应的对象
        for href_month in all_div[0].find_all('a'):
            href_month_list.append([href_month['title'],href_month['href']])
    return href_month_list


#获得页面的数据并进行打包
def get_pages_data(href_month_list):
    for  city_link_item in href_month_list:
        url=url_header+city_link_item[1]
        soup=get_html_soup(url)
        data_list=[]
        table=soup.find_all('table')
        for i in range(len(table[0].find_all('tr'))):#对行数据进行解析
            td_all=table[0].find_all('tr')[i].find_all('td') #对每一行的数据进行解析
            data=td_all[0].text.strip()
            quality=td_all[1].text.strip()
            AQI=td_all[2].text.strip()
            AQI_Rank=td_all[3].text.strip()
            PM25=td_all[4].text.strip()
            PM10=td_all[5].text.strip()
            So2=td_all[6].text.strip()
            No2=td_all[7].text.strip()
            Co=td_all[8].text.strip()
            O3=td_all[9].text.strip()
            data_list.append({"data":data,"quality":quality,"AQI":AQI,"AQI_Rank":AQI_Rank,
            "PM25":PM25,"PM10":PM10,"So2":So2,"No2":No2,"Co":Co,"O3":O3})
        data_dataframe=pd.DataFrame(data_list,columns=["data","quality","AQI","AQI_Rank","PM25","PM10","So2","No2","Co","O3"])
        #文件命名
        root_path="csv"
        city=city_link_item[0][8:10]
        year=city_link_item[0][0:4]
        path=os.path.join(root_path,city,year)
        #-------
        if not os.path.exists(path):#没有文件夹则新建文件夹
            os.makedirs(path)
        csv_name=os.path.join(path,city_link_item[0]+".csv")
        print("csv write:",csv_name)
        data_dataframe.to_csv(csv_name,index=False,header=0)#保存CSV文件

#设置主函数组装  
def main():
    city_link_list=get_city_link_list()
    href_month_list=get_city_historical_link_list(city_link_list)
    get_pages_data(href_month_list)

main()
