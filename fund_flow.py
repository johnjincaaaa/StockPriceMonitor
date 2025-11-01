import requests
import re,json
def fund_flow(stock_code):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://data.eastmoney.com/zjlx/600036.html",
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
        "st_nvi": "jVrv1nVDUiKXnvNTbzWV6141e",
        "nid": "053fb4cc43be192e3cffd6fdc8afbd61",
        "nid_create_time": "1761887054408",
        "gvi": "2-WboYQztWgmWaC3aL-vY58b8",
        "gvi_create_time": "1761887054409",
        "st_asi": "delete",
        "st_pvi": "33874453744038",
        "st_sp": "2025-10-31%2013%3A04%3A13",
        "st_inirUrl": "https%3A%2F%2Fwww.doubao.com%2F",
        "st_sn": "47",
        "st_psi": "20251031182732703-113300300815-2001006639"
    }
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    area = {'sh': '1', 'sz': '0'}
    params = {
        "cb": "jQuery112305302866280931489_1761906479032",
        "fltt": "2",
        "secids": f"{area[stock_code[:2]]}.{stock_code[2::]}",
        "fields": "f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f64,f65,f70,f71,f76,f77,f82,f83,f164,f166,f168,f170,f172,f252,f253,f254,f255,f256,f124,f6,f278,f279,f280,f281,f282",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "_": "1761906479033"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)

    # print(response.text)
    # print(response)
    data = re.findall(r'\(.*?\)', response.text)[0].strip('(').strip(')')
    print(response)
    data = json.loads(data)
    print(data)

    return data.get('data').get('diff')[0]['f62']

if __name__ == '__main__':
    fund_flow('sh600036')