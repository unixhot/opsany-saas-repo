import json
import datetime

import mongoengine
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.views import View

from component.base_views import BaseView
from repo.decorator import admin_auth
from repo.models import ApplicationModel, ApplicationUserRoleModel, RepositoryTagsModel
from repo.utils.component import GetUserInfo
from component.status_code import *
from repo.models import ToolsModel, RepositoryModel, ApplicationRepoModel, RepositoryGuideModel, RawComponentModel, \
    RawComponentGroupModel
from repo.utils import constant
from repo.utils.constant import REPOSITORY_TYPE_LIST
from repo.utils.harbor_api import HarborApi
from repo.utils.jenkins_api import flash_all_tool_status
from repo.utils.repo import BusinessTree, RepositoryTags
from repo.utils.sync_data import nexus_sync_data, nexus_sync_component
from repo.utils.nexus_api import NexusApi


# 获取制品库格式列表
class RepositoryFormatView(BaseView):
    def get(self, request):
        data = list()
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))

        for tool_type in REPOSITORY_TYPE_LIST:
            api_addr = tool_query.api_addr
            if str(api_addr)[-1] != "/":
                api_addr = str(api_addr) + "/"
            url = api_addr + "repository/"
            data.append({"format_name": tool_type[0], "url": url})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))


# 获取制品库，新建制品库，删除制品库
class NexusRepositoryView(BaseView):
    def get(self, request):
        """
            获取制品仓库
        :param request:
        :return:
        """
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        # 同步制品库
        nexus_sync_data()

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))
        kwargs = request.GET.dict()
        format_type = kwargs.get("format_type")
        list_type = kwargs.get("list_type", "all")
        search_type = kwargs.get("search_type", None)
        search_data = kwargs.get("search_data", None)
        code = kwargs.get("code", None)

        if search_type == "repo_name" and search_data:
            search_type = "name"

        application_query = ApplicationModel.fetch_one(code=code)
        if not application_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

        if user_query.role not in [1]:
            # if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=application_query):
            if not user_query.is_app_auth(application_query):
                return JsonResponse(error(ErrorStatusCode.USER_NOT_APPLICATION_POWER, language=self.ops_language()))

        public_dic = {"is_app": False}
        inner_dic = {"is_app": True}
        app_list = []
        # 是否收藏
        if list_type == "tags":
            tags_queryset = RepositoryTagsModel.fetch_all(user_info=user_query)
            app_list = []
            for tags_query in tags_queryset:
                try:
                    app_list.append(tags_query.repository.code)
                except Exception:
                    res = tags_query.delete()
            public_dic["code__in"] = app_list

        if search_type and search_data:
            public_dic[search_type + "__icontains"] = search_data
            inner_dic[search_type + "__icontains"] = search_data

        public_repo_queryset = RepositoryModel.fetch_all(**public_dic)
        public_list = [repo.to_tags_dict(user_query) for repo in public_repo_queryset]

        if user_query.role != 1:
            public_repo_queryset = RepositoryModel.fetch_all(**public_dic)
            public_list = [repo.to_tags_dict(user_query) for repo in public_repo_queryset]

            _, _, repo_read_code_list = user_query.get_code_list(application_query, id_type="repo")
            if list_type == "tags":
                repo_code_list = list(set(app_list) & set(repo_read_code_list[0]))
            else:
                repo_code_list = repo_read_code_list[0]
            inner_dic["code__in"] = repo_code_list

            inner_repo_queryset = RepositoryModel.fetch_all(**inner_dic)
            inner_list = [repo.to_tags_dict(user_query, repo_read_code_list) for repo in inner_repo_queryset]
            all_data = {"inner_list": inner_list, "public_list": public_list}
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, all_data, language=self.ops_language()))

        # 当前应用所关联的制品库
        app_repo_queryset = ApplicationRepoModel.fetch_all(application=application_query)
        app_code_list = [app_repo_query.repo.code for app_repo_query in app_repo_queryset]

        if list_type == "tags":
            code_list = list(set(app_list) & set(app_code_list))
        else:
            code_list = app_code_list
        inner_dic["code__in"] = code_list
        inner_repo_queryset = RepositoryModel.fetch_all(**inner_dic)
        inner_list = [repo.to_tags_dict(user_query) for repo in inner_repo_queryset]

        all_data = {"inner_list": inner_list, "public_list": public_list}
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, all_data, language=self.ops_language()))

    # 弃用
    def get_old(self, request):
        """
            获取制品仓库
        :param request:
        :return:
        """
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        # 同步制品库
        nexus_sync_data()

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))
        kwargs = request.GET.dict()
        format_type = kwargs.get("format_type")
        list_type = kwargs.get("list_type", "all")
        search_type = kwargs.get("search_type", None)
        search_data = kwargs.get("search_data", None)
        code = kwargs.get("code", None)
        application_query = ApplicationModel.fetch_one(code=code)
        if not application_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

        if user_query.role not in [1]:
            if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=application_query):
                return JsonResponse(error(ErrorStatusCode.USER_NOT_APPLICATION_POWER, language=self.ops_language()))

        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

        public_dic = {"is_app": False}
        inner_idc = {}
        # 是否收藏
        if list_type == "tags":
            tags_queryset = RepositoryTagsModel.fetch_all(user_info=user_query)
            app_list = []
            app_id_list = []
            for tags_query in tags_queryset:
                try:
                    app_list.append(tags_query.repository.code)
                    app_id_list.append(tags_query.repository.id)
                except Exception:
                    res = tags_query.delete()
            public_dic["code__in"] = app_list
            inner_idc["repo__in"] = app_id_list
        # 是否搜索
        if search_type and search_data:
            public_dic["name" + "__icontains"] = search_data
            # 与应用关联的制品
            repo_query_set = RepositoryModel.fetch_all(name__icontains=search_data)     # 获取符合模糊查询条件的制品库
            repo_id_list = [repo.id for repo in repo_query_set]     # 获取每个制品库的id
            app_repo_queryset = list(set(ApplicationRepoModel.fetch_all(application=app_query, **inner_idc)))
            app_repo_queryset = [app_repo for app_repo in app_repo_queryset if app_repo.repo.id in repo_id_list]
        else:
            # 如果没有查询条件就正常展示所有与当前应用相关的制品库
            app_repo_queryset = list(set(ApplicationRepoModel.fetch_all(application=app_query, **inner_idc)))

        if format_type:
            public_dic.update(format=format_type)
        repo_query_set = RepositoryModel.fetch_all(**public_dic)
        public_list = [repo.to_tags_dict(user_query) for repo in repo_query_set]

        inner_list = []
        for app_repo in app_repo_queryset:
            if format_type:
                if app_repo.repo.format == format_type:
                    inner_list.append(app_repo.repo.to_tags_dict(user_query))
            else:
                inner_list.append(app_repo.repo.to_tags_dict(user_query))
        all_data = {"inner_list": inner_list, "public_list": public_list}
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, all_data, language=self.ops_language()))

    def post(self, request):
        """
        新建制品库
        :param request:
        {
            "code":10,  # 应用code
            "repository_type":"raw",  # 制品库格式
            "repository_id":"pypi_test",  # 制品库名称
            "inner":"true",     # 是否应用内
            "describe":"描述",
        }
        :return:
        """

        kwargs = json.loads(request.body)
        repository_id = kwargs.get("repository_id")
        code = kwargs.pop("code", None)
        inner = kwargs.get("inner", None)
        describe = kwargs.get("describe", "")
        repository_type = kwargs.get("repository_type")
        proxy_docker = kwargs.get("proxy_docker", None)
        parameters = kwargs.get("parameters", {})
        docker_user_url = kwargs.get("docker_user_url", "")
        writePolicy = kwargs.get("writePolicy", "ALLOW")
        parameters.update(writePolicy=writePolicy)
        if not all([repository_id, repository_type, code]):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        if repository_type not in dict(constant.REPOSITORY_TYPE_LIST).keys():
            return JsonResponse(error(ErrorStatusCode.TYPE_NOT_EXISTED, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, {}, language=self.ops_language()))

        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.create_repository(repository_id, repository_type, parameters, proxy_docker)
        if res.get("status"):
            # 本地保存
            dic = {"name": repository_id, "describe": describe, "attributes": parameters, "format": repository_type,
                   "active_time": datetime.datetime.now(), "user": user_query, "docker_user_url": docker_user_url}
            repo_query = RepositoryModel.fetch_one(name=repository_id)
            if not repo_query:
                repo_query = RepositoryModel.create(**dic)
            if inner:
                dic["is_app"] = True
                if not ApplicationRepoModel.fetch_one(application=app_query, repo=repo_query):
                    ApplicationRepoModel.create(application=app_query, repo=repo_query)
            else:
                app_repo = ApplicationRepoModel.fetch_one(application=app_query, repo=repo_query)
                if app_repo:
                    app_repo.delete()
                dic["is_app"] = False
            repo_query.update(**dic)

            nexus_sync_data()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, res.get("data"), language=self.ops_language()))
        else:
            return JsonResponse(error(*res.get("message"), language=self.ops_language()))

    def delete(self, request):
        """
        删除制品库
        :param request:
        {
            "code": 10,  # 应用code
            "repository_id":"name"  # 制品库名称
        }
        :return:
        """
        # 同步数据
        nexus_sync_data()
        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))

        try:
            kwargs = json.loads(request.body)
            code = kwargs.get("code")
            repository_id = kwargs.get("repository_id")
            if not repository_id:
                return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))

            app_query = ApplicationModel.fetch_one(code=code)
            if not app_query:
                return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

            # 校验工具
            tool_query = ToolsModel.fetch_one(tool_type="repository")
            if not tool_query:
                return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
            if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
                return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
            print(tool_query.to_dict())
            repo_query = RepositoryModel.fetch_one(name=repository_id)

            # 判断权限
            if user_query.role != 1:
                status = repo_query.is_auth_delete(user_query)
                if not status:
                    return JsonResponse(error(ErrorStatusCode.USER_NOT_POWER, language=self.ops_language()))

            res = NexusApi(**tool_query.link_tool_dict()).delete_repository(repository_id)
            print("res", res)
            if not res.get("status"):
                return JsonResponse(error(*res.get("message"), language=self.ops_language()))
            try:
                repo_query.delete()
            except Exception:
                pass
            return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS, language=self.ops_language()))
        except Exception as e:
            return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, str(e), language=self.ops_language()))


