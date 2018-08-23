#!/usr/bin/env python
# encoding=utf-8

"""
基金净值查询,要查的基金代码
"""
fund_code='002001'

#手续费
fund_buy=0.0015
fund_sale=0.005
import csv
import requests
#from bs4 import BeautifulSoup
import json
#import pymongo
# myclient = pymongo.MongoClient('mongodb://192.168.31.23:27017/')
# mydb = myclient["runoobdb"]
# mycol = mydb["chuanye"]


DOWNLOAD_URL = 'http://stock.finance.sina.com.cn/fundInfo/api/openapi.php/CaihuiFundInfoService.getNav?symbol='+fund_code+'&datefrom=&dateto=&page='
DOWNLOAD_URL_fenhong='http://stock.finance.sina.com.cn/fundInfo/api/openapi.php/FundPageInfoService.tabfh?symbol='+fund_code+'&format=json'


def download_page(url):
    return requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }).text


def parse_html(html):
    # soup = BeautifulSoup(html,'html.parser')
    # json_soup=json.loads(soup.get_text())
    # return json_soup['result']['data']['data']
    #print(html)
    return json.loads(html)['result']['data']['data']

def parse_fenhong_html(html):
    dict_fenhong = {}
    list_fenhong=json.loads(html)['result']['data']['fhdata']
    if list_fenhong:
        for i in  range(0,len(list_fenhong)):
            dict_fenhong[list_fenhong[i]["djr"]]=list_fenhong[i]["mffh"]
    else:
        pass
    print(dict_fenhong)
    return(dict_fenhong)


def main():

   #红利发放查询
    hml2 = download_page(DOWNLOAD_URL_fenhong)
    dict_fenhong=parse_fenhong_html(hml2)
    print(dict_fenhong)

    #基金净值查询
    list_soup=[]
    for i in range(1,999):
        url = DOWNLOAD_URL+str(i)
        print(url)
        html = download_page(url)
        get_one_html=parse_html(html)
        if get_one_html:
            list_soup=list_soup+get_one_html
        else:
            break
    list_soup.reverse()



    list_have_fund=[]



    with open('./out/'+fund_code+'.csv', "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "jijing_jz", "leiji_jz","fenhong","zengzhang","buy_money","buy_amount","aravge_price","sum_buy_amount","sum_buy_money","service_charge","fenhong"])
        date=''
        sum_buy_amount,sum_buy_money,buy_count,last_jz,aravge_price,sum_service_charge,sum_fenhong,maichu_shouyi_all=0,0,0,1,1,0,0,0


        for dic_soup in list_soup:
            if date==dic_soup['fbrq']:
                pass
            else:
                dict_have_fund_date = {}
                add= round((last_jz*-1+float(dic_soup['jjjz']))/last_jz*100,2)


                # if add>=2 and sum_buy_amount>200:
                #     buy_money=-100
                # elif add<=-1:
                #     buy_money=100
                # else:
                #     buy_money = 100
                zuichu_mairu_jiage=1

                if zuichu_mairu_jiage*1.05<last_jz  :
                    if sum_buy_amount>2000:
                        buy_money = -100
                    else:
                        buy_money=0
                else:
                    buy_money = 200


                #手续费
                if buy_money>0:
                    service_charge=buy_money*fund_buy
                else:
                    service_charge=buy_money*-1*fund_sale

                #除手续费后实际购买份额
                buy_amount=round((buy_money-service_charge)/last_jz,4)
                #累积购买基金份额
                sum_buy_amount = sum_buy_amount + buy_amount

                #最新基金净值
                last_jz = float(dic_soup['jjjz'])

                #基金日期
                date = dic_soup['fbrq']

                #累积投入金钱
                sum_buy_money = sum_buy_money + buy_money
                #平均购买价格
                aravge_price = (sum_buy_money) / sum_buy_amount
                #总购买次数
                buy_count = buy_count + 1
                #总手续费
                sum_service_charge=sum_service_charge+service_charge
                #分红率
                if dic_soup['fbrq'] in dict_fenhong:
                    fenhong=float(dict_fenhong[dic_soup['fbrq']])*sum_buy_amount
                    print(str(dic_soup['fbrq']) + '分红'+str(fenhong))
                else:
                    fenhong=0
                #总分红金额
                sum_fenhong=sum_fenhong+fenhong
                #目前投资总收益
                shouyi=sum_buy_amount*last_jz+sum_fenhong-sum_buy_money-sum_service_charge
                jinri_shouyi = 0

                #购买金额大于0
                if buy_money>0:
                     dict_have_fund_date['date']=date
                     dict_have_fund_date['amonunt']=buy_amount
                     dict_have_fund_date['price']=last_jz
                     list_have_fund.append( dict_have_fund_date)
                #卖出计算收益
                elif buy_money<0:
                    xiaochu_amount=buy_amount*-1

                    for dict_remove_fund in list_have_fund:
                        if dict_remove_fund['amonunt']<=xiaochu_amount:
                            xiaochu_amount=xiaochu_amount-dict_remove_fund['amonunt']
                            jinri_shouyi=jinri_shouyi+dict_remove_fund['amonunt']*(last_jz-dict_remove_fund['price'])
                            print('del'+str(dict_remove_fund))
                            del list_have_fund[0]
                        elif dict_remove_fund['amonunt']>xiaochu_amount:
                            dict_remove_fund['amonunt']=dict_remove_fund['amonunt']-xiaochu_amount
                            jinri_shouyi = jinri_shouyi + xiaochu_amount * (last_jz - dict_remove_fund['price'])
                            list_have_fund[0]=dict_remove_fund
                            break
                    maichu_shouyi_all=maichu_shouyi_all+jinri_shouyi
                    zuichu_mairu_jiage=list_have_fund[0]['price']








                writer.writerow([date, last_jz, dic_soup['ljjz'],fenhong, add,buy_money,buy_amount,aravge_price,sum_buy_amount,sum_buy_money,service_charge,fenhong,jinri_shouyi,maichu_shouyi_all])


        print(list_have_fund)
        writer.writerow(['最新净值','目前总份额','目前市值','投入总金额','投资收益率'])
        writer.writerow([last_jz, sum_buy_amount, sum_buy_amount*last_jz, sum_buy_money,shouyi/sum_buy_money])


        print(fund_code+'最新净值：'+str(last_jz)+'\n投资次数：' + str(buy_count)+'\n目前总份额 :'+str(sum_buy_amount)+'\n目前市值：'+str(sum_buy_amount*last_jz)+'\n投入总金额 :'+str(sum_buy_money))

        print('投资总收益：' + str(shouyi ))
        print('年化投资收益率：'+str((shouyi)/sum_buy_money/buy_count*245))
        print('投资收益率：' + str((shouyi) / sum_buy_money ))


if __name__ == '__main__':
    main()