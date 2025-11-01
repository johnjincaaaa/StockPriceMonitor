import requests
import execjs
import re
import json

# 1sh 0sz sz14111

def get_data(stock_code):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://quote.eastmoney.com/sz301170.html",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    cookies = {
        "qgqp_b_id": "bf20aa060c55fb6103d9ae2e699677da",
        "fullscreengg": "1",
        "fullscreengg2": "1",
        "st_si": "90459649178605",
        "st_asi": "delete",
        "st_nvi": "jVrv1nVDUiKXnvNTbzWV6141e",
        "nid": "053fb4cc43be192e3cffd6fdc8afbd61",
        "nid_create_time": "1761887054408",
        "gvi": "2-WboYQztWgmWaC3aL-vY58b8",
        "gvi_create_time": "1761887054409",
        "st_pvi": "33874453744038",
        "st_sp": "2025-10-31%2013%3A04%3A13",
        "st_inirUrl": "https%3A%2F%2Fwww.doubao.com%2F",
        "st_sn": "23",
        "st_psi": "20251031164346109-113200301201-6906754602"
    }
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    area = {'sh':'1','sz':'0'}
    params = {
        "cb": "jQuery35102773207766642962_1761900524532",
        "secid": f"{area[stock_code[:2]]}.{stock_code[2::]}",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",
        "fqt": "1",
        "beg": "0",
        "end": "20500101",
        "smplmt": "460",
        "lmt": "1000000",
        "_": "1761900524533"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    data = re.findall(r'\(.*?\)', response.text)[0].strip('(').strip(')')
    print(response)
    data = json.loads(data)
    # print(data)
    try:
        data_detail = data['data']['klines'][-1].split(',')
        date = data_detail[0]
        opening_price  = data_detail[1]
        new_price = data_detail[2]
        high = data_detail[3]
        low = data_detail[4]
        price_limit = data_detail[8]
        change_amount = data_detail[9]
        turnover_rate = data_detail[10]
        # 'k_line:日期,今开,最新价,最高,最低,**,**,**,涨跌幅%,涨跌额,换手率%'
        a = {
            'stock_name':data.get('data').get('name'),
            'date':date,
            'opening_price':opening_price,
            'new_price':new_price,
            'high':high,
            'low':low,
            'price_limit':price_limit,
            'change_amount':change_amount,
            'turnover_rate':turnover_rate,
        }
    except Exception as e:
        print(e)
        a = {}
    return a

if __name__ == '__main__':

    print(get_data('sh600036'))
