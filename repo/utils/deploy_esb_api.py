import json
import os
import subprocess

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from component.base_views import BaseView
from component.status_code import error, ErrorStatusCode, success, SuccessStatusCode
from repo.decorator import admin_auth
from repo.models import ToolsModel
from repo.utils import constant


class CloneProjectView(BaseView):
    @admin_auth
    def post(self, request):
        data = json.loads(request.body)
        project_url = data.get("project_url") or ""
        project_branch = data.get("project_branch") or ""
        api_token = data.get("api_token") or ""
        script_path = os.path.join(settings.UPLOAD_PATH, settings.UPLOAD_CACHE_PATH)

        # 校验 project_url 必须包含协议分隔符，避免格式错误
        if "//" not in project_url:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="project_url error", language=self.ops_language()))
        scheme, _, rest = project_url.partition("//")
        api_token_url = "{}//oauth2:{}@{}".format(scheme, api_token, rest)

        # subprocess 参数化调用（不经过 shell），杜绝命令注入
        cmd = ["git", "clone", "-b", project_branch, api_token_url]
        try:
            subprocess.run(cmd, cwd=script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        except Exception as e:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=str(e), language=self.ops_language()))
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, language=self.ops_language()))


class NexusRepositoryView(BaseView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            download_url = data.get("download_url")
            tool_query = ToolsModel.fetch_one(tool_type="repository")
            if not tool_query:
                return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))

            login_res = requests.get(url=download_url, auth=(tool_query.username, tool_query.api_token))
            if login_res.status_code == 200:
                name = download_url.split("/")[-1]
                script_url = os.path.join(settings.UPLOAD_NEXUS_PATH, name)
                script_path = os.path.join(settings.UPLOAD_PATH, script_url)
                with open(script_path, "wb") as f:
                    f.write(login_res.content)
                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, script_url, language=self.ops_language()))
            # if login_res.status_code == 404:
            #     return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="Nexus Project Not Found"))
            else:
                info = login_res.status_code
                return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, custom_message=info, language=self.ops_language()))

        except Exception as e:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="制品库下载失败请稍后再试或联系管理员{}".format(str(e)), language=self.ops_language()))

