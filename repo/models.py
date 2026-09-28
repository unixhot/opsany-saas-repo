from datetime import timedelta

import mongoengine as db
from datetime import datetime

# Create your models here.

# 用户
from mongoengine import Q

from component.base_model import BasicDocument
from repo.utils import constant


class UserInfo(BasicDocument):
    code = db.SequenceField(primary_key=True)
    phone = db.StringField()
    username = db.StringField()
    email = db.StringField()
    ch_name = db.StringField()
    role = db.IntField()
    is_activate = db.BooleanField()
    icon_url = db.StringField()

    def to_base_dict(self):
        dt = {
            "id": self.id,
            "username": self.username,
            "ch_name": self.ch_name,
        }
        return dt

    def to_dict(self):
        dt = {
            "phone": self.phone,
            "username": self.username,
            "email": self.email,
            "ch_name": self.ch_name,
            "role": self.role,
            "icon_url": self.icon_url
        }
        return dt

    def to_code_dict(self):
        dt = {
            "code": self.code,
            "phone": self.phone,
            "username": self.username,
            "ch_name": self.ch_name,
        }
        return dt

    def to_role_dict(self):
        dt = {
            "code": self.code,
            "phone": self.phone,
            "username": self.username,
            "ch_name": self.ch_name,
        }
        return dt

    def to_user_info_dict(self):
        dt = {
            "phone": self.phone,
            "username": self.username,
            "email": self.email,
            "ch_name": self.ch_name,
            "role": self.role,
            # "icon_url": self.icon_url
        }
        return dt

    # 判断用户是否有某个应用的权限
    def is_app_auth(self, app_query):
        app_auth_queryset = self.get_get_strategy_list_by_user(app_query)
        if not app_auth_queryset:
            return False
        return True

    # 获取用户的权限策略
    def get_strategy_list_by_user(self):
        return StrategyModel.objects.filter(Q(user=self) | Q(group__in=list(GroupModel.fetch_all(user_list=self))))

    # 获取用户有权访问的所有应用code列表
    def get_auth_all_app_code_list(self):
        strategy_queryset = StrategyModel.objects.filter(Q(user=self) | Q(group__in=list(GroupModel.fetch_all(user_list=self))))

        application_code_list = list()
        for strategy_query in strategy_queryset:
            app_auth_queryset = ApplicationAuthModel.fetch_all(strategy=strategy_query)
            for app_auth_query in app_auth_queryset:
                application_code_list.append(app_auth_query.application.code)
        application_code_set_list = list(set(application_code_list))
        return application_code_set_list

    # 获取用户有权限的应用
    def get_get_strategy_list_by_user(self, app=None):
        """
        :param app: 应用或应用查询集
        :return:
        """
        # 当前用户关联的所有策略
        strategy_queryset = StrategyModel.objects.filter(Q(user=self) | Q(group__in=list(GroupModel.fetch_all(user_list=self))))
        dic = {"strategy__in": list(strategy_queryset)}
        if app:
            if isinstance(app, ApplicationModel):
                dic["application"] = app
            else:
                dic["application__in"] = list(app)
        return ApplicationAuthModel.fetch_all(**dic)

    # 获取应用或应用分组或全部应用下的资源（流水线、持续部署、制品仓库）
    def get_code_list(self, app=None, id_type="job,deploy,repo"):
        app_auth_queryset = self.get_get_strategy_list_by_user(app)
        job_code_list, job_2_list, job_3_list, job_4_list, job_5_list, job_6_list, job_7_list = [], [], [], [], [], [], []
        deploy_code_list, deploy_2_list, deploy_3_list, deploy_4_list, deploy_5_list, deploy_6_list, deploy_7_list, deploy_8_list = [], [], [], [], [], [], [], []
        repo_code_list, repo_2_list, repo_3_list, repo_4_list, repo_5_list, repo_6_list, repo_7_list = [], [], [], [], [], [], []
        for app_auth_query in app_auth_queryset:
            if "job" in id_type:
                job_code_list.extend(app_auth_query.auth_job_1)
                job_2_list.extend(app_auth_query.auth_job_2)
                job_3_list.extend(app_auth_query.auth_job_3)
                job_4_list.extend(app_auth_query.auth_job_4)
                job_5_list.extend(app_auth_query.auth_job_5)
                job_6_list.extend(app_auth_query.auth_job_6)
                job_7_list.extend(app_auth_query.auth_job_7)
            if "deploy" in id_type:
                deploy_code_list.extend(app_auth_query.auth_deploy_1)
                deploy_2_list.extend(app_auth_query.auth_deploy_2)
                deploy_3_list.extend(app_auth_query.auth_deploy_3)
                deploy_4_list.extend(app_auth_query.auth_deploy_4)
                deploy_5_list.extend(app_auth_query.auth_deploy_5)
                deploy_6_list.extend(app_auth_query.auth_deploy_6)
                deploy_7_list.extend(app_auth_query.auth_deploy_7)
                deploy_8_list.extend(app_auth_query.auth_deploy_8)
            if "repo" in id_type:
                # if "repo" in id_type and app_auth_query.all_select == 1:
                #     all_repo_code_list = [app_repo.repo.code for app_repo in ApplicationRepoModel.fetch_all(application=app_auth_query.application)]
                #     repo_code_list.extend(all_repo_code_list)
                #     repo_2_list.extend(all_repo_code_list)
                #     repo_3_list.extend(all_repo_code_list)
                #     repo_4_list.extend(all_repo_code_list)
                #     repo_5_list.extend(all_repo_code_list)
                #     repo_6_list.extend(all_repo_code_list)
                #     repo_7_list.extend(all_repo_code_list)
                if app_auth_query.all_select == 1 and app_auth_query.repo_all_select:
                    all_repo_code_list = [app_repo.repo.code for app_repo in ApplicationRepoModel.fetch_all(application=app_auth_query.application)]
                    if 1 in app_auth_query.repo_all_select:
                        repo_code_list.extend(all_repo_code_list)
                    if 2 in app_auth_query.repo_all_select:
                        repo_2_list.extend(all_repo_code_list)
                    if 3 in app_auth_query.repo_all_select:
                        repo_3_list.extend(all_repo_code_list)
                    if 4 in app_auth_query.repo_all_select:
                        repo_4_list.extend(all_repo_code_list)
                    if 5 in app_auth_query.repo_all_select:
                        repo_5_list.extend(all_repo_code_list)
                    if 6 in app_auth_query.repo_all_select:
                        repo_6_list.extend(all_repo_code_list)
                    if 7 in app_auth_query.repo_all_select:
                        repo_7_list.extend(all_repo_code_list)
                else:
                    repo_code_list.extend(app_auth_query.auth_repo_1)
                    repo_2_list.extend(app_auth_query.auth_repo_2)
                    repo_3_list.extend(app_auth_query.auth_repo_3)
                    repo_4_list.extend(app_auth_query.auth_repo_4)
                    repo_5_list.extend(app_auth_query.auth_repo_5)
                    repo_6_list.extend(app_auth_query.auth_repo_6)
                    repo_7_list.extend(app_auth_query.auth_repo_7)
        return ([list(set(job_code_list)), list(set(job_2_list)), list(set(job_3_list)), list(set(job_4_list)), list(set(job_5_list)), list(set(job_6_list)), list(set(job_7_list))],
                [list(set(deploy_code_list)), list(set(deploy_2_list)), list(set(deploy_3_list)), list(set(deploy_4_list)), list(set(deploy_5_list)), list(set(deploy_6_list)), list(set(deploy_7_list)), list(set(deploy_8_list))],
                [list(set(repo_code_list)), list(set(repo_2_list)), list(set(repo_3_list)), list(set(repo_4_list)), list(set(repo_5_list)), list(set(repo_6_list)), list(set(repo_7_list))]
                )


