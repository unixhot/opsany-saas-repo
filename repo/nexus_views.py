import datetime
import json
import os
import subprocess

from django.conf import settings
from django.http import JsonResponse
import requests

from component.base_views import BaseView
from repo.decorator import admin_auth
from repo.models import ApplicationModel, ApplicationUserRoleModel, RepositoryTagsModel
from repo.utils.component import GetUserInfo
from component.status_code import *
from repo.models import ToolsModel, RepositoryModel, ApplicationRepoModel, RepositoryGuideModel, RawComponentModel, \
    RawComponentGroupModel
from repo.utils import constant
from repo.utils.constant import REPOSITORY_TYPE_LIST
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


# 获取制品库
class NexusRepositoryGetView(BaseView):
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
            app_repo_queryset = list(set(ApplicationRepoModel.fetch_all(application=app_query, repo__in=repo_id_list, **inner_idc)))
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


# 新建制品库
class NexusRepositoryPostView(BaseView):
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
        inner = kwargs.get("inner")
        describe = kwargs.get("describe", "")
        repository_type = kwargs.get("repository_type")
        parameters = kwargs.get("parameters", {})

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
        print(tool_query.to_dict())
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.create_repository(repository_id, repository_type, parameters)
        if res.get("status"):
            # 本地保存
            dic = {"name": repository_id, "describe": describe, "attributes": parameters, "format": repository_type}
            print("dic", dic)
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


# 删除制品库
class NexusRepositoryDeleteView(BaseView):
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
                return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
            if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
                return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
            print(tool_query.to_dict())
            repo_query = RepositoryModel.fetch_one(name=repository_id)

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


# 获取制品库信息
class RepoGetView(BaseView):
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
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        repository = RepositoryModel.fetch_one(name=repository_id)
        data = repository.to_dict() if repository else []
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))


# 修改制品库权限
class RepoPutView(BaseView):
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
        code = kwargs.get("code")
        inner = kwargs.get("inner")
        describe = kwargs.get("describe", "")

        dic = {
            "describe": describe
        }

        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        repo = RepositoryModel.fetch_one(name=repository_id)
        if not repo:
            return JsonResponse(error(ErrorStatusCode.REPOSITORY_NOT_EXISTED, language=self.ops_language()))
        app_repo = ApplicationRepoModel.fetch_one(application=app_query, repo=repo)
        if inner:
            dic["is_app"] = True
            if not app_repo:
                ApplicationRepoModel.create(application=app_query, repo=repo)
        else:
            if app_repo: app_repo.delete()
            repo.update(is_app=False)
        repo.update(**dic)

        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, language=self.ops_language()))


# 获取制品库使用指引
class RepositoryGuideGetView(BaseView):
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
        if repository_guide:
            data = repository_guide.to_dict()
            # print("RepositoryGuideView-get", repository.url, repository.name)
            data["content"] = data.get("content", "{url}").format(url=repository.url, id=repository.name)
        else:
            data = {"format": repository_format, "content": "#### 无"}
        # print("data345", data)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))


# 更新制品库使用指引
class RepositoryGuidePostView(BaseView):
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


# 获取制品库组件
class NexusComponentGetView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        continuationToken = kwargs.get("continuationToken")
        repository_id = kwargs.get("repository_id")
        id = kwargs.get("id")
        if (not repository_id) and (not id):
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
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


# 上传制品
class NexusComponentPostView(BaseView):
    def post(self, request):
        """
            上传制品
        :param request:
        :return:
        """
        kwargs = request.POST.dict()
        # print("kwargskwargs", kwargs)
        repository_id = kwargs.get("repository_id")
        # print("repository_id", repository_id)
        file = request.FILES.get("file")

        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))

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
            repo_query = RepositoryModel.fetch_one(name=repository_id)
            if repo_query:
                if repo_query.active_time:
                    repo_query.update(active_time=datetime.datetime.now())
                else:
                    repo_query.update(active_time=datetime.datetime.now())
            return JsonResponse(
                success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, res.get("data"), language=self.ops_language()))
        else:
            return JsonResponse(error(*res.get("message"), language=self.ops_language()))


# 删除制品
class NexusComponentDeleteView(BaseView):
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
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))

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
                return JsonResponse(
                    success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS, res.get("data"), language=self.ops_language()))
            else:
                return JsonResponse(error(*res.get("message"), language=self.ops_language()))
        else:
            return JsonResponse(
                error(ErrorStatusCode.CUSTOM_ERROR, custom_message=str(message), language=self.ops_language()))

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
            if user_query.role not in [1]:
                if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=app_query):
                    return False, "没有删除权限"
        return True, "Can Delete"


# 制品库资源
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
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
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


# 组件搜索
class SearchComponentView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        code = kwargs.pop("code", None)
        repository = kwargs.get("repository")
        format = kwargs.get("format")
        name = kwargs.get("name")
        continuationToken = kwargs.get("continuationToken")
        app_query = ApplicationModel.fetch_one(code=code)
        if not app_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.search_component(repository, format, name, continuationToken)
        print("res", res)
        if res.get("status"):
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res.get("data"), language=self.ops_language()))
        return JsonResponse(error(*res.get("message"), language=self.ops_language()))


# 获取资源(根据组)
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
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
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


# 获取版本资源(树结构-带资源)
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
            return JsonResponse(error(ErrorStatusCode.JENKINS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.JENKINS_STATUS_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        if nexus_api.status() is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))
        nexus_sync_component(nexus_api, repository_id)

        queryset = RawComponentGroupModel.fetch_all(parent=None, repository_id=repository_id)
        new_group_list = [query.to_parent_dict(repository_id) for query in queryset]
        component_queryset = RawComponentModel.fetch_all(group=None)
        new_group_list.extend([component_query.data_dict for component_query in component_queryset])
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, new_group_list, language=self.ops_language()))