# 修改获取制品库描述应用权限
class RepoView(BaseView):
    def get(self, request):
        """
        获取制品库信息
        :param request:
        {
            "code": 10,  # 应用code
            "repository_id":"name"  # 制品库名称
        }
        :return:
        """
        # 同步数据
        # nexus_sync_data()
        code = request.GET.get("code")
        repository_id = request.GET.get("repository_id")
        repository_type = request.GET.get("repository_type")
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, {}, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())

        repository = RepositoryModel.fetch_one(name=repository_id)
        data = repository.to_dict() if repository else []
        repo_type = repository.type or None
        writePolicy = None
        if repo_type == "hosted" and repository_type in ["raw", "maven2", "maven", "docker", "pypi", "helm"]:
            repo_detail = nexus_api.get_repository_detail(repository_type, repository_id)
            if repo_detail.get("status"):
                writePolicy = repo_detail.get("data", {}).get("storage", {}).get("writePolicy")
                httpPort = repo_detail.get("data", {}).get("docker", {}).get("httpPort", None)
                if repository_type == "docker" and httpPort:
                    data.update(httpPort=httpPort)
        data.update(writePolicy=writePolicy)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))

    def put(self, request):
        """
        修改制品库权限，描述
        :param request:
        {
            "code": 10,  # 应用code
            "repository_id":"name",  # 制品库名称
            "inner":"true",     # 是否应用内
            "describe":"描述",
        }
        :return:
        """

        # 校验工具
        kwargs = json.loads(request.body)
        repository_id = kwargs.get("repository_id")
        repository_type = kwargs.get("format")
        repo_type = kwargs.get("type")
        code = kwargs.get("code")
        inner = kwargs.get("inner")
        describe = kwargs.get("describe", "")
        writePolicy = kwargs.get("writePolicy", "ALLOW")
        httpPort = kwargs.get("httpPort", 8082)
        parameters = {"writePolicy": writePolicy}
        if repository_type == "docker":
            parameters.update(httpPort=httpPort)

        dic = {
            "describe": describe,
            "active_time": datetime.datetime.now()
        }

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))

        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        repo = RepositoryModel.fetch_one(name=repository_id)
        if not repo:
            return JsonResponse(error(ErrorStatusCode.REPOSITORY_NOT_EXISTED, language=self.ops_language()))

        # 判断权限
        if user_query.role != 1:
            status = repo.is_auth_update(user_query)
            if not status:
                return JsonResponse(error(ErrorStatusCode.USER_NOT_POWER, language=self.ops_language()))
        app_repo = ApplicationRepoModel.fetch_one(application=app_query, repo=repo)
        if inner:
            dic["is_app"] = True
            if not app_repo:
                ApplicationRepoModel.create(application=app_query, repo=repo)
        else:
            if app_repo: app_repo.delete()
            repo.update(is_app=False)

        if repository_type not in dict(constant.REPOSITORY_TYPE_LIST).keys():
            return JsonResponse(error(ErrorStatusCode.TYPE_NOT_EXISTED, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())

        # 指定类型的制品库不可编辑
        valid_repository_types = ['raw', 'maven2', 'docker', 'pypi', 'helm']
        valid_repo_types = ['hosted', 'proxy']

        # 判断是否支持编辑
        if repository_type not in valid_repository_types or repo_type != 'hosted':
            pass
        else:
            update_write_policy = nexus_api.update_repository(repository_id, repository_type, parameters=parameters)
            if not update_write_policy.get("status"):
                error_message = update_write_policy.get("message")
                return JsonResponse(
                    error(ErrorStatusCode.OPERATION_ERROR, custom_message="修改部署策略失败：{}".format(error_message)))

        repo.update(**dic)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, language=self.ops_language()))


