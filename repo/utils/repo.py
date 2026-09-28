import collections
import json
import os
import uuid
from collections import OrderedDict
from datetime import datetime

from django.http import JsonResponse

from django.conf import settings
from mongoengine import Q

from component import return_message
from component.base_views import BaseObject

from component.esb_api import EsbApi
from component.libs import GetUserInfo, first_error_message, ordered_yaml_dump
from component.status_code import success, SuccessStatusCode, ErrorStatusCode, error
from repo.models import BusinessModel, ApplicationModel, RepositoryModel, RepositoryTagsModel


# 业务树
class BusinessTree(BaseObject):
    def get_business_application_list(self, request):
        user_query = GetUserInfo().get_user_info(request)
        business_tree_list = self._get_business_tree(user_query=user_query)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, business_tree_list, language=self.ops_language()))

    def _get_business_tree(self, user_query=None):
        if not user_query:
            return False, return_message.USER_NOT_EXISTED_MESSAGE
        business_queryset = BusinessModel.fetch_all()
        return [business_query.to_tree_dict(user_query=user_query) for business_query in business_queryset]

    def _business_application_list(self, bk_token):
        business_tree_list = self._business_tree(bk_token)
        for business_tree in business_tree_list:
            app_list = business_tree.get("children", [])
            if app_list:
                for app in app_list:
                    if "children" in app.keys():
                        del app["children"]
        return business_tree_list

    def _check_application_exist(self, bk_token, app_name):
        if app_name in self._application_list(bk_token=bk_token, data_type="app_name_list"):
            return True
        else:
            return False

    def _application_list(self, bk_token, data_type="app_list"):
        business_tree_list = self._business_tree(bk_token)
        app_list = []
        app_name_list = []
        for business_tree in business_tree_list:
            application_list = business_tree.get("children", [])
            if application_list:
                for app in application_list:
                    if "children" in app.keys():
                        del app["children"]
                    app_list.append(app)
                    app_name_list.append(app.get("unique_code"))
        if data_type == "app_name_list":
            return app_name_list
        else:
            return app_list

    def _business_tree(self, token):
        """
        [
            {
                'type': 'BUSINESS',
                'code': 1,
                'unique_code': 'OpsAny',
                'name': 'OpsAny产品线',
                'children': [
                    {
                        'type': 'APPLICATION',
                        'code': 1,
                        'unique_code': 'OpsAny',
                        'name': 'OpsAny智能运维平台',
                        'children': [
                            {
                                'type': 'SERVICE',
                                'code': 1,
                                'unique_code': 'fuwu', '
                                name': '服务'
                            }
                        ]
                    }
                ]
            }
        ]
        """
        esb_obj = EsbApi(token)
        business_tree_list = esb_obj.business_tree()
        return business_tree_list


# 收藏制品库
class RepositoryTags(BaseObject):
    def tags_repository(self, request):
        data = json.loads(request.body)
        user_query = GetUserInfo().get_user_info(request)
        status, message = self._tags_repository(data, user_query)
        if not status:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=message, language=self.ops_language()))
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, language=self.ops_language()))

    def _tags_repository(self, data, user_query):
        code = data.get("code")
        repo_code = data.get("repo_code")
        application_query = ApplicationModel.fetch_one(code=code)
        if not application_query:
            return JsonResponse(error(ErrorStatusCode.APPLICATION_NOT_EXISTED, language=self.ops_language()))
        # if user_query.role not in [1]:
        #     if not ApplicationUserRoleModel.fetch_one(user_info=user_query, application=application_query):
        #         return JsonResponse(error(ErrorStatusCode.USER_NOT_APPLICATION_POWER, language=self.ops_language()))
        tags = data.get("tags")
        if not user_query:
            return False, return_message.USER_NOT_EXISTED_MESSAGE
        repo_query = RepositoryModel.fetch_one(code=repo_code)
        if not repo_query:
            return False, return_message.REPOSITORY_NOT_EXISTED_MESSAGE
        repo_tags = RepositoryTagsModel.fetch_one(repository=repo_query, user_info=user_query)

        if tags:
            if not repo_tags:
                RepositoryTagsModel.create(repository=repo_query, user_info=user_query)
            return True, ""
        else:
            if repo_tags:
                repo_tags.delete()
            return True, ""
