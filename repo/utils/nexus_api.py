# -*- coding: utf-8 -*-
"""
__author__:  A.Z
email: bluerevelry@163.COM
"""
from django.http import QueryDict, JsonResponse

import requests, json
from component.status_code import ErrorStatusCode

# Ngxus V sonatype/nexus3:3.37.0
# BASE_URL = "/service/rest/beta"
BASE_URL = "/service/rest/v1"
NEXUS_STATUS = BASE_URL + "/status/"  # 连接状态
GET_REPOSITORY_LIST = BASE_URL + "/repositories/"  # 获取制品库列表
CREATE_REPOSITORY = BASE_URL + "/script/"  # 新建制品库
DELETE_REPOSITORY = BASE_URL + "/repositories/{repository_id}"  # 删除制品库

CREATE_RAW_REPOSITORY = BASE_URL + "/repositories/raw/hosted/"  # 创建raw库
CREATE_PYPI_REPOSITORY = BASE_URL + "/repositories/pypi/hosted/"  # 创建pypi库
CREATE_MAVEN_REPOSITORY = BASE_URL + "/repositories/maven/hosted/"  # 创建maven库
CREATE_DOCKER_REPOSITORY = BASE_URL + "/repositories/docker/hosted/"  # 创建docker库
CREATE_PROXY_DOCKER_REPOSITORY = BASE_URL + "/repositories/docker/proxy/"  # 创建docker库
CREATE_HELM_REPOSITORY = BASE_URL + "/repositories/helm/hosted/"        # 创建hosted类型helm库

# 获取制品库详情/编辑制品库
GET_RAW_REPOSITORY_DETAIL = BASE_URL + "/repositories/raw/hosted/{repository_id}"               # raw
GET_PYPI_REPOSITORY_DETAIL = BASE_URL + "/repositories/pypi/hosted/{repository_id}"             # pypi
GET_MAVEN_REPOSITORY_DETAIL = BASE_URL + "/repositories/maven/hosted/{repository_id}"           # maven
GET_DOCKER_REPOSITORY_DETAIL = BASE_URL + "/repositories/docker/hosted/{repository_id}"         # docker
GET_PROXY_DOCKER_REPOSITORY_DETAIL = BASE_URL + "/repositories/docker/proxy/{repository_id}"    # docker proxy
GET_HELM_REPOSITORY_DETAIL = BASE_URL + "/repositories/helm/hosted/{repository_id}"             # helm

UPLOAD_COMPONENT = BASE_URL + "/components/"  # 创建 pypi 资源
GET_COMPONENT_LIST = BASE_URL + "/components/"  # 获取制品库全部资源
GET_COMPONENT = BASE_URL + "/components/{id}/"  # 获取单个资源
DELETE_COMPONENT = BASE_URL + "/components/{id}/"  # 删除当前版本资源

GET_BLB_LIST = BASE_URL + "/blobstores/" 

# GET_ASSETS = BASE_URL + "/assets​​/{id}/"
GET_ASSETS = BASE_URL + "/assets/{id}/"
DELETE_ASSETS = BASE_URL + "/assets/{id}/"

SEARCH = BASE_URL + "/search/"
# print("GET_ASSETS", GET_ASSETS)


