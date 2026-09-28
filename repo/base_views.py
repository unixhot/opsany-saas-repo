import json

from django.http import JsonResponse

from component.base_views import BaseView
from component.libs import GetUserInfo
from component.status_code import success, SuccessStatusCode, error, ErrorStatusCode
from repo import get_user_query_from_cookie
from repo.models import UserInfo, RepositoryModel, ToolsModel, ApplicationRepoModel, ApplicationModel
from component.esb_api import EsbApi
from repo.utils import constant
from repo.utils.nexus_api import NexusApi
from repo.utils.sync_data import nexus_sync_data


class DeployMenuStrategyCtrl(BaseView):
    # @user_sync
    def get(self, request):
        """ 获取当前平台使用者的菜单列表 """
        token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        esb_obj = EsbApi(token, language=language)
        res_data = esb_obj.get_user_menu()  # 调用ESB接口获取到当前用户的在资源平台的菜单列表
        return JsonResponse(success(SuccessStatusCode.MENU_GET_SUCCESS, res_data[0] if res_data else {}, language=language))


class GuideCtrl(BaseView):
    def get(self, request):
        """ 获取当前平台使用指南"""
        token = request.COOKIES.get("bk_token")
        platform_code = request.GET.get("platform_code", "")
        if not platform_code:
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE, language=self.ops_language()))
        esb_obj = EsbApi(token)
        res_data = esb_obj.guide(platform_code)
        return JsonResponse(res_data, safe=False)


# 获取当前用户信息
class GetUserInfoCtrl(BaseView):

    # @user_sync
    def get(self, request):
        """
        获取当前用户信息
        """
        token = request.COOKIES.get("bk_token")
        user_query = get_user_query_from_cookie(request)
        if not user_query:
            UpdateDirectorView()._update_director(request)
            user_query = get_user_query_from_cookie(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.NOT_HAVE_USER_INFO, language=self.ops_language()))
        data = user_query.to_user_info_dict()
        language_theme_config = EsbApi(token, language=self.ops_language()).get_language_theme_config(user_query.username)
        data.update(language_theme_config)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=self.ops_language()))


# 获取用户收藏信息
class GetNavCollectionView(BaseView):
    def get(self, request):
        token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        end_data = EsbApi(token, language).get_nav_and_collection()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data, language=language))


# 用户收藏信息
class CollectionNavView(BaseView):
    def post(self, request):
        token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        data = json.loads(request.body)
        nav_id = data.get("nav_id")
        end_data = EsbApi(token, language).collection_nav(nav_id)
        if not isinstance(end_data, dict):
            return JsonResponse(error(ErrorStatusCode.OPERATION_ERROR, language=language))
        successcode = end_data.pop("api_code")
        res_dict = {
            "code": 200,
            "successcode": successcode,
            "message": end_data.get("message"),
            "data": end_data.get("data")
        }
        return JsonResponse(res_dict)


# 获取用户站内信
class GetUserMessageView(BaseView):
    def get(self, request):
        kwargs = request.GET.dict()
        page = int(kwargs.pop("current", 1))
        per_page = int(kwargs.pop("pageSize", 10))
        token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        data = EsbApi(token, language).get_user_message_info(page, per_page)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data, language=language))


# 全部已读站内信
class ReadAllMessageView(BaseView):
    def get(self, request):
        bk_token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        EsbApi(bk_token, language).read_all_message()
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, language=language))


# 底部版权
class CopyrightConfigView(BaseView):
    def get(self, request):
        """
        底部版权信息
        :param request:
        :return:
        {
            "code": 200,
            "successcode": 20005,
            "message": "相关信息信息获取成功",
            "data": {
                "content": "Copyright © 2019-2021 OpsAny. All Rights Reserved",
                "id": 1
            }
        }
        """
        token = request.COOKIES.get("bk_token")
        language = self.ops_language()
        end_data = EsbApi(token, language).get_copyright_config()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data, language=language))


# 概览页制品库统计
class HomePageView(BaseView):
    def get(self, request):
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, {}, language=self.ops_language()))

        repo_filter_dic = {}
        if user_query.role != 1:
            _, _, repo_read_code_list = user_query.get_code_list(id_type="repo")
            repo_filter_dic["code__in"] = repo_read_code_list[0]

            # 制品库总数
            repo_public_count = RepositoryModel.counter(is_app=False)
            repo_inner_count = RepositoryModel.counter(**repo_filter_dic)
            repo_all_count = repo_public_count + repo_inner_count

            # Raw仓库
            repo_public_raw_count = RepositoryModel.counter(is_app=False, format="raw")
            repo_inner_raw_count = RepositoryModel.counter(**repo_filter_dic, format="raw")
            repo_all_raw_count = repo_public_raw_count + repo_inner_raw_count

            # Docker仓库
            repo_public_docker_count = RepositoryModel.counter(is_app=False, format="docker")
            repo_inner_docker_count = RepositoryModel.counter(**repo_filter_dic, format="docker")
            repo_all_docker_count = repo_public_docker_count + repo_inner_docker_count

            # Maven仓库
            repo_public_maven_count = RepositoryModel.counter(is_app=False, format="maven2")
            repo_inner_maven_count = RepositoryModel.counter(**repo_filter_dic, format="maven2")
            repo_all_maven_count = repo_public_maven_count + repo_inner_maven_count

            # PyPi仓库
            repo_public_pypi_count = RepositoryModel.counter(is_app=False, format="pypi")
            repo_inner_pypi_count = RepositoryModel.counter(**repo_filter_dic, format="pypi")
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

        # 制品库总数
        repo_public_count, repo_inner_count = 0, 0
        repo_all_count = RepositoryModel.counter()
        repo_query_set = RepositoryModel.fetch_all()
        for i in repo_query_set:
            if i.is_app:
                repo_inner_count += 1
            else:
                repo_public_count += 1

        # Raw仓库
        repo_public_raw_count, repo_inner_raw_count = 0, 0
        repo_all_raw_count = RepositoryModel.counter(format="raw")
        repo_query_raw_set = RepositoryModel.fetch_all(format="raw")
        for i in repo_query_raw_set:
            if i.is_app:
                repo_inner_raw_count += 1
            else:
                repo_public_raw_count += 1

        # Docker仓库
        repo_public_docker_count, repo_inner_docker_count = 0, 0
        repo_all_docker_count = RepositoryModel.counter(format="docker")
        repo_query_docker_set = RepositoryModel.fetch_all(format="docker")
        for i in repo_query_docker_set:
            if i.is_app:
                repo_inner_docker_count += 1
            else:
                repo_public_docker_count += 1

        # Maven仓库
        repo_public_maven_count, repo_inner_maven_count = 0, 0
        repo_all_maven_count = RepositoryModel.counter(format="maven2")
        repo_maven_query_set = RepositoryModel.fetch_all(format="maven2")
        for i in repo_maven_query_set:
            if i.is_app:
                repo_inner_maven_count += 1
            else:
                repo_public_maven_count += 1

        # PyPi仓库
        repo_public_pypi_count, repo_inner_pypi_count = 0, 0
        repo_all_pypi_count = RepositoryModel.counter(format="pypi")
        repo_pypi_query_set = RepositoryModel.fetch_all(format="pypi")
        for i in repo_pypi_query_set:
            if i.is_app:
                repo_inner_pypi_count += 1
            else:
                repo_public_pypi_count += 1

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


