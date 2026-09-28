import requests, json
from component.status_code import ErrorStatusCode


BASE_URL = "/service/rest/v1"
NEXUS_STATUS = BASE_URL + "/status/"  # 连接状态
GET_REPOSITORY_LIST = BASE_URL + "/repositories/"  # 获取制品库列表
CREATE_REPOSITORY = BASE_URL + "/script/"  # 新建制品库
DELETE_REPOSITORY = BASE_URL + "/repositories/{repository_id}"  # 删除制品库

CREATE_RAW_REPOSITORY = BASE_URL + "/repositories/raw/hosted/"  # 创建raw库
CREATE_PYPI_REPOSITORY = BASE_URL + "/repositories/pypi/hosted/"  # 创建pypi库
CREATE_MAVEN_REPOSITORY = BASE_URL + "/repositories/maven/hosted/"  # 创建maven库
CREATE_DOCKER_REPOSITORY = BASE_URL + "/repositories/docker/hosted/"  # 创建docker库

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



def get_repository(self):
    """获取制品库列表及容量大小"""
    data = {"status": 0, "message": "success", "data": None}
    try:
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        # writable check
        url = self.nexus_addr + GET_REPOSITORY_LIST
        headers = {
            'accept': 'application/json'
        }
        res = req.get(url, headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 200 or res.status_code == 204:
            data["status"] = 1
            repositories = res.json()
            repository_list = []
            for repository in repositories:
                repository_id = repository['name']
                repository_url = self.nexus_addr + f"/repository/{repository_id}"
                repository_size = self.get_repository_size(repository_url)
                repository_data = {
                    'name': repository_id,
                    'size': repository_size
                }
                repository_list.append(repository_data)
            data['data'] = repository_list
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

def get_repository_size(self, repository_url):
    """获取制品库容量大小"""
    try:
        req = requests.session()
        req.auth = (self.NEXUS_ADMIN_ACCOUNT, self.NEXUS_ADMIN_ACCOUNT_PASSWORD)
        url = repository_url + "/storage"
        res = req.get(url)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            storage_info = res.json()
            used_size = storage_info['data']['storageSize']
            return used_size
        else:
            print("status_code-error", res.status_code)
            print("res.content-error", res.content)
            return None
    except requests.exceptions.ConnectionError as e:
        print("requests.exceptions.ConnectionError", e)
        return None
    except requests.exceptions.HTTPError as e:
        print("requests.exceptions.HTTPError", e)
        return None
    except Exception as e:
        print("Exception", e)
        return None
