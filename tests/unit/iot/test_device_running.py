import requests
import unittest


class IotDeviceTestCase(unittest.TestCase):

    def test_device_access(self):
        raspiot_endpoint = 'http://127.0.0.1/'
        response = requests.get(raspiot_endpoint)
        self.assertEqual(response.status_code, 200)

        data = {"name": "John", "age": 30}
        access_url = raspiot_endpoint + '/device/%s/access' % 'de93ee9e-3d74-4b28-ac77-0a3318f3f944'
        response = requests.post(access_url, data=data)
        print(response.status_code)
        print(response.json())  # 将响应内容解析为JSON格式

        # 设置请求头
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get("https://www.baidu.com", headers=headers)
        print(response.status_code)
        print(response.text)