# 保存最近一次更新rbac用户体系时间
class UserUpdateInfo(BasicDocument):
    id = db.SequenceField(primary_key=True)
    last_update_time = db.DateTimeField()

    class Meta:
        db_table = "update_user_data"


# 业务
class BusinessModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    data = db.DictField()
    pk_name = db.StringField()
    pk_value = db.StringField()
    model_code = db.StringField()
    import_type = db.StringField(default="逐条录入")
    link_inst = db.ListField()
    business_code = db.StringField(default="")  # 业务code
    position = db.StringField(null=False, default="yw")
    parent_inst = db.StringField()
    label_list = db.ListField()
    staff_manager_list = db.ListField()
    cmdb_code = db.IntField()

    # principal_user = db.ReferenceField(UserInfo, reverse_delete_rule=db.DO_NOTHING)
    # create_user = db.ReferenceField(UserInfo, reverse_delete_rule=db.DO_NOTHING)

    def to_dict(self):
        dt = dict()
        dt["code"] = self.code
        dt["model_code"] = self.model_code
        dt["data"] = self.data
        if dt["data"]:
            dt["data"].pop("code", None)
        dt["pk_name"] = self.pk_name
        dt["pk_value"] = self.pk_value
        dt["position"] = self.position
        dt["import_type"] = self.import_type
        dt["link_inst"] = self.link_inst
        dt["parent_inst"] = self.parent_inst
        dt["business_code"] = self.business_code
        dt["created_at"] = str(self.created_at).split(".")[0]
        dt["cmdb_code"] = self.cmdb_code
        dt["application_count"] = ApplicationModel.counter(business=self)
        return dt

    def to_tree_dict(self, user_query=None):
        dt = dict()
        dt["code"] = self.code
        dt["unique_code"] = self.data.get("BUSINESS_name")
        dt["name"] = self.data.get("BUSINESS_VISIBLE_NAME")
        dt["type"] = self.model_code
        dic = {"business": self}
        if user_query:
            if user_query.role not in [1]:
                app_code_list = self.business_tree_to_strategy(user_query)
                dic["code__in"] = app_code_list
        application_queryset = ApplicationModel.fetch_all(**dic)
        application_list = [application_query.to_tree_dict() for application_query in application_queryset if
                            application_queryset]
        dt["children"] = application_list
        return dt

    # 获取用户有权限访问的所有应用code列表
    def business_tree_to_strategy(self, user_query):
        application_code_list = list()
        app_auth_queryset = user_query.get_get_strategy_list_by_user()
        for app_auth_query in app_auth_queryset:
            application_code_list.append(app_auth_query.application.code)
        application_code_set_list = list(set(application_code_list))
        return application_code_set_list


# 应用
class ApplicationModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    data = db.DictField()
    pk_name = db.StringField()
    pk_value = db.StringField()
    model_code = db.StringField()
    import_type = db.StringField(default="逐条录入")
    link_inst = db.ListField()
    business_code = db.StringField(default="")  # 业务code
    position = db.StringField(null=False, default="yw")
    parent_inst = db.StringField()
    label_list = db.ListField()
    business = db.ReferenceField(BusinessModel, reverse_delete_rule=db.CASCADE)
    staff_manager_list = db.ListField()
    cmdb_code = db.IntField()
    creator_id = db.IntField()
    creator_username = db.StringField()

    # principal_user = db.ReferenceField(UserInfo, reverse_delete_rule=db.DO_NOTHING)
    # create_user = db.ReferenceField(UserInfo, reverse_delete_rule=db.DO_NOTHING)

    def to_deploy_dict(self):
        dt = {}
        dt["code"] = self.code
        dt["model_code"] = self.model_code
        dt["pk_name"] = self.pk_name
        dt["pk_value"] = self.pk_value
        return dt

    def to_dict(self):
        dt = {}
        dt["code"] = self.code
        dt["model_code"] = self.model_code
        dt["data"] = self.data
        if dt["data"]:
            dt["data"].pop("code", None)
        dt["pk_name"] = self.pk_name
        dt["pk_value"] = self.pk_value
        dt["position"] = self.position
        dt["import_type"] = self.import_type
        dt["link_inst"] = self.link_inst
        dt["parent_inst"] = self.parent_inst
        dt["business_code"] = self.business_code
        dt["position"] = self.position
        dt["created_at"] = str(self.created_at).split(".")[0]
        dt["cmdb_code"] = self.cmdb_code

        business = self.business
        if business:
            dt["business"] = business.to_dict()
        return dt

    def to_tree_dict(self):
        dt = {}
        dt["code"] = self.code
        dt["unique_code"] = self.data.get("APPLICATION_name")
        dt["name"] = self.data.get("APPLICATION_VISIBLE_NAME")
        dt["type"] = self.model_code
        return dt

    def to_home_page(self):
        dt = {}
        dt["code"] = self.code
        dt["name"] = self.get_model_code_visible_name()
        return dt

    def get_model_code_name(self):
        return self.data.get(self.model_code + "_name")

    def get_model_code_visible_name(self):
        return self.data.get(self.model_code + "_VISIBLE_NAME")