class NexusRepositoryReconfigView(BaseView):
    def put(self, request):
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, language=self.ops_language()))


class RepositoryGuideView(BaseView):
    def get(self, request):
        """
        获取制品库指引
        :param request:
        {
            "code": 10,
            "repository_format", "raw",
            "repository_id", "name",
        }
        :return:
        """
        kwargs = request.GET.dict()
        code = kwargs.get("code", None)
        repository_format = kwargs.get("repository_format")
        repository_id = kwargs.get("repository_id")
        if not all([repository_id, repository_format, code]):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        repository = RepositoryModel.fetch_one(name=repository_id)
        if not repository:
            return JsonResponse(error(ErrorStatusCode.REPOSITORY_NOT_EXISTED, language=self.ops_language()))
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query: return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        repository_guide = RepositoryGuideModel.fetch_one(format=repository_format)
        repository_url = repository.url
        repository_docker_user_url = repository.docker_user_url
        try:
            if repository_format == "docker" and not repository_docker_user_url:
                repository_url = repository_url.lower()
            if repository_format == "docker" and repository_docker_user_url:
                repository_url = repository_docker_user_url.lower()
        except:
            repository_url = repository.url

        if repository_guide:
            data = repository_guide.to_dict()
            data["content"] = data.get("content", "{url}").format(url=repository_url, id=repository.name)
        else:
            data = {"format": repository_format, "content": "#### 无"}
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))

    def post(self, request):
        print("POST", request.POST.dict())
        repository_format = request.POST.get("repository_format")
        repository_guide = request.POST.get("repository_guide")
        if not all([repository_format, repository_guide]):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        print("repository_format", repository_format, repository_guide)
        repository_guide_query = RepositoryGuideModel.fetch_one(format=repository_format)
        print("repository_guide_query", repository_guide_query)
        if repository_guide_query:
            repository_guide_query.update()
        else:
            RepositoryGuideModel.create(format=repository_format, content=repository_guide)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, language=self.ops_language()))