class NexusApi(object):
    def __init__(self, request=None, url=None, username=None, password=None):
        self.nexus_addr = url if url[-1] != "/" else url[:-1]
        self.NEXUS_ADMIN_ACCOUNT = username
        self.NEXUS_ADMIN_ACCOUNT_PASSWORD = password

    def status(self):
        """测试连接状态"""
        # data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + NEXUS_STATUS
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            if res.status_code == 200 or res.status_code == 204:
                # print("status_code-success", res.status_code)
                # print("res.content-success", res.content)
                # data["status"] = 1
                status = True
            else:
                # print("status_code-error", res.status_code)
                # print("res.content-error", res.content.decode())
                if res.status_code == 401:
                    status = ErrorStatusCode.USER_OR_PASSWORD_ERROR, str("Unauthorized")
                else:
                    status = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
                # data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            status = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
            # data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            status = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
            # data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        # return data
        return status

    def get_repository(self):
        """获取制品库列表"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_REPOSITORY_LIST
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = res.json()
                # print(res.content, res.text, res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    # 获取指定制品库
    def get_repository_detail(self, repository_type, repository_id):
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            if repository_type == "raw":
                url = self.nexus_addr + GET_RAW_REPOSITORY_DETAIL.format(repository_id=repository_id)
            elif repository_type == "maven2":
                url = self.nexus_addr + GET_MAVEN_REPOSITORY_DETAIL.format(repository_id=repository_id)
            elif repository_type == "pypi":
                url = self.nexus_addr + GET_PYPI_REPOSITORY_DETAIL.format(repository_id=repository_id)
            elif repository_type == "docker":
                url = self.nexus_addr + GET_DOCKER_REPOSITORY_DETAIL.format(repository_id=repository_id)
            elif repository_type == "proxy_docker":
                url = self.nexus_addr + GET_PROXY_DOCKER_REPOSITORY_DETAIL.format(repository_id=repository_id)
            else:
                url = self.nexus_addr + GET_HELM_REPOSITORY_DETAIL.format(repository_id=repository_id)
            print("获取指定制品库详情url", url)
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = res.json()
                print("获取制品库详情", res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def create_repository(self, repository_id, repository_type, parameters={}, proxy_docker=None):
        """创建制品库"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
            if repository_type == "raw":
                url = self.nexus_addr + CREATE_RAW_REPOSITORY
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                    },
                    "raw": {
                        "contentDisposition": "ATTACHMENT" if not parameters.get(
                            "contentDisposition") else parameters.get("contentDisposition")
                    }
                }
            elif repository_type == "maven2":
                url = self.nexus_addr + CREATE_MAVEN_REPOSITORY
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "maven": {
                        "versionPolicy": "MIXED" if not parameters.get("versionPolicy") else parameters.get(
                            "versionPolicy"),
                        "layoutPolicy": "STRICT" if not parameters.get("layoutPolicy") else parameters.get(
                            "layoutPolicy")
                    }
                }
            elif repository_type == "docker" and not proxy_docker:
                url = self.nexus_addr + CREATE_DOCKER_REPOSITORY
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default",
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "docker": {
                        "v1Enabled": "false" if not parameters.get("v1Enabled") else parameters.get("v1Enabled"),
                        "forceBasicAuth": "true" if not parameters.get("forceBasicAuth") else parameters.get("forceBasicAuth"),
                        "httpPort": 8082 if not parameters.get("httpPort") else parameters.get("httpPort"),
                        # "httpsPort": 8086 if not parameters.get("httpsPort") else parameters.get("httpsPort")
                    },
                    "cleanup": {
                        "policyNames": [
                            "string"
                        ]
                    },
                }
            elif proxy_docker:
                url = self.nexus_addr + CREATE_PROXY_DOCKER_REPOSITORY
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default",
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                    },
                    "docker": {
                        "v1Enabled": "false" if not parameters.get("v1Enabled") else parameters.get("v1Enabled"),
                        "forceBasicAuth": "true" if not parameters.get("forceBasicAuth") else parameters.get(
                            "forceBasicAuth"),
                        "httpPort": 8082 if not parameters.get("httpPort") else parameters.get("httpPort"),
                        # "httpsPort": 8086 if not parameters.get("httpsPort") else parameters.get("httpsPort")
                    },
                    "cleanup": {
                        "policyNames": [
                            "string"
                        ]
                    },
                    "proxy": {
                        "remoteUrl": parameters.get("remoteUrl"),
                        "contentMaxAge": 1440 if not parameters.get("contentMaxAge") else parameters.get("contentMaxAge"),
                        "metadataMaxAge": 1440 if not parameters.get("metadataMaxAge") else parameters.get("metadataMaxAge")
                    },
                    "negativeCache": {
                        "enabled": "true" if not parameters.get("enabled") else parameters.get("enabled"),
                        "timeToLive": 1440 if not parameters.get("timeToLive") else parameters.get("timeToLive")
                    },
                    "dockerProxy": {
                        "indexType": "HUB" if not parameters.get("indexType") else parameters.get("indexType"),
                        # "indexUrl": "string" if not parameters.get("indexUrl") else parameters.get("indexUrl")
                    },
                    "httpClient": {
                        "blocked": "false",
                        "autoBlock": "true",
                        "connection": {
                            "retries": 0,
                            "userAgentSuffix": "string",
                            "timeout": 60,
                            "enableCircularRedirects": "false",
                            "enableCookies": "false",
                            "useTrustStore": "false"
                        },
                        "authentication": {
                            "type": "username",
                            "username": "string",
                            "password": "string",
                            "ntlmHost": "string",
                            "ntlmDomain": "string"
                        }
                    }
                }
                if parameters.get("httpsPort"):
                    form_data["docker"]["httpsPort"] = parameters.get("httpsPort")
            elif repository_type == "pypi":
                url = self.nexus_addr + CREATE_PYPI_REPOSITORY
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                    }
                }
            elif repository_type == "helm":
                url = self.nexus_addr + CREATE_HELM_REPOSITORY
                form_data = {
                      "name": repository_id,
                      "online": "true" if not parameters.get("online") else parameters.get("online"),
                      "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                      },
                      "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                      },
                      "component": {"proprietaryComponents": "true"}
                    }
            else:
                raise Exception("tool type error")
            print("form_data", form_data)
            res = req.post(url, data=json.dumps(form_data), headers=headers)
            res.encoding = 'utf-8'
            print("data12", res.content.decode(), res.status_code)
            if res.status_code == 201:
                data["status"] = 1
                data["data"] = res.content.decode()
            elif res.status_code == 400:
                if "Port must be unique" in res.content.decode():
                    data["message"] = ErrorStatusCode.PORT_MUST_UNIQUE, str("Port must be unique")
                elif "may not be empty" in res.content.decode():
                    data["message"] = ErrorStatusCode.OPERATION_ERROR, str("may not be empty")
                elif "found duplicated key" in res.content.decode():
                    data["message"] = ErrorStatusCode.NEXUS_HAS_EXISTED, str("repo has exist")
                else:
                    data["message"] = ErrorStatusCode.OPERATION_ERROR, str(res.content.decode())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["message"] = ErrorStatusCode.URL_NOT_EXISTED, str("api error")
            else:
                raise Exception(
                    "create " + repository_type + " repository went wrong! errmsg: " + str(res.content.decode()))
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            if "found duplicated key" in str(e):
                data["message"] = ErrorStatusCode.NEXUS_HAS_EXISTED, str(e)
            else:
                data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    # 编辑制品库
    def update_repository(self, repository_id, repository_type, parameters={}):
        """创建制品库"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
            if repository_type == "raw":
                url = self.nexus_addr + GET_RAW_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                    },
                    "raw": {
                        "contentDisposition": "ATTACHMENT" if not parameters.get(
                            "contentDisposition") else parameters.get("contentDisposition")
                    }
                }
            elif repository_type == "maven2":
                url = self.nexus_addr + GET_MAVEN_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "maven": {
                        "versionPolicy": "MIXED" if not parameters.get("versionPolicy") else parameters.get(
                            "versionPolicy"),
                        "layoutPolicy": "STRICT" if not parameters.get("layoutPolicy") else parameters.get(
                            "layoutPolicy")
                    }
                }
            elif repository_type == "docker":
                url = self.nexus_addr + GET_DOCKER_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default",
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "docker": {
                        "v1Enabled": "false" if not parameters.get("v1Enabled") else parameters.get("v1Enabled"),
                        "forceBasicAuth": "true" if not parameters.get("forceBasicAuth") else parameters.get(
                            "forceBasicAuth"),
                        "httpPort": 8082 if not parameters.get("httpPort") else parameters.get("httpPort"),
                        # "httpsPort": 8086 if not parameters.get("httpsPort") else parameters.get("httpsPort")
                    },
                    "cleanup": {
                        "policyNames": [
                            "string"
                        ]
                    },
                }
            elif repository_type == "proxy_docker":
                url = self.nexus_addr + GET_PROXY_DOCKER_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default",
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                    },
                    "docker": {
                        "v1Enabled": "false" if not parameters.get("v1Enabled") else parameters.get("v1Enabled"),
                        "forceBasicAuth": "true" if not parameters.get("forceBasicAuth") else parameters.get(
                            "forceBasicAuth"),
                        "httpPort": 8082 if not parameters.get("httpPort") else parameters.get("httpPort"),
                        # "httpsPort": 8086 if not parameters.get("httpsPort") else parameters.get("httpsPort")
                    },
                    "cleanup": {
                        "policyNames": [
                            "string"
                        ]
                    },
                    "proxy": {
                        "remoteUrl": parameters.get("remoteUrl"),
                        "contentMaxAge": 1440 if not parameters.get("contentMaxAge") else parameters.get(
                            "contentMaxAge"),
                        "metadataMaxAge": 1440 if not parameters.get("metadataMaxAge") else parameters.get(
                            "metadataMaxAge")
                    },
                    "negativeCache": {
                        "enabled": "true" if not parameters.get("enabled") else parameters.get("enabled"),
                        "timeToLive": 1440 if not parameters.get("timeToLive") else parameters.get("timeToLive")
                    },
                    "dockerProxy": {
                        "indexType": "HUB" if not parameters.get("indexType") else parameters.get("indexType"),
                        # "indexUrl": "string" if not parameters.get("indexUrl") else parameters.get("indexUrl")
                    },
                    "httpClient": {
                        "blocked": "false",
                        "autoBlock": "true",
                        "connection": {
                            "retries": 0,
                            "userAgentSuffix": "string",
                            "timeout": 60,
                            "enableCircularRedirects": "false",
                            "enableCookies": "false",
                            "useTrustStore": "false"
                        },
                        "authentication": {
                            "type": "username",
                            "username": "string",
                            "password": "string",
                            "ntlmHost": "string",
                            "ntlmDomain": "string"
                        }
                    }
                }
                if parameters.get("httpsPort"):
                    form_data["docker"]["httpsPort"] = parameters.get("httpsPort")
            elif repository_type == "pypi":
                url = self.nexus_addr + GET_PYPI_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                    }
                }
            elif repository_type == "helm":
                url = self.nexus_addr + GET_HELM_REPOSITORY_DETAIL.format(repository_id=repository_id)
                form_data = {
                    "name": repository_id,
                    "online": "true" if not parameters.get("online") else parameters.get("online"),
                    "storage": {
                        "blobStoreName": "default" if not parameters.get("blobStoreName") else parameters.get(
                            "blobStoreName"),
                        "strictContentTypeValidation": "false" if not parameters.get(
                            "strictContentTypeValidation") else parameters.get("strictContentTypeValidation"),
                        "writePolicy": "ALLOW" if not parameters.get("writePolicy") else parameters.get(
                            "writePolicy")
                    },
                    "cleanup": {
                        "policyNames": ["string"] if not parameters.get("policyNames") else parameters.get(
                            "policyNames")
                    },
                    "component": {"proprietaryComponents": "true"}
                }
            else:
                raise Exception("tool type error")
            print("编辑制品库form_data", type(form_data), form_data)
            res = req.put(url, data=json.dumps(form_data), headers=headers)
            res.encoding = 'utf-8'
            print("编辑制品库API返回结果", res.content.decode(), res.status_code)
            if res.status_code in [201, 204]:
                data["status"] = 1
                data["data"] = res.content.decode()
            elif res.status_code == 400:
                if "Port must be unique" in res.content.decode():
                    data["message"] = ErrorStatusCode.PORT_MUST_UNIQUE, str("Port must be unique")
                elif "may not be empty" in res.content.decode():
                    data["message"] = ErrorStatusCode.OPERATION_ERROR, str("may not be empty")
                elif "found duplicated key" in res.content.decode():
                    data["message"] = ErrorStatusCode.NEXUS_HAS_EXISTED, str("repo has exist")
                else:
                    data["message"] = ErrorStatusCode.OPERATION_ERROR, str(res.content.decode())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["message"] = ErrorStatusCode.URL_NOT_EXISTED, str("api error")
            else:
                raise Exception(
                    "update " + repository_type + " repository went wrong! errmsg: " + str(res.content.decode()))
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            if "found duplicated key" in str(e):
                data["message"] = ErrorStatusCode.NEXUS_HAS_EXISTED, str(e)
            else:
                data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def delete_repository(self, repository_id):
        "删除制品库"
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            url = self.nexus_addr + DELETE_REPOSITORY.format(repository_id=repository_id)
            headers = {
                'accept': 'application/json'
            }
            res = req.delete(url, headers=headers)
            res.encoding = 'utf-8'
            print("res.content.decode()", res.content.decode(), res.status_code)
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = str(res.content.decode())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["message"] = ErrorStatusCode.REPOSITORY_NOT_EXISTED, str("Repository not found")
            else:
                # data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str(res.content.decode())
                raise Exception("delete_repository went wrong! errmsg: " + res.text)
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def get_component_list(self, repository_id, continuationToken=None):
        """获取当前仓库全部组件列表"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_COMPONENT_LIST
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            dic = {"repository": repository_id,"continuationToken": continuationToken}
            res = req.get(url, headers=headers, params=dic)

            res.encoding = 'utf-8'
            # print("resres", res.status_code, res.content.decode())
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = res.json()
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["status"] = 1
                data["data"] = []
                # data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("NOT FOUND")

            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)

        if data["status"] == 1 and data["data"]:
            for component in data["data"].get("items", []):
                for asset in component.get("assets", []):
                    if "size" not in asset:
                        asset["size"] = self.get_asset_size(asset["downloadUrl"])
        return data

    # 获取文件大小
    def get_asset_size(self, download_url):
        try:
            res = requests.head(
                download_url,
                auth=(self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD),
                allow_redirects=True,
                verify=False
            )
            if res.status_code == 200:
                return int(res.headers.get('Content-Length', 0))
        except Exception:
            pass
        return 0

    # 获取当前仓库下的组件总数
    def get_component_count(self, repository_id):
        try:
            total_item_count = 0
            continuationToken = None
            while True:
                req = requests.session()
                req.verify = False
                req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
                url = self.nexus_addr + GET_COMPONENT_LIST
                headers = {
                    'accept': 'application/json'
                }
                dic = {"repository": repository_id, "continuationToken": continuationToken}
                res = req.get(url, headers=headers, params=dic)

                res_data = res.json()

                res.encoding = 'utf-8'
                if res.status_code == 200 or res.status_code == 204:
                    items = res_data.get("items", [])
                    total_item_count += len(items)
                else:
                    break
                continuationToken = res_data.get("continuationToken", None)
                if not continuationToken:
                    break

            return total_item_count
        except Exception as e:
            return 0

    def get_all_component(self, repository_id):
        """获取当前仓库全部组件列表"""
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        # writable check
        url = self.nexus_addr + GET_COMPONENT_LIST
        # print("url", url)
        headers = {
            'accept': 'application/json'
        }
        new_list = []
        continuationToken = None
        try:
            while True:
                dic = {"repository": repository_id, "continuationToken": continuationToken}
                res = req.get(url, headers=headers, params=dic)
                res.encoding = 'utf-8'
                if res.status_code == 200 or res.status_code == 204:
                    res_dic = res.json()
                    continuationToken = res_dic.get("continuationToken")
                    new_list.extend(res_dic.get("items", []))
                if not continuationToken:
                    break
                # print("resres", res.status_code, res.content.decode())

        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
        except Exception as e:
            print("Exception", e)
        return new_list

    def search_component(self, repository=None, format=None, name=None, continuationToken=None):
        """获取当前仓库全部组件列表"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + SEARCH
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            dic = {}
            if repository: dic["repository"] = repository
            if format: dic["format"] = format
            if name: dic["name"] = name
            if continuationToken: dic["continuationToken"] =  continuationToken
            print("continuationToken", dic)
            res = req.get(url, headers=headers, params=dic)
            print("search_component", res.url)
            res.encoding = 'utf-8'
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = res.json()
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["status"] = 1
                data["data"] = []
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        # except Exception as e:
        #     data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def get_component(self, id=None):
        """获取当前仓库一条组件"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_COMPONENT.format(id=id)
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            # print("resres", res.status_code, res.content.decode())
            if res.status_code == 200 or res.status_code == 204:
                data["status"] = 1
                data["data"] = res.json()
                # print(res.content, res.text, res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("连接出错！无法访问该工具，请确认配置后提交!")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("没有操作权限")
            elif res.status_code == 404 or res.status_code == 422:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("资源不存在")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def update_component(self, file=None, format=None, **kwargs):
        """上传组件"""
        data = {"status": 0, "message": "success", "data": None}
        print("kwargs", kwargs)
        try:
            req_g = requests.session()
            req_g.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req_g.verify = False
            headers = {
                # 'content-type': 'application/json',
                'content-type': 'multipart/form-data; boundary=something'
            }
            url = self.nexus_addr + UPLOAD_COMPONENT + "?repository=" + str(kwargs.get("repository_id", ""))
            # print("url", url)
            if format == "pypi":
                files = {
                    "pypi.asset": file
                }
                res = req_g.post(url, files=files)
            elif format == "raw":
                files = {
                    "raw.asset1": file
                }
                data = {
                    "raw.asset1.filename": kwargs.get("filename", ""),
                    "directory": "/" if kwargs.get("directory", "/") else "/"
                }
                res = req_g.post(url, data=data, files=files)
            elif format == "docker":
                files = {
                    "docker.asset": file
                }
                res = req_g.post(url, files=files)
            elif format == "maven2":
                files = {
                    "maven2.asset1": file
                }
                data = {
                    # 分组名
                    "maven2.groupId": kwargs.get("groupId", ""),
                    # 工程名
                    "maven2.artifactId": kwargs.get("artifactId", ""),
                    # 版本
                    "maven2.version": kwargs.get("version", ""),
                    # 扩展
                    "maven2.asset1.extension": kwargs.get("extension", ""),
                    # "maven2.asset1.classifier": kwargs.get("classifier", ""),
                    # Generate a POM file with these coordinates
                    # "maven2.generate-pom": kwargs.get("generate_pom", False),
                    # "maven2.packaging": kwargs.get("packaging", "")
                }
                res = req_g.post(url, files=files, data=data)
            else:
                raise Exception("tool type error")

            res.encoding = 'utf-8'
            print("status_code", res.status_code)
            print("update_component-code-error", res.content.decode(), res.status_code, type(res.content.decode()))
            if res.status_code == 204 or res.status_code == 200 or res.status_code == 201:
                data["status"] = 1
                data["data"] = "upload success"
            elif "not allow" in res.content.decode():
                data["message"] = ErrorStatusCode.REPO_NOT_UPDATE, str(res.content.decode())
            elif res.status_code == 400:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str(res.content.decode())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["message"] = ErrorStatusCode.SERVER_ERROR, str("authentication error")
            else:
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str(res.content.decode())
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            if "tool type error" in str(e):
                data["message"] = ErrorStatusCode.REPOSITORY_ASSET_NOT_UPLOAD, str(e)
            else:
                data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def delete_component(self, id):
        "删除当前制品库内组件"
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            url = self.nexus_addr + DELETE_COMPONENT.format(id=id)
            headers = {
                'accept': 'application/json'
            }
            res = req.delete(url, headers=headers)
            res.encoding = 'utf-8'
            # print("res.content.decode()", url, res.content.decode(), res.status_code)
            if res.status_code == 204:
                data["status"] = 1
                data["data"] = str(res.content.decode())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("NOT FOUND")

            else:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str(res.content.decode())
                # raise Exception("delete_repository went wrong! errmsg: " + res.text)
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def get_assets(self, id=None):
        """获取单一资产"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_ASSETS.format(id=id)
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            # print("resres", res.status_code, res.content.decode())
            if res.status_code == 200:
                data["status"] = 1
                data["data"] = res.json()
                # print(res.content, res.text, res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404 or res.status_code == 422:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("NOT FOUND")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def delete_assets(self, id=None):
        """获取单一资产"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_ASSETS.format(id=id)
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            res = req.delete(url, headers=headers)
            res.encoding = 'utf-8'
            # print("resres", res.status_code, res.content.decode())
            if res.status_code in [200, 204]:
                data["status"] = 1
                data["data"] = res.json()
                # print(res.content, res.text, res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404 or res.status_code == 422:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("NOT FOUND")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def get_blob_list(self, id=None):
        """获取blob"""
        data = {"status": 0, "message": "success", "data": None}
        try:
            req = requests.session()
            req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
            req.verify = False
            # writable check
            url = self.nexus_addr + GET_BLB_LIST.format(id=id)
            # print("url", url)
            headers = {
                'accept': 'application/json'
            }
            res = req.get(url, headers=headers)
            res.encoding = 'utf-8'
            # print("resres", res.status_code, res.content.decode())
            if res.status_code == 200:
                data["status"] = 1
                data["data"] = res.json()
                # print(res.content, res.text, res.json())
            elif res.status_code == 401:
                data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str("Authentication required")
            elif res.status_code == 403:
                data["message"] = ErrorStatusCode.USER_NOT_POWER, str("Insufficient permissions")
            elif res.status_code == 404 or res.status_code == 422:
                data["message"] = ErrorStatusCode.DATA_NOT_EXISTED, str("NOT FOUND")
            else:
                print("status_code-error", res.status_code)
                print("res.content-error", res.content)
                data["message"] = ErrorStatusCode.NEXUS_STATUS_ERROR, str("连接失败")
        except requests.exceptions.ConnectionError as e:
            print("requests.exceptions.ConnectionError", e)
            data["message"] = ErrorStatusCode.TOOL_CONNECTION_ERROR, str(e)
        except requests.exceptions.HTTPError as e:
            print("requests.exceptions.HTTPError", e)
            data["message"] = ErrorStatusCode.NEXUS_SERVER_ERROR, str(e)
        except Exception as e:
            data["message"] = ErrorStatusCode.OPERATION_ERROR, str(e)
        return data

    def get_privileges_by_role_id(self, nexus_role_id):
        # nexus 获取role的权限
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/roles/" + nexus_role_id + "?source=default"
        res = req.get(url, headers=headers)
        res.encoding = 'utf-8'
        print(res.text, type(res.text))
        privileges = json.loads(res.text)["privileges"]
        print(privileges)
        # privileges is a LIST
        return privileges

    def create_repository_privilege(self, repository_type, repository_id):
        # nexus上创建库的权限
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/privileges/repository-admin"
        form_data = {
            "name": repository_type + "-" + repository_id,
            "description": repository_id + " admin",
            "actions": [
                "ALL "
            ],
            "format": repository_type,
            "repository": repository_id
        }
        res = req.post(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 201:
            return True
        else:
            raise Exception("create_repository_privilege went wrong! errmsg: " + res.text)

    def delete_privilege(self, repository_type, repository_id):
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/privileges/" + repository_type + "-" + repository_id
        res = req.delete(url, headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 204:
            return True
        else:
            raise Exception("create_repository_privilege went wrong! errmsg: " + res.text)

    def get_role_list(self):
        # nexus 获取role的权限
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/roles/"
        res = req.get(url, headers=headers)
        res.encoding = 'utf-8'
        print("res.text", res.text)
        rolelist = json.loads(res.text)
        print(rolelist)
        # privileges is a LIST
        return rolelist

    def create_role(self, nexus_role, privilege):
        # nexus上创建role
        list1 = self.get_role_list()
        for fn in list1:
            if fn["id"] == nexus_role:
                return True
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        url = self.nexus_addr + "/service/rest/beta/security/roles"
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        form_data = {
            "id": nexus_role,
            "name": nexus_role,
            "description": nexus_role,
            "privileges": [
                privilege
            ],
            "roles": [
                "nx-anonymous"
            ]
        }
        res = req.post(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 200 or res.status_code == 204:
            return True
        else:
            raise Exception("create_role went wrong! errmsg: " + res.text)

    def grant_pris_to_role(self, nexus_role, privileges):
        # nexus上将库的权限授予role：NEXUS_PUBLIC_ACCOUNT
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        url = self.nexus_addr + "/service/rest/beta/security/roles/" + nexus_role
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        form_data = {
            "id": nexus_role,
            "name": nexus_role,
            "description": nexus_role,
            "privileges": privileges,
            "roles": [
                "nx-anonymous"
            ]
        }
        res = req.put(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 200 or res.status_code == 204:
            return True
        else:
            raise Exception("put_role went wrong! errmsg: " + res.text)

    def get_user_list(self):
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/users"
        res = req.get(url, headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            return res.text
        else:
            raise Exception("get_user_list went wrong! errmsg: " + res.text)

    def create_user(self, nexus_user_id, password, nexus_role):
        userlist = json.loads(self.get_user_list())
        for fn in userlist:
            if nexus_user_id == fn["userId"]:
                if self.delete_user(nexus_user_id):
                    self.create_user(nexus_user_id, password, nexus_role)
                return True
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/users"
        form_data = {
            "userId": nexus_user_id,
            "firstName": "nexus",
            "lastName": "nexus",
            "emailAddress": nexus_user_id + "@nexus.com",
            "password": password,
            "status": "active",
            "roles": [
                nexus_role
            ]
        }
        res = req.post(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 200 or res.status_code == 204:
            return True
        else:
            raise Exception("create_user went wrong! errmsg: " + res.text)

    def update_user(self, origin_user, nexus_user_id, password, nexus_role, status):
        # status is in ["active", "locked", "disabled", "changepassword"]
        # 目前nexus对这个接口的支持有问题，暂无法使用
        # userlist = json.loads(get_user_list())
        # for fn in userlist:
        #     if fn["userId"] == origin_user:
        #         user = fn
        #         break
        # req = requests.session()
        # req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        # headers = {
        #     'Content-Type': 'application/json',
        #     'accept': 'application/json'
        # }
        # url = self.nexus_addr + "/service/rest/beta/security/users"
        # user["roles"].append(nexus_role)
        # form_data = {
        #     "userId": nexus_user_id,
        #     "firstName": user["firstName"],
        #     "lastName": user["firstName"],
        #     "emailAddress": nexus_user_id + "@nexus.com",
        #     "source": user["source"],
        #     "status": user["status"],
        #     "readOnly": user["readOnly"],
        #     "roles": [
        #         user["roles"]
        #     ],
        #     "externalRoles": user["externalRoles"]
        # }
        # res = req.put(url, data=json.dumps(form_data), headers=headers)
        # res.encoding = 'utf-8'
        # print(res.status_code, res.text)
        # if res.status_code == 200 or res.status_code == 204:
        #     return True
        # else:
        #     raise Exception ("update_user went wrong! errmsg: " + res.text)
        pass

    def change_user_password(self, nexus_user_id, password):
        # status is in ["active", "locked", "disabled", "changepassword"]
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'Content-Type': 'text/plain',
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/users/" + nexus_user_id + "/change-password"
        res = req.put(url, data=password, headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 204:
            return True
        else:
            raise Exception("change_user_password went wrong! errmsg: " + res.text)

    def delete_user(self, nexus_user_id):
        # status is in ["active", "locked", "disabled", "changepassword"]
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        url = self.nexus_addr + "/service/rest/beta/security/users/" + nexus_user_id
        res = req.delete(url, headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 204:
            return True
        else:
            raise Exception("delete_user_password went wrong! errmsg: " + res.text)

    def update_maven_repository(self, repository_id, recipe_type):
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        if recipe_type == "proxy":
            url = self.nexus_addr + "/service/rest/beta/repositories/maven/hosted/" + repository_id
            form_data = {
                "name": "internal",
                "online": "true",
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": "true"
                },
                "cleanup": {
                    "policyNames": "weekly-cleanup"
                },
                "proxy": {
                    "remoteUrl": "https://registry.npmjs.org",
                    "contentMaxAge": 1440,
                    "metadataMaxAge": 1440
                },
                "negativeCache": {
                    "enabled": "false",
                    "timeToLive": 1440
                },
                "httpClient": {
                    "blocked": "false",
                    "autoBlock": "false",
                    "connection": {
                        "retries": 0,
                        "userAgentSuffix": "string",
                        "timeout": 60,
                        "enableCircularRedirects": "false",
                        "enableCookies": "false"
                    },
                    "authentication": {
                        "type": "username",
                        "username": "string",
                        "ntlmHost": "string",
                        "ntlmDomain": "string"
                    }
                },
                "routingRule": "string",
                "maven": {
                    "versionPolicy": "MIXED",
                    "layoutPolicy": "STRICT"
                }
            }
        elif recipe_type == "hosted":
            url = self.nexus_addr + "/service/rest/beta/repositories/maven/proxy/" + repository_id
            form_data = {
                "name": "internal",
                "online": "true",
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": "true",
                    "writePolicy": "allow_once"
                },
                "cleanup": {
                    "policyNames": "weekly-cleanup"
                },
                "maven": {
                    "versionPolicy": "MIXED",
                    "layoutPolicy": "STRICT"
                }
            }
        res = req.put(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 204:
            return True
        else:
            raise Exception("delete_user_password went wrong! errmsg: " + res.text)

    def update_docker_repository(self, repository_id, recipe_type):
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        if recipe_type == "hosted":
            url = self.nexus_addr + "/beta/repositories/docker/hosted/" + repository_id
            form_data = {
                "name": "internal",
                "online": "true",
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": "true",
                    "writePolicy": "allow_once"
                },
                "cleanup": {
                    "policyNames": "weekly-cleanup"
                },
                "docker": {
                    "v1Enabled": "false",
                    "forceBasicAuth": "true",
                    "httpPort": 8082,
                    "httpsPort": 8083
                }
            }
        elif recipe_type == "proxy":
            url = self.nexus_addr + "/beta/repositories/docker/proxy/" + repository_id
            form_data = {
                "name": "internal",
                "online": "true",
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": "true"
                },
                "cleanup": {
                    "policyNames": "weekly-cleanup"
                },
                "proxy": {
                    "remoteUrl": "https://registry.npmjs.org",
                    "contentMaxAge": 1440,
                    "metadataMaxAge": 1440
                },
                "negativeCache": {
                    "enabled": "false",
                    "timeToLive": 1440
                },
                "httpClient": {
                    "blocked": "false",
                    "autoBlock": "false",
                    "connection": {
                        "retries": 0,
                        "userAgentSuffix": "string",
                        "timeout": 60,
                        "enableCircularRedirects": "false",
                        "enableCookies": "false"
                    },
                    "authentication": {
                        "type": "username",
                        "username": "string",
                        "ntlmHost": "string",
                        "ntlmDomain": "string"
                    }
                },
                "routingRule": "string",
                "docker": {
                    "v1Enabled": "false",
                    "forceBasicAuth": "true",
                    "httpPort": 8082,
                    "httpsPort": 8083
                },
                "dockerProxy": {
                    "indexType": "HUB",
                    "indexUrl": "string"
                }
            }
        res = req.put(url, data=json.dumps(form_data), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 204:
            return True
        else:
            raise Exception("delete_user_password went wrong! errmsg: " + res.text)

    def update_raw_repository(self, repository_id, recipe_type):
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        req.verify = False
        headers = {
            'accept': 'application/json'
        }
        if recipe_type == "hosted":
            form_data = {

            }
        elif recipe_type == "proxy":
            form_data = {

            }
        pass
        # res = req.put(url, data=json.dumps(form_data), headers=headers)
        # res.encoding = 'utf-8'
        # if res.status_code == 204:
        #    return True
        # else:
        #    raise Exception ("delete_user_password went wrong! errmsg: " + res.text)


if __name__ == '__main__':
    # 6937707a-8b01-317d-9bd1-dd1d76e8dbb4
    nexus_api = NexusApi(url="http://127.0.0.1:8888/", username="admin", password="123456.coM")
    status = nexus_api.status()
    # get_component = nexus_api.get_component()
    # get_repository = nexus_api.get_repository()
    # print("get_repository", get_repository)
    get_data1 = nexus_api.get_component("T3BzQW55LXRlc3QtZGVtbzpiZjBiY2ZmMzM5YmVlZjA2YzY5YjBmNDE3YmQ2YzYwYw")
    # get_data1 = nexus_api.delete_assets("T3BzQW55LXRlc3QtZGVtbzpkNTMyOThlNTA3NWM3ZWNlYWMxYjg3YmVkODViMjU4ZQ")
    message = get_data1.get("message")
    print(get_data1)
    # print(type(message[0]))
    print(message[1])

    # get_data2 = nexus_api.get_assets(id="b3BzYW55LXJlZ2lzdHJ5OjdmNjM3OWQzMmY4ZGQ3OGY5YzJkNjYwMjEwZTBkN2Ji")
    # print("status", status)
    print("get_component", get_data1)
    # print("get_component", get_data2)