# 应用权限
class ApplicationUserRoleModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    application = db.ReferenceField(ApplicationModel, reverse_delete_rule=db.CASCADE)
    user_info = db.ReferenceField(UserInfo, reverse_delete_rule=db.CASCADE)

    def to_dict(self):
        dt = {}
        dt["code"] = self.code
        dt["application"] = self.application.to_code_data_dict()
        dt["user_info"] = self.user_info.to_role_dict()
        return dt


# 工具
class ToolsModel(BasicDocument):
    type_choice = constant.TOOL_TYPE_LIST

    code = db.SequenceField(primary_key=True)
    # 工具名，最短4，最长32， 必传，唯一
    tool_name = db.StringField(min_length=2, max_length=128, required=True)
    # 工具类型，最长10， 必传
    tool_type = db.StringField(max_length=10, default="jenkins", required=True, unique=True, choices=type_choice)
    # 工具访问地址， 必传
    api_addr = db.StringField(max_length=255, required=True)
    # 用户名
    username = db.StringField(max_length=128)
    # 密码(token)
    api_token = db.StringField(max_length=255)
    # 描述
    description = db.StringField(max_length=512)
    # status
    link_status = db.StringField(default=constant.TOOL_LINK_STATUS_ERROR, max_length=32)
    # 引用次数
    quoted_times = db.IntField(default=0)

    def to_dict(self):
        dt = dict()
        dt["code"] = self.code
        dt["tool_name"] = self.tool_name
        dt["tool_type"] = self.tool_type
        dt["api_addr"] = self.api_addr
        dt["username"] = self.username
        dt["api_token"] = "******"
        dt["description"] = self.description
        dt["link_status"] = self.link_status
        return dt

    def link_tool_dict(self):
        dt = dict()
        dt["url"] = self.api_addr
        dt["username"] = self.username
        dt["password"] = self.api_token
        return dt

    def link_git_dict(self):
        dt = dict()
        dt["url"] = self.api_addr
        dt["oauth_token"] = self.api_token
        return dt


# ST2配置
class EventStackStormServiceModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    tool_name = db.StringField(max_length=128, null=True, unique=True)
    api_addr = db.StringField(max_length=255, null=False)
    username = db.StringField(max_length=128, null=True)
    password = db.StringField(max_length=255, null=True)
    api_token = db.StringField(max_length=255, null=True)
    description = db.StringField(max_length=255, null=True)

    def __unicode__(self):
        return self.tool_name

    def __str__(self):
        return self.tool_name

    def to_dict(self):
        dt = dict()
        dt["id"] = self.id
        dt["tool_name"] = self.tool_name
        dt["api_addr"] = self.api_addr
        dt["username"] = self.username
        dt["description"] = self.description
        return dt

    def connect_use_password_dict(self):
        dt = dict()
        dt["url"] = self.api_addr
        dt["username"] = self.username
        dt["password"] = self.password
        return dt

    def connect_use_api_token_dict(self):
        dt = dict()
        dt["url"] = self.api_addr
        dt["api_key"] = self.api_token
        return dt