class NexusComponentView(BaseView):
    def get(self, request):
        """
            获取制品库的组件
        :param request:
        :return:
        """
        kwargs = request.GET.dict()
        continuationToken = kwargs.get("continuationToken")
        repository_id = kwargs.get("repository_id")
        id = kwargs.get("id")
        if (not repository_id) and (not id):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if id:
            res = nexus_api.get_component(id=id)
        elif repository_id:
            res = nexus_api.get_component_list(repository_id=repository_id, continuationToken=continuationToken)
        else:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_GET_SUCCESS, [], language=self.ops_language()))
        if res.get("status"):
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res.get("data"), language=self.ops_language()))
        else:
            return JsonResponse(error(*res.get("message"), language=self.ops_language()))

    def post(self, request):
        """
            上传制品
        :param request:
        :return:
        """
        kwargs = request.POST.dict()
        repository_id = kwargs.get("repository_id")
        file = request.FILES.get("file")

        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))
        repo_query = RepositoryModel.fetch_one(name=repository_id)

        # 判断权限
        if user_query.role != 1:
            status = repo_query.is_auth_upload(user_query)
            if not status:
                return JsonResponse(error(ErrorStatusCode.USER_NOT_POWER, language=self.ops_language()))

        nexus_api = NexusApi(**tool_query.link_tool_dict())
        get_repository_result = nexus_api.get_repository()
        format = None
        if get_repository_result.get("status"):
            repository_list = get_repository_result.get("data")
            for repository in repository_list:
                if repository.get("name") == repository_id:
                    format = repository.get("format")
        if not format:
            return JsonResponse(error(ErrorStatusCode.REPOSITORY_NOT_EXISTED, language=self.ops_language()))
        if format not in constant.REPOSITORY_FORMAT:
            return JsonResponse(error(ErrorStatusCode.REPOSITORY_ASSET_NOT_UPLOAD, language=self.ops_language()))

        res = nexus_api.update_component(file, format, **kwargs)
        if res.get("status"):
            if repo_query:
                if repo_query.active_time:
                    repo_query.update(active_time=datetime.datetime.now())
                else:
                    repo_query.update(active_time=datetime.datetime.now())
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, res.get("data"), language=self.ops_language()))
        else:
            return JsonResponse(error(*res.get("message"), language=self.ops_language()))

    def delete(self, request):
        """
            删除制品
        :param request:
        :return:
        """
        data = json.loads(request.body)
        repository_id = data.get("repository_id")
        component_id = data.get("component_id")
        code = data.get("code", None)
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        nexus_api = NexusApi(**tool_query.link_tool_dict())
        status, message = self._is_delete(request, nexus_api, repository_id, component_id, code)
        if status:
            res = nexus_api.delete_component(component_id)
            if res.get("status"):
                repo_query = RepositoryModel.fetch_one(name=repository_id)
                if repo_query:
                    if repo_query.active_time:
                        repo_query.update(active_time=datetime.datetime.now())
                    else:
                        repo_query.update(active_time=datetime.datetime.now())
                return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS, res.get("data"), language=self.ops_language()))
            else:
                return JsonResponse(error(*res.get("message"), language=self.ops_language()))
        else:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR,custom_message=str(message), language=self.ops_language()))

    def _is_delete(self, request, nexus_api, repository_id, component_id, code):
        repository = RepositoryModel.fetch_one(name=repository_id)
        if not repository:
            return False, "制品库不存在"
        res = nexus_api.get_component(component_id)
        if not res.get("status"):
            return False, res.get("message", ["", "Delete Error"])[1]
        if repository.is_app:
            app_query = ApplicationModel.fetch_one(code=code)
            if not app_query:
                return False, "应用不存在"
            user_query = GetUserInfo().get_user_info(request)
            if not user_query:
                return False, "用户不存在"
            # if user_query.role not in [1]:
            #     if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=app_query):
            #         return False, "没有删除权限"

            # 判断权限
            if user_query.role != 1:
                status = repository.is_auth_file_delete(user_query)
                if not status:
                    return False, "没有操作权限"
        return True, "Can Delete"


