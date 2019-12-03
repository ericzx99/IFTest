import requests
import jsonpath


class Method:
    GET = 'get'
    POST = 'post'

class Body_Type:
    URLENCODED = 'urlencoded'
    JSON='json'
    XML='xml'
    FORM_DATA='form-data'

class Http:
    session = requests.session()

    def __init__(self, url, body_type=None, method = 'get', timeout=3):
        # 成员变量
        self.url = url
        self.method = method
        self.body_type = body_type
        self.params = {}
        self.res = None
        self.headers = {}
        self.body={}
        self.timeout = timeout


# setter 设置一些数据
#     请求参数
    def set_params(self, params_dict):
        if isinstance(params_dict,dict):
            self.params = params_dict
        else:
            raise Exception('请求参数应为字典格式')

    # 请求头
    def set_headers(self, headers_dict):
        if isinstance(headers_dict,dict):
            self.headers = headers_dict
        else:
            raise Exception('请求参数应为字典格式')

    def set_header(self, key, value):
        self.headers[key] = value

    def set_body(self,body_dict):

        if isinstance(body_dict,dict):
            self.body = body_dict
        else:
            raise Exception('请求正文应为字典格式')

        if self.body_type == 'urlencoded':
            self.set_header('Content-Type', 'application/x-www-form-urlencoded')

        elif self.body_type == 'json':
            self.set_header('Content-Type', 'application/json')

        elif self.body_type == 'xml':
            self.set_header('Content-Type', 'text/xml')

        elif self.body_type == 'form-data':
            pass

        # else:
        #     raise Exception('不支持的请求正文格式')

    def send(self):

        if self.method == 'get':
            try:
                self.res = self.session.get(url=self.url, params=self.params,
                                        headers=self.headers, timeout=self.timeout)
            except Exception as e:
                print('未获取到响应:', e)

        elif self.method == 'post':
            if self.body_type == 'urlencoded':
                try:
                    self.res = self.session.post(url=self.url, params=self.params,
                                         headers=self.headers, data=self.body, timeout=self.timeout)
                except Exception as e:
                    print('未获取到响应:', e)

            elif self.body_type=='xml':
                result = self.body.get('xml')
                if result:
                    try:
                        self.res = self.session.post(url=self.url, params=self.params,
                                             headers=self.headers, data=result, timeout=self.timeout)
                    except Exception as e:
                        print('未获取到响应:', e)
                else:
                    raise Exception("xml格式不正确，应为{'xml':'<xxxxxxxxx>'}")

            elif self.body_type=='json':
                try:
                    self.res = self.session.post(url=self.url, params=self.params,
                                         headers=self.headers, json=self.body, timeout=self.timeout)
                except Exception as e:
                    print('未获取到响应:', e)

            elif self.body_type == 'form-data':
                try:
                    self.res = self.session.post(url=self.url, params=self.params,
                                         headers=self.headers, files=self.body, timeout=self.timeout)
                except Exception as e:
                    print('未获取到响应:', e)
            else:
                raise Exception('不支持的请求正文格式:{type}'.format(type=self.body_type))

        else:
            raise Exception('不支持的请求方式:{method}'.format(method=self.method))

# getter
    @property
    def res_text(self):
        if self.res != None:
            return self.res.text
        else:
            return None

    @property
    def res_code(self):
        if self.res != None:
            return self.res.status_code
        else:
            return None

    @property
    def res_dict_from_json(self):
        if self.res != None:
            try:
                return self.res.json()
            except:
                raise Exception('目标json格式不正确:[{act}]'.format(act=self.res_text))
        else:
            return None

    @property
    def res_time(self):
        if self.res != None:
            return round(self.res.elapsed.total_seconds()*1000)
        else:
            return None

    @property
    def res_headers(self):
        if self.res != None:
            # print(type(self.res.headers))
            return self.res.headers
        else:
            return None

    def get_header_value(self,json_path):
        # print('json_path为',json_path)
        # print('self.res_headers为',self.res_headers)
        target = jsonpath.jsonpath(dict(self.res_headers), json_path)
        # print('target为',target)
        if target != False:
            act_value = target[0]
            # print('取到的头的值', act_value)
            return act_value
        else:
            return None

    def get_json_node_value(self,json_path):
        target = jsonpath.jsonpath(self.res_dict_from_json, json_path)
        if target != False:
            act_value = jsonpath.jsonpath(self.res_dict_from_json, json_path)[0]
            return act_value
        else:
            return None




# 断言 检查点

    def check_status_code(self, exp_code=200):
        assert self.res_code==exp_code,'响应状态码检查不通过,期望[{exp}],实际[{act}]'\
            .format(exp=exp_code,act=self.res_code)
        info = '响应状态码检查通过'
        print(info)
        return info

# 响应正文  预期  == 实际
    def check_text_equals(self, exp):
        assert self.res_text == exp, '响应正文检查不通过,期望[{exp}],实际[{act}]'\
            .format(exp=exp,act=self.res_text)
        info = '响应正文检查通过'
        print(info)
        return info

    def check_text_contains(self, exp):
        assert exp in self.res_text,\
            '响应正文检查不通过,期望包含[{exp}],实际未包含,实际为[{act}]' \
            .format(exp=exp, act=self.res_text)
        info = '响应正文检查通过'
        print(info)
        return info

# 特殊 json   关键字段
# 关键字段值

    def check_json_node_exists(self, json_path):
        assert jsonpath.jsonpath(self.res_dict_from_json, json_path) != False,\
            'json字段{exp}检查不通过，不存在该节点'.format(exp=json_path)
        info = 'json字段{exp}检查通过'.format(exp=json_path)
        print(info)
        return info

    def check_json_node_value(self, json_path, exp_value):
        target = jsonpath.jsonpath(self.res_dict_from_json, json_path)
        if target != False:
            act_value = jsonpath.jsonpath(self.res_dict_from_json, json_path)[0]
            assert str(act_value) == str(exp_value), \
                'json字段{path}值检查不通过，期望[{path} == {exp}],实际[{path}为{act}]'\
                    .format(path=json_path, exp=exp_value, act=act_value)
            info = 'json字段{path}值检查通过'.format(path=json_path)
            print(info)
            return info

        else:
            raise AssertionError('json字段{path}不存在'.format(path=json_path))

    def check_res_time(self, max_allowed_ms):
        assert self.res_time < max_allowed_ms,'响应时间检查不通过，期望[<{exp}],实际[{act}]'\
            .format(exp=max_allowed_ms, act=self.res_time)

        info = '响应时间检查通过'
        print(info)
        return info