# 概览页最近活跃
class HomePageLeftView(BaseView):
    def get(self, request):
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))

        repo_filter_dic = {}
        if user_query.role != 1:
            _, _, repo_read_code_list = user_query.get_code_list(id_type="repo")
            repo_filter_dic["code__in"] = repo_read_code_list[0]

        repo_query_set = RepositoryModel.fetch_all(**repo_filter_dic).order_by("-active_time")[:6]
        repo_list = [repo.to_tags_dict(user_query) for repo in repo_query_set if repo.active_time is not None]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, repo_list, language=self.ops_language()))


# 概览页数量排名
class HomePageVolumeView(BaseView):
    def get(self, request):
        tool_query = ToolsModel.fetch_one(tool_type="repository")
        if not tool_query:
            return JsonResponse(error(ErrorStatusCode.NEXUS_NOT_EXISTED, language=self.ops_language()))
        if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
            return JsonResponse(error(ErrorStatusCode.NEXUS_SERVER_ERROR, language=self.ops_language()))
        nexus_api = NexusApi(**tool_query.link_tool_dict())
        res = nexus_api.status()
        if res is not True:
            return JsonResponse(error(ErrorStatusCode.NEXUS_STATUS_ERROR, language=self.ops_language()))

        user_query = GetUserInfo().get_user_info(request)
        if not user_query:
            return JsonResponse(error(ErrorStatusCode.USER_NOT_EXISTED, language=self.ops_language()))

        repo_filter_dic = {}
        if user_query.role != 1:
            _, _, repo_read_code_list = user_query.get_code_list(id_type="repo")
            repo_filter_dic["code__in"] = repo_read_code_list[0]

        repositories = RepositoryModel.fetch_all(**repo_filter_dic)

        result = []
        sorted_result = []

        for repository in repositories:
            # 获取制品库名称
            repository_name = repository.name
            # 获取制品库类型
            repository_format = repository.format
            component_count = nexus_api.get_component_count(repository_name)
            # 获取所属应用的名称
            application = ApplicationRepoModel.fetch_one(repo=repository)
            application_name = application.application.pk_value if application else ""
            application_unique = application.application.data.get("APPLICATION_name") if application else ""
            application_id = application.application.code if application else ""
            result.append({
                "repository": repository_name,
                "type": repository_format,
                "count": component_count,
                "application": application_name,
                "app_id": application_id,
                "app_unique": application_unique
            })
            # 排序
            sorted_result = sorted(result, key=lambda x: x["count"], reverse=True)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, sorted_result, language=self.ops_language()))


class UpdateDirectorView(BaseView):
    def get(self, request):
        # all_user_list = esb.get_all_users()
        token = request.COOKIES.get("bk_token")
        esb = EsbApi(token=token)
        all_user_list = esb.get_user_group_sync()
        user_list = all_user_list.get("user_list", []) or []
        if not user_list:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR,custom_message="没有拉取到用户信息"))
        temp_user_list = []
        for each_user in user_list:
            used_field = {}
            is_activate = each_user.get("is_activate")
            used_field["phone"] = each_user.get("phone")
            used_field["username"] = each_user.get("username")
            used_field["email"] = each_user.get("email")
            used_field["ch_name"] = each_user.get("chname")
            used_field["role"] = each_user.get("bk_role")
            used_field["is_activate"] = True if is_activate else False
            # if not UserInfo.objects.filter(username=each_user["bk_username"]).count():
            obj_user = UserInfo.fetch_one(username=each_user["username"])
            if not obj_user:
                obj_user = UserInfo.objects.create(**used_field)
            else:
                obj_user.update(**used_field)
                # obj_user = UserInfo.objects.select_for_update().filter(username=each_user["bk_username"])
                # with transaction.atomic():

            temp_user_list.append(used_field["username"])
        local_all_users = UserInfo.objects.all()
        deleted_user_list = []
        for each in local_all_users:
            if each.username not in temp_user_list:
                deleted_user_list.append(each.username)
        UserInfo.objects.filter(username__in=deleted_user_list).update(is_activate=False)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS))