class NexusComponentTreeView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        repository_id = kwargs.get("repository_id")
        id = kwargs.get("id")
        if (not repository_id) and (not id):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if nexus_api.status() is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_sync_component(nexus_api, repository_id)

        queryset = RawComponentGroupModel.fetch_all(parent=None, repository_id=repository_id)
        new_group_list = [query.to_parent_dict(repository_id) for query in queryset]
        component_queryset = RawComponentModel.fetch_all(group=None)
        new_group_list.extend([component_query.data_dict for component_query in component_queryset])
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, new_group_list, language=self.ops_language()))


class NexusComponentV2View(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        group_code = kwargs.get("group_code")
        repository_id = kwargs.get("repository_id")
        search_type, search_data = kwargs.pop("search_type", None), kwargs.pop("search_data", None)
        try:
            current, pageSize = int(kwargs.pop("current")), int(kwargs.pop("pageSize"))
        except Exception:
            current, pageSize = 1, 10
        if not repository_id:
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if nexus_api.status() is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_sync_component(nexus_api, repository_id)
        dic = {"repository_id": repository_id}
        try:
            group_code = int(group_code)
            group_query = RawComponentGroupModel.fetch_one(repository_id=repository_id, code=group_code)
            if not group_query:
                children_group_queryset = []
            else:
                children_group_queryset = group_query.get_children_group_queryset()
            dic["group__in"] = children_group_queryset
        except Exception:
            if group_code == "all":
                pass
            else:
                dic["group"] = None
        if search_type and search_data:
            dic[search_type + "__contains"] = search_data
        current_page, total = RawComponentModel.pagination(current,pageSize, **dic)
        end_data = [i.to_dict() for i in current_page]
        res_data = {
            "current": current,
            "pageSize": pageSize,
            "total": total,
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res_data, language=self.ops_language()))