# 制品库
class RepositoryModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    is_app = db.BooleanField(default=False)
    name = db.StringField()
    # hosted  proxy group
    type = db.StringField(null=True)
    # raw maven2 docker pypi helm
    format = db.StringField(null=True)
    status = db.StringField(default="Online")
    url = db.StringField()
    describe = db.StringField()
    attributes = db.DictField()
    active_time = db.DateTimeField()
    user = db.ReferenceField(UserInfo, reverse_delete_rule=db.CASCADE)
    # 用户在平台创建的docker类型制品库
    docker_user_url = db.StringField(null=True, default="")

    def to_simple_dict(self):
        dt = {
            "name": self.name,
            "format": self.format
        }
        return dt

    def to_dict(self):
        dt = dict()
        dt["code"] = self.code
        dt["is_app"] = self.is_app
        dt["name"] = self.name
        dt["type"] = self.type
        dt["format"] = self.format
        dt["status"] = self.status
        dt["url"] = self.url
        dt["describe"] = self.describe if self.describe else ""
        dt["attributes"] = self.attributes
        if self.active_time:
            dt["active_time"] = self.active_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            dt["active_time"] = None
        return dt

    def to_devops_dict(self, user_query=None, repo_code_list=None):
        dt = dict()
        dt["code"] = self.code
        dt["is_app"] = self.is_app
        dt["name"] = self.name
        dt["type"] = self.type
        dt["format"] = self.format
        dt["status"] = self.status
        dt["url"] = self.url
        dt["describe"] = self.describe if self.describe else ""
        dt["attributes"] = self.attributes
        if self.active_time:
            dt["active_time"] = self.active_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            dt["active_time"] = None
        dt["tags"] = False

        if self.user:
            dt["username"] = self.user.username
            dt["ch_name"] = self.user.ch_name

        if user_query:
            if RepositoryTagsModel.fetch_one(user_info=user_query, repository=self):
                dt["tags"] = True

        if repo_code_list:
            dt["can_update"] = self.code in repo_code_list[1]
            dt["can_delete"] = self.code in repo_code_list[2]
            dt["can_file_detail"] = self.code in repo_code_list[3]
            dt["can_file_delete"] = self.code in repo_code_list[4]
            dt["can_file_upload"] = self.code in repo_code_list[5]
            dt["can_file_download"] = self.code in repo_code_list[6]
        if user_query.role == 1:
            dt["can_update"] = True
            dt["can_delete"] = True
            dt["can_file_detail"] = True
            dt["can_file_delete"] = True
            dt["can_file_upload"] = True
            dt["can_file_download"] = True

        return dt

    def to_tags_dict(self, user_query=None, repo_code_list=None):
        dt = dict()
        dt["code"] = self.code
        dt["is_app"] = self.is_app
        dt["name"] = self.name
        dt["type"] = self.type
        dt["format"] = self.format
        dt["status"] = self.status
        dt["url"] = self.url
        dt["describe"] = self.describe if self.describe else ""
        dt["attributes"] = self.attributes
        if self.active_time:
            dt["active_time"] = self.active_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            dt["active_time"] = None
        dt["tags"] = False

        if self.user:
            dt["username"] = self.user.username
            dt["ch_name"] = self.user.ch_name

        if user_query:
            if RepositoryTagsModel.fetch_one(user_info=user_query, repository=self):
                dt["tags"] = True

        if repo_code_list:
            dt["can_update"] = self.code in repo_code_list[1]
            dt["can_delete"] = self.code in repo_code_list[2]
            dt["can_file_detail"] = self.code in repo_code_list[3]
            dt["can_file_delete"] = self.code in repo_code_list[4]
            dt["can_file_upload"] = self.code in repo_code_list[5]
            dt["can_file_download"] = self.code in repo_code_list[6]
        if user_query.role == 1:
            dt["can_update"] = True
            dt["can_delete"] = True
            dt["can_file_detail"] = True
            dt["can_file_delete"] = True
            dt["can_file_upload"] = True
            dt["can_file_download"] = True

        # 所属应用
        app_repo_query = ApplicationRepoModel.fetch_one(repo=self)
        if app_repo_query:
            try:
                dt["application"] = app_repo_query.application.to_tree_dict()
            except:
                pass
        return dt

    # 编辑2
    def is_auth_update(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 2 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_2):
                return True
        return False

    # 删除3
    def is_auth_delete(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 3 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_3):
                return True
        return False

    # 查看文件详情4
    def is_auth_file_detail(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 4 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_4):
                return True
        return False

    # 删除文件5
    def is_auth_file_delete(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 5 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_5):
                return True
        return False

    # 上传制品6
    def is_auth_upload(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 6 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_6):
                return True
        return False

    # 下载制品7
    def is_auth_file_download(self, user_query):
        app_auth_queryset = user_query.get_get_strategy_list_by_user(ApplicationRepoModel.fetch_one(repo=self).application)
        for app_auth_query in app_auth_queryset:
            if app_auth_query.all_select == 1 and 7 in app_auth_query.repo_all_select:
                return True
            if (self.code in app_auth_query.auth_repo_1) and (self.code in app_auth_query.auth_repo_7):
                return True
        return False


# 制品库资源
class RepositoryComponentModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    repository = db.ReferenceField(RepositoryModel, reverse_delete_rule=db.CASCADE)
    component = db.DictField(null=True)

    def to_dict(self):
        dt = dict()
        dt["repository"] = self.repository
        dt["component"] = self.component if self.component else []
        return dt

    def to_component(self):
        return self.component if self.component else []


