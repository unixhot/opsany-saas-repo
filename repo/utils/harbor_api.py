import requests, json
from django.conf import settings


class HarborApi():
    def __init__(self):
        self.harbor_url = settings.HARBOR_URL
        self.username = settings.HARBOR_USERNAME
        self.password = settings.HARBOR_PASSWORD
        self.headers = {"Content-Type": "application/json"}

    # 获取镜像列表
    def get_project_list(self):
        try:
            url = f"{self.harbor_url}/api/v2.0/projects?page_size=100"
            response = requests.get(url, headers=self.headers, verify=False)
            project_list = []
            if response.status_code == 200:
                data = response.json()
                for i in data:
                    i["update_time"] = self.utc_time_to_str_time(i.get("update_time"))
                    i["creation_time"] = self.utc_time_to_str_time(i.get("creation_time"))
                    project_list.append(i)
                return True, project_list
            return False, f"Failed to get harbor project, message: {response.text}"
        except Exception as e:
            return False, f"Failed to get harbor project, message: {str(e)}"

    # 获取指定项目下的镜像列表
    def get_repository_list(self, project_name, page=1, per_page=10):
        try:
            url = f"{self.harbor_url}/api/v2.0/projects/{project_name}/repositories?page_size={per_page}&page={page}"
            response = requests.get(url, headers=self.headers, verify=False)
            repository_list = []
            if response.status_code == 200:
                data = response.json()
                for i in data:
                    i["creation_time"] = self.utc_time_to_str_time(i.get("creation_time"))
                    i["update_time"] = self.utc_time_to_str_time(i.get("update_time"))
                    repository_list.append(i)
                return True, repository_list
            return False, f"Failed to get harbor repository, message：{response.text}"
        except Exception as e:
            return False, f"Failed to get harbor repository, message： {str(e)}"

    # 获取指定项目下镜像总数
    def project_harbor_total(self, project_name):
        try:
            url = f"{self.harbor_url}/api/v2.0/projects/{project_name}/summary"
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                repo_count = int(data.get("repo_count"))
                return True, repo_count
            return False, response.text
        except Exception as e:
            return False, str(e)

    def utc_time_to_str_time(self, utc_time):
        try:
            # 输入：2023-07-12T12:58:37.000Z
            # 输出：2023-07-12 20:58
            from datetime import datetime
            from pytz import timezone
            dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S.%fZ")

            # 将 UTC 时间转换为北京时间（中国时区，UTC+8）
            china_tz = timezone('Asia/Shanghai')
            dt_china = dt.replace(tzinfo=timezone('UTC')).astimezone(china_tz)

            # 格式化为目标格式
            formatted_time = dt_china.strftime("%Y-%m-%d %H:%M")
            return formatted_time
        except:
            return utc_time