class NexusComponentTreeV2View(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        repository_id = kwargs.get("repository_id")
        if not repository_id:
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if nexus_api.status() is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_sync_component(nexus_api, repository_id)
        queryset = RawComponentGroupModel.fetch_all(parent=None, repository_id=repository_id)
        new_group_list = [query.to_parent_v2_dict(repository_id) for query in queryset]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, new_group_list, language=self.ops_language()))


class SearchComponentView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        code = kwargs.pop("code", None)
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.search_component(**kwargs)
        print("res", res)
        if res.get("status"):
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res.get("data"), language=self.ops_language()))
        return JsonResponse(error(*res.get("message"), language=self.ops_language()))


class NexusAssetView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        repository_id = kwargs.get("repository_id")
        id = kwargs.get("id")
        if (not repository_id) and (not id):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        print(tool_query.to_dict())
        print()
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if id:
            res = nexus_api.get_assets(id=id)
        # elif repository_id:
        #     res = nexus_api.get_component_list(repository_id=repository_id)
        else:
            return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, language=self.ops_language()))
        if res.get("status"):
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res.get("data"), language=self.ops_language()))
        else:
            return JsonResponse(error(*res.get("message"), language=self.ops_language()))


class ApplicationRepoView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        application_code = kwargs.get("application_code")
        repo_code = kwargs.get("repo_code")
        if application_code:
            application = ApplicationModel.fetch_one(code=application_code)
            dic = {"application": application}
        elif repo_code:
            repo = RepositoryModel.fetch_one(code=repo_code)
            dic = {"repo": repo}
        else:
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        app_repo_queryset = ApplicationRepoModel.fetch_all(**dic)
        print(app_repo_queryset)
        app_repo_list = [app_repo.to_dict() for app_repo in app_repo_queryset]

        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, app_repo_list, language=self.ops_language()))

    def post(self, request):
        kwargs = json.loads(request.body)
        application_code = kwargs.get("application_code")
        repo_code = kwargs.get("repo_code")
        if not all([application_code, repo_code]):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        application_query = ApplicationModel.fetch_one(code=application_code)
        repo_query = RepositoryModel.fetch_one(code=repo_code)
        if not application_query: return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        if not repo_query: return JsonResponse(error(ErrorStatusCode.REPOSITORY_NOT_EXISTED, language=self.ops_language()))
        app_repo_query = ApplicationRepoModel.fetch_one(application=application_query, repo=repo_query)
        if not app_repo_query:
            app_repo_query = ApplicationRepoModel.create(application=application_query, repo=repo_query)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, app_repo_query.to_dict(), language=self.ops_language()))
        return JsonResponse(error(ErrorStatusCode.RECORD_HAS_EXISTED, language=self.ops_language()))

    def delete(self, request):
        kwargs = json.loads(request.body)
        app_repo_code = kwargs.get("app_repo_code")
        app_repo_query = ApplicationRepoModel.fetch_one(code=app_repo_code)
        if not app_repo_query:
            return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, language=self.ops_language()))
        app_repo_query.delete()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS, app_repo_query.to_dict(), language=self.ops_language()))