# 获取版本资源(树结构不带资源)
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


# 克隆操作
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


# 制品库下载
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


# 获取制品库资源统计数量
class GetHomePageView(BaseView):
    def get(self, request):
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED_V2, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, {}, language=self.ops_language()))

        kwargs = request.GET.dict()
        code = kwargs.get("code")

        application_query = ApplicationModel.fetch_one(code=code)
        if not application_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

        repo_filter_dic = {}
        if user_query.role != 1:
            status = user_query.is_app_auth(application_query)
            if not status:
                return JsonResponse(error(ErrorStatusCode.USER_NOT_POWER, language=self.ops_language()))

            _, _, repo_read_code_list = user_query.get_code_list(application_query, id_type="repo")
            repo_filter_dic["code__in"] = repo_read_code_list[0]

        repo_queryset = RepositoryModel.fetch_all(**repo_filter_dic)

        # 制品仓库数量
        repo_public_count = RepositoryModel.counter(is_app=False)
        repo_inner_count = 0

        # raw仓库数量
        repo_public_raw_count = RepositoryModel.counter(is_app=False, format="raw")
        repo_inner_raw_count = 0

        # docker仓库数量
        repo_public_docker_count = RepositoryModel.counter(is_app=False, format="docker")
        repo_inner_docker_count = 0

        # maven仓库数量
        repo_public_maven_count = RepositoryModel.counter(is_app=False, format="maven2")
        repo_inner_maven_count = 0

        # pypi仓库数量
        repo_public_pypi_count = RepositoryModel.counter(is_app=False, format="pypi")
        repo_inner_pypi_count = 0

        # 与当前应用关联的制品库
        application_repository_queryset = ApplicationRepoModel.fetch_all(application=application_query, repo__in=repo_queryset)

        for app_repo in application_repository_queryset:
            # 应用内仓库
            if app_repo.application == application_query:
                repo_inner_count += 1
            if app_repo.repo.format == "raw":
                repo_inner_raw_count += 1
            if app_repo.repo.format == "docker":
                repo_inner_docker_count += 1
            if app_repo.repo.format == "maven2":
                repo_inner_maven_count += 1
            if app_repo.repo.format == "pypi":
                repo_inner_pypi_count += 1

        repo_all_count = repo_public_count + repo_inner_count
        repo_all_raw_count = repo_public_raw_count + repo_inner_raw_count
        repo_all_docker_count = repo_public_docker_count + repo_inner_docker_count
        repo_all_maven_count = repo_public_maven_count + repo_inner_maven_count
        repo_all_pypi_count = repo_public_pypi_count + repo_inner_pypi_count

        end_dic = {
            "repo_count": {
                "repo_all_count": repo_all_count,
                "repo_public_count": repo_public_count,
                "repo_inner_count": repo_inner_count
            },
            "repo_raw_count": {
                "repo_all_raw_count": repo_all_raw_count,
                "repo_public_raw_count": repo_public_raw_count,
                "repo_inner_raw_count": repo_inner_raw_count
            },
            "repo_docker_count": {
                "repo_all_docker_count": repo_all_docker_count,
                "repo_public_docker_count": repo_public_docker_count,
                "repo_inner_docker_count": repo_inner_docker_count
            },
            "repo_maven_count": {
                "repo_all_maven_count": repo_all_maven_count,
                "repo_public_maven_count": repo_public_maven_count,
                "repo_inner_maven_count": repo_inner_maven_count
            },
            "repo_pypi_count": {
                "repo_all_pypi_count": repo_all_pypi_count,
                "repo_public_pypi_count": repo_public_pypi_count,
                "repo_inner_pypi_count": repo_inner_pypi_count
            }
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_dic, language=self.ops_language()))


# 获取所有的制品库（包括公共）
class GetRepositoryPaginationView(BaseView):
    def get(self, request):
        # 校验工具
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED_V2, language=self.ops_language()))
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
        search_type = kwargs.get("search_type", None)
        search_data = kwargs.get("search_data", None)

        try:
            page = int(kwargs.get("current"))
            per_page = int(kwargs.get("pageSize"))
        except:
            page = 1
            per_page = 20

        code = kwargs.get("code", None)
        application_query = ApplicationModel.fetch_one(code=code)
        if not application_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))

        if user_query.role not in [1]:
            # if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=application_query):
            status = user_query.is_app_auth(application_query)
            if not status:
                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, {}, language=self.ops_language()))

        # 与当前应用没有关联的制品库code
        application_not_repo_queryset = ApplicationRepoModel.fetch_all(application__ne=application_query)
        application_not_repo_list = [i.repo.code for i in application_not_repo_queryset]

        # 所有的制品库code
        repository_model = RepositoryModel.fetch_all()
        repository_code_list = [repo.code for repo in repository_model]

        # 公共制品库和当前应用下的制品库code
        repo_code_list = [code for code in repository_code_list if code not in application_not_repo_list]

        filter_dict = {"code__in": repo_code_list}
        if search_type and search_data:
            filter_dict[search_type + "__icontains"] = search_data

        repo_read_code_list = []
        if user_query.role != 1:
            _, _, repo_read_code_list = user_query.get_code_list(application_query, id_type="repo")
            filter_dict["code__in"] = repo_read_code_list[0]

        # 公共制品库和当前应用下的制品库
        repo_queryset, total = RepositoryModel.pagination(page, per_page, **filter_dict)

        repo_list = [repo.to_devops_dict(user_query, repo_read_code_list) for repo in repo_queryset]

        end_data = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "data": repo_list
        }

        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data, language=self.ops_language()))
