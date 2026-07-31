import urllib3
urllib3.disable_warnings()
import requests

class MicroHX:
    def __init__(self):
        self.session = requests.Session()
        self.MicroHXHost =  "https://m.hxxy.edu.cn"
        self.headers = {}

    def set_headers(self,cookies:str)->dict:
        """
        根据登录信息获取请求头,同时更新对象headers变量
        :param cookies: 登录态Cookies,一般以'PHPSESSID='开头
        :return:字典headers
        """
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541932) XWEB/19841 Flue",
            'x-requested-with': "XMLHttpRequest",
            'Cookie': cookies
        }
        self.headers = headers
        return headers

    def get_headers(self)-> dict:
        return self.headers

    def update_auth(self,cookies:str)->None:
        """
        更新登录态
        :param cookies: 登录态Cookies,,一般以'PHPSESSID='开头
        :return:
        """
        new_headers = self.set_headers(cookies)
        self.session.headers.update(new_headers)

    def _request(self, method, url, **kwargs) -> dict:
        """
        统一处理HTTP请求
        """

        result = {
            "code": 0,
            "status_code": 0,
            "msg": "",
            "is_json": False,
            "data": None
        }

        try:
            resp = self.session.request(
                method,
                url,
                timeout=10,
                verify=False,
                **kwargs
            )

            result["status_code"] = resp.status_code

            try:
                result["data"] = resp.json()
                result["is_json"] = True
                result["msg"] = "请求成功"

            except ValueError:
                result["code"] = 1
                result["msg"] = "返回数据非JSON"
                result["data"] = resp.text

        except requests.exceptions.Timeout:
            result["code"] = -101
            result["msg"] = "请求超时"

        except requests.exceptions.RequestException as e:
            result["code"] = -102
            result["msg"] = f"请求失败: {e}"

        except Exception as e:
            result["code"] = -999
            result["msg"] = str(e)

        return result

    def test_auth(self)->bool:
        """
        测试登录态有效性
        :return: True:有效/False:失效
        """
        result = self.api_sumhdxfforxflx()
        return result["code"] == 0

    def api_getvisitedactives(self)->dict:
        """
        获取已参加活动列表
        :return:
        """
        api = f"{self.MicroHXHost}/hdzx/stage2/getvisitedactives"
        return self._request('POST',api)

    def api_sumhdxfforxflx(self)->dict:
        """
        获取已获得学分
        :return:
        """
        api = "https://m.hxxy.edu.cn/hdzx/stage2/sumhdxfforxflx"
        return self._request('POST',api)

    def api_ssyx(self,price:str)->dict:
        """
        接口：宿舍预选
        :param price: 价位参数字符串,可选：['1500','3000','4000']
        :return: True/False
        """
        api = f"{self.MicroHXHost}/xitong/ssyx/select.php"
        payload = {
            'price': price
        }
        return self._request('POST',api,data=payload)