class ToolView(BaseView):
    @admin_auth
    def get(self, request, **kwargs):
        tool_queryset = ToolsModel.fetch_all(tool_type="repository")
        status = flash_all_tool_status(request, tool_queryset)
        end_data = []
        if tool_queryset:
            for i in tool_queryset:
                end_data.append(i.to_dict())
        data = {
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))

    @admin_auth
    def post(self, request, **kwargs):
        try:
            post_data = json.loads(request.body)
            tool_type = post_data.get("tool_type")
            tool_dict = {
                "tool_name": post_data.get("tool_name"),
                "tool_type": post_data.get("tool_type"),
                "api_addr": post_data.get("api_addr"),
                "username": post_data.get("username"),
                "api_token": post_data.get("api_token"),
                "description": post_data.get("description")
            }
            api_dict = {
                "url": post_data.get("api_addr"),
                "username": post_data.get("username"),
                "password": post_data.get("api_token"),
            }
            if not all([tool_dict["tool_name"],tool_dict["api_token"], tool_dict["tool_type"], tool_dict["api_addr"]]):
                return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
            # 工具类唯一
            tool_obj_type = ToolsModel.fetch_one(tool_type=tool_dict.get("tool_type"))
            if tool_obj_type:
                return JsonResponse(error(ErrorStatusCode.TOOL_HAS_EXISTED, language=self.ops_language()))
            # 工具名称唯一
            tool_obj_name = ToolsModel.fetch_one(tool_type=tool_type, tool_name=tool_dict.get("tool_name"))
            if tool_obj_name:
                return JsonResponse(error(ErrorStatusCode.TOOL_NAME_HAS_EXISTED, language=self.ops_language()))
            # Nexus
            if tool_dict["tool_type"] == "repository":
                status = NexusApi(request, **api_dict).status()
            else:
                raise Exception("tool type error")
            if status is True:
                tool_dict["link_status"] = constant.TOOL_LINK_STATUS_SUCCESS
                tool_obj = ToolsModel.create(**tool_dict)
                return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, tool_obj.to_dict(), language=self.ops_language()))
            else:
                print("状态连接失败", status)
                return JsonResponse(error(*status, language=self.ops_language()))
        except Exception as e:
            print(e)
            return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, str(e), language=self.ops_language()))

    @admin_auth
    def put(self, request, **kwargs):
        post_data = json.loads(request.body)
        code = post_data.get("code")
        try:
            if code:
                tool_dict = dict()
                tool_type = post_data.get("tool_type")
                if post_data.get("tool_name"): tool_dict["tool_name"] = post_data.get("tool_name")
                if post_data.get("tool_type"): tool_dict["tool_type"] = post_data.get("tool_type")
                if post_data.get("api_addr"): tool_dict["api_addr"] = post_data.get("api_addr")
                if post_data.get("username"): tool_dict["username"] = post_data.get("username")
                if post_data.get("api_token"): tool_dict["api_token"] = post_data.get("api_token")
                tool_dict["description"] = post_data.get("description")

                # 参数是否完整
                if not all([tool_dict["tool_name"], tool_dict["tool_type"], tool_dict["api_addr"]]):
                    return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))

                # 数据是否存在
                tool_obj_id = ToolsModel.fetch_one(code=code)
                if not tool_obj_id:
                    return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, language=self.ops_language()))
                if post_data.get("api_token") == "******":
                    post_data["api_token"] = tool_obj_id.api_token
                    tool_dict["api_token"] = tool_obj_id.api_token

                # 工具类唯一
                tool_name_unique = ToolsModel.check_field_unique(code, "tool_type", tool_dict.get("tool_type"))
                if not tool_name_unique:
                    return JsonResponse(error(ErrorStatusCode.TOOL_NAME_HAS_EXISTED, language=self.ops_language()))

                # 工具名称唯一
                tool_name_query = ToolsModel.fetch_one(tool_type=tool_type, tool_name=tool_dict.get("tool_name"))
                if tool_name_query:
                    if tool_name_query != tool_obj_id:
                        return JsonResponse(error(ErrorStatusCode.TOOL_NAME_HAS_EXISTED, language=self.ops_language()))
                # tool_name_unique = ToolsModel.check_field_unique(code, "tool_name", tool_dict.get("tool_name"))
                # if not tool_name_unique:
                #     return JsonResponse(error(ErrorStatusCode.TOOL_NAME_HAS_EXISTED, language=self.ops_language()))

                api_dict = {
                    "url": post_data.get("api_addr"),
                    "username": post_data.get("username"),
                    "password": post_data.get("api_token"),
                }
                # Nexus
                if tool_dict["tool_type"] == "repository":
                    status = NexusApi(request, **api_dict).status()
                else:
                    raise Exception("tool type error")
                if status == True:
                    tool_dict["link_status"] = constant.TOOL_LINK_STATUS_SUCCESS
                    tool_obj = tool_obj_id.update(**tool_dict)
                    return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, tool_obj.to_dict(), language=self.ops_language()))
                else:
                    return JsonResponse(error(*status, language=self.ops_language()))
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        except mongoengine.errors.NotUniqueError as e:
            print("mongoengine.errors.NotUniqueError", e)
            return JsonResponse(error(ErrorStatusCode.TOOL_NAME_HAS_EXISTED, language=self.ops_language()))
        except Exception as e:
            print(e)
            return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, str(e), language=self.ops_language()))

    @admin_auth
    def delete(self, request, **kwargs):
        delete_data = json.loads(request.body)
        code = delete_data.get("code")
        print("delete_data", delete_data)
        try:
            if code:
                tool_obj = ToolsModel.fetch_one(code=code)
                if not tool_obj:
                    return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, language=self.ops_language()))

                if tool_obj.tool_type == "repository":
                    app_repo_queryset = ApplicationRepoModel.fetch_all()
                    if app_repo_queryset:
                        return JsonResponse(error(ErrorStatusCode.INST_HAS_NEXUS, language=self.ops_language()))
                tool_obj.delete()
                return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS, language=self.ops_language()))
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        except Exception as e:
            print(e)
            return JsonResponse(error(ErrorStatusCode.SERVER_ERROR, e, language=self.ops_language()))

    # def create_jenkins_folder(self, jenkins_api):
    #     """当增加或修改Jenkins工具时，主动创建以应用唯一标识为名的Jenkins目录，且创建本地关联关系"""
    #     app_queryset = ApplicationModel.fetch_all()
    #     for app in app_queryset:
    #         dt = {"application": app}
    #         app_name = app.get_model_code_name()
    #         if not ApplicationJenkinsModel.fetch_one(**dt):
    #             ApplicationJenkinsModel.create(jenkins_view_name=app_name, **dt)
    #         jenkins_api.create_folder(app_name)