# 制品库导引
class RepositoryGuideModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    format = db.StringField()
    content = db.StringField()

    def to_dict(self):
        dt = dict()
        dt["code"] = self.code
        dt["format"] = self.format
        dt["content"] = self.content
        return dt


# 应用制品库关联
class ApplicationRepoModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    application = db.ReferenceField(ApplicationModel, reverse_delete_rule=db.CASCADE)
    repo = db.ReferenceField(RepositoryModel, reverse_delete_rule=db.CASCADE)

    def to_dict(self, user_query=None):
        dt = dict()
        dt["code"] = self.code
        dt["application_name"] = self.application.get_application_name()
        dt["repo"] = self.repo.to_tags_dict(user_query)
        return dt


class RawComponentGroupModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    repository_id = db.StringField()
    parent = db.ReferenceField("self", reverse_delete_rule=db.CASCADE, null=True)
    name = db.StringField()

    def to_parent_dict(self, repository_id):
        children = []
        children_query_set = RawComponentGroupModel.fetch_all(repository_id=repository_id ,parent=self).order_by("created_at")
        for i in children_query_set:
            children.append(i.to_parent_dict(repository_id))
        dic = {
            "code": self.code,
            "name": self.name,
            "repository_id": self.repository_id,
            "children": children
        }
        component_list = self.get_raw_component_list()
        dic["component_list"] = component_list
        return dic

    def to_parent_v2_dict(self, repository_id):
        children = []
        children_query_set = RawComponentGroupModel.fetch_all(repository_id=repository_id ,parent=self).order_by("created_at")
        for i in children_query_set:
            children.append(i.to_parent_v2_dict(repository_id))
        dic = {
            "code": self.code,
            "name": self.name,
            "repository_id": self.repository_id,
            "children": children
        }
        return dic

    def get_children_group_queryset(self):
        children_group_queryset = [self]
        query_set = RawComponentGroupModel.fetch_all(parent=self)
        children_group_queryset.extend(query_set)
        for children_query in query_set:
            children_query_set = RawComponentGroupModel.fetch_all(parent=children_query)
            children_group_queryset.extend(children_query_set)
            if children_query_set:
                children_group_queryset += children_query.get_children_group_queryset()
        return list(set(children_group_queryset))

    def get_raw_component_list(self):
        component_group_queryset = RawComponentModel.fetch_all(group=self)
        return [component.data_dict for component in component_group_queryset]
        # return [component.to_base_dict() for component in component_group_queryset]


class RawComponentModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    repository_id = db.StringField()
    group = db.ReferenceField(RawComponentGroupModel, reverse_delete_rule=db.CASCADE, null=True)
    data_id = db.StringField()
    data_dict = db.DictField()

    def to_base_dict(self):
        dt = {
            "id": self.data_dict.get("id"),
            "repository": self.data_dict.get("repository"),
            "format": self.data_dict.get("format"),
            "downloadUrl": self.data_dict.get("assets")[0].get("downloadUrl"),
        }
        return dt

    def to_dict(self):
        dt = self.data_dict
        dt["repository_id"] = self.repository_id

        if self.group:
            dt["group_name"] = self.group.name
            dt["group_code"] = self.group.code
        else:
            dt["group_name"] = "/"
            dt["group_code"] = None
        return dt


# 收藏任务
class RepositoryTagsModel(BasicDocument):
    repository = db.ReferenceField(RepositoryModel, required=True, reverse_delete_rule=db.CASCADE)
    user_info = db.ReferenceField(UserInfo, required=True, reverse_delete_rule=db.CASCADE)


class GroupModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    group_name = db.StringField(max_length=128, unique=True, null=False)
    description = db.StringField(max_length=255, null=True)
    user_list = db.ListField(db.ReferenceField(UserInfo, null=True))

    def to_base_dict(self):
        dt = {
            "code": self.code,
            "group_name": self.group_name,
            "description": self.description
        }
        return dt

    def to_dict(self):
        dt = dict()
        dt["code"] = self.code
        dt["group_name"] = self.group_name
        dt["description"] = self.description
        dt["user_list"] = [user_query.to_base_dict() for user_query in self.user_list if self.user_list]
        return dt


