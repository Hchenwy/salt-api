#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import ssl
import urllib.request
import urllib.parse
ssl._create_default_https_context = ssl._create_unverified_context

class SaltAPI(object):
    __HEADER = {'X-Auth-Token': '', 'Accept': 'application/json'}

    def __init__(self, url, username, password):
        self.__url = url.rstrip('/')  # 移除URL末尾的/
        self.__username = username
        self.__password = password
        self.__HEADER['X-Auth-Token'] = self.__salt_login()

    def __deal_request(self, url, data=''):
        ''' 发起https请求
        :param url: 请求的url地址
        :param data: 请求数据
        :return: （dict）响应数据内容
        '''
        request = urllib.request.Request(url=url, headers=self.__HEADER, data=data) if data else urllib.request.Request(url=url, headers=self.__HEADER)
        response = urllib.request.urlopen(request)
        try:
            response_dict = json.loads(response.read().decode('utf-8'))
            return response_dict
        except Exception:
            raise Exception

    def __salt_login(self):
        ''' 登录获取token
        :return: （str）token字符串
        '''
        params = {'eauth': 'pam', 'username': self.__username, 'password': self.__password}
        encode = urllib.parse.urlencode(params)
        data = urllib.parse.unquote(encode).encode('utf-8')
        url = self.__url + '/login'
        result = self.__deal_request(url, data)
        try:
            return result['return'][0]['token']
        except Exception:
            raise Exception

    def run_cmd(self, **kwargs):
        '''
        远程执行命令
        :param kwargs: 字典形式的参数传入
        :return: （dict）主机对应的执行结果
        '''
        if not kwargs:
            print('Error: params input error.')
            return {}
        encode = urllib.parse.urlencode(kwargs)
        data = urllib.parse.unquote(encode).encode('utf-8')
        result = self.__deal_request(self.__url, data)
        try:
            return result['return'][0]
        except Exception:
            raise Exception

    def get_minions(self):
        '''
        获取minions主机列表
        :return: (list)minions信息
        '''
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        encode = urllib.parse.urlencode(params)
        data = urllib.parse.unquote(encode).encode('utf-8')
        result = self.__deal_request(self.__url, data)
        try:
            return result['return'][0]['data']['return']['minions']
        except Exception:
            raise Exception

if __name__ == '__main__':
	saltapi = SaltAPI('https://127.0.0.1:8000', 'saltapi', '1234qwer')
	cmd_res = saltapi.run_cmd(client='local', tgt='dev-web,dev-r_d', fun='cmd.run', arg='ifconfig', expr_form='list')
	key_res = saltapi.get_minions()
	print(cmd_res)
	print(key_res)