# 刷新全部工具状态
class ToolStatusView(BaseView):
    def get(self, request, **kwargs):
        tool_code = request.GET.get("tool_code")
        if tool_code:
            tool_queryset = ToolsModel.fetch_all(code=tool_code)
        else:
            tool_queryset = ToolsModel.fetch_all()
        status = flash_all_tool_status(request, tool_queryset)
        return JsonResponse(success(SuccessStatusCode.REFRESH_STATUS_SUCCESS, "成功：{}，失败：{}".format(*status), language=self.ops_language()))


class ToolTestView(BaseView):
    def post(self, request, **kwargs):
        data = json.loads(request.body)
        tool_url = data.get("tool_url")
        tool_username = data.get("tool_username")
        tool_password = data.get("tool_password")
        code = data.get("code")

        if not all([tool_url, tool_username, tool_password]):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))

        try:
            if code and tool_password == "******":
                nexus_query = ToolsModel.fetch_one(code=code)
                if not nexus_query:
                    return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, custom_message="nexus工具不存在！"))
                tool_password = nexus_query.api_token
            nexus_api = NexusApi(url=tool_url, username=tool_username, password=tool_password)
            status = nexus_api.status()

            if status == True:
                end_data = {
                    "data": "连接测试成功",
                    "status": 1
                }
                return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, end_data, language=self.ops_language()))
            else:
                end_data = {
                    "data": "连接测试失败",
                    "status": 2
                }
                return JsonResponse(error(*status, language=self.ops_language()))
                # return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, end_data, language=self.ops_language()))
        except Exception as e:
            return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, errors=str(e), language=self.ops_language()))


class HarborProjectView(BaseView):
    def get(self, request):
        api = HarborApi()
        status, res = api.get_project_list()
        if status:
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res))
        return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, custom_message=res))


class HarborRepositoryView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        page = int(kwargs.get("current", 1))
        per_page = int(kwargs.get("pageSize", 10))
        project_name = kwargs.get("project_name")
        api = HarborApi()
        status, res = api.get_repository_list(project_name, page, per_page)
        total_status, total = api.project_harbor_total(project_name)
        if status:
            end_data = {
                "current": page,
                "pageSize": per_page,
                "total": total if total_status else len(res),
                "data": res
            }
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
        return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED, custom_message=res))


class BusinessTreeView(View):
    def get(self, request):
        return BusinessTree(request).get_business_application_list(request)


class RepositoryTagsView(View):
    def put(self, request):
        return RepositoryTags(request).tags_repository(request)