# 权限策略
class StrategyModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    strategy_name = db.StringField(unique=True, null=True)
    description = db.StringField(max_length=1024, unique=False, null=True)
    quoted_times = db.IntField()
    group_quoted_times = db.IntField()
    user = db.ListField(db.ReferenceField(UserInfo, null=True))
    group = db.ListField(db.ReferenceField(GroupModel, null=True))

    def to_dict(self):
        dt = {
            "code": self.code,
            "strategy_name": self.strategy_name,
            "description": self.description,
            "quoted_times": self.quoted_times,
            "group_quoted_times": self.group_quoted_times
        }
        return dt


class ApplicationAuthModel(BasicDocument):
    code = db.SequenceField(primary_key=True)
    strategy = db.ReferenceField(StrategyModel, reverse_delete_rule=db.CASCADE)
    application = db.ReferenceField(ApplicationModel, reverse_delete_rule=db.CASCADE)
    all_select = db.IntField(default=0)
    job_list = db.ListField()       # 存放流水线及对应操作权限
    deploy_list = db.ListField()    # 存放部署任务及对应操作权限
    repo_list = db.ListField()      # 存放制品仓库及对应操作权限
    apm_list = db.ListField()      # 存放APM服务组及对应操作权限
    # 是否为新数据 1：新数据
    new = db.IntField(default=0)

    # 流水线-全部      1：查看  2：编辑  3：删除  4：执行  5：终止  6：查看日志  7.删除日志
    job_all_select = db.ListField()

    # 持续部署-全部    1：查看  2：编辑  3：删除  4：执行  5：终止  6：克隆  7：查看日志  8.删除日志
    deploy_all_select = db.ListField()

    # 制品库-全部      1：查看  2：编辑  3：删除  4：查看文件详情  5：删除文件  6：上传制品  7：下载制品
    repo_all_select = db.ListField()

    # APM服务组-全部      1：查看  2：编辑  3：删除
    apm_all_select = db.ListField()

    """"
    job_list = [
        {
            "job_code": 11,
            "action_list": [1,2,3,4,5]
        },
        {
            "job_code": 12,
            "action_list": [1,2,3,4,5]
        }
    ]
    """

    # 流水线
    auth_job_1 = db.ListField()     # 查看
    auth_job_2 = db.ListField()     # 编辑
    auth_job_3 = db.ListField()     # 删除
    auth_job_4 = db.ListField()     # 执行
    auth_job_5 = db.ListField()     # 终止
    auth_job_6 = db.ListField()     # 查看日志
    auth_job_7 = db.ListField()     # 删除日志

    # 部署任务
    auth_deploy_1 = db.ListField()  # 查看
    auth_deploy_2 = db.ListField()  # 编辑
    auth_deploy_3 = db.ListField()  # 删除
    auth_deploy_4 = db.ListField()  # 执行
    auth_deploy_5 = db.ListField()  # 终止
    auth_deploy_6 = db.ListField()  # 克隆
    auth_deploy_7 = db.ListField()  # 查看日志
    auth_deploy_8 = db.ListField()  # 删除日志 弃用

    # 制品仓库
    auth_repo_1 = db.ListField()    # 查看
    auth_repo_2 = db.ListField()    # 编辑
    auth_repo_3 = db.ListField()    # 删除
    auth_repo_4 = db.ListField()    # 查看文件详情
    auth_repo_5 = db.ListField()    # 删除文件
    auth_repo_6 = db.ListField()    # 上传制品
    auth_repo_7 = db.ListField()    # 下载制品

    auth_apm_1 = db.ListField()    # 查看
    auth_apm_2 = db.ListField()    # 编辑
    auth_apm_3 = db.ListField()    # 删除

    def to_dict(self):
        dt = {
            "code": self.code,
            "strategy_code": self.strategy.code,
            "application_code": self.application.code,
            "all_select": self.all_select,
            "job_all_select": self.job_all_select,
            "deploy_all_select": self.deploy_all_select,
            "repo_all_select": self.repo_all_select,
            "apm_all_select": self.apm_all_select,
        }
        if self.job_list:
            dt["job_list"] = self.job_list
        if self.deploy_list:
            dt["deploy_list"] = self.deploy_list
        if self.repo_list:
            dt["repo_list"] = self.repo_list
        if self.apm_list:
            dt["apm_list"] = self.apm_list
        return dt
