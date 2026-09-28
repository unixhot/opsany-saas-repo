import datetime
import time

from repo.models import ToolsModel, RepositoryModel, RawComponentModel, RawComponentGroupModel
from repo.utils import constant
from repo.utils.nexus_api import NexusApi


# 同步Nexus数据- 耗时0.1秒左右，有数据1秒左右
def nexus_sync_data():
    # 同步制品库
    t1 = time.time()
    tool_query = ToolsModel.fetch_one(tool_type="repository")
    if not tool_query:
        return "error"
    if tool_query.link_status != constant.TOOL_LINK_STATUS_SUCCESS:
        return "error"
    # print(tool_query.to_dict())

    # 同步制品库
    res = NexusApi(**tool_query.link_tool_dict()).get_repository()
    if res.get("status"):
        nexus_data = res.get("data")
        # print("nexus_data", nexus_data)
        # nexus-devops 增加,修改
        # print("repo", res)
        for repo in nexus_data:
            repo_query = RepositoryModel.fetch_one(name=repo.get("name"))
            if repo_query:
                repo_query.update(**repo)
            else:
                RepositoryModel.create(**repo)

        # devops-nexus 本地删除多余制品库
        repo_queryset = RepositoryModel.fetch_all()
        nexus_name_li = [nexus.get("name") for nexus in nexus_data]
        for repo in repo_queryset:
            if repo.name not in nexus_name_li:
                repo.delete()
    else:
        return "error"
    t2 = time.time()
    print("同步制品库耗时：", t2 - t1)


def nexus_sync_component(nexus_api, repository_id):
    t1 = time.time()
    component_list = nexus_api.get_all_component(repository_id=repository_id)
    new_id_list = []
    group_code_list = []
    for component in component_list:
        group = component.get("group")
        data_id = component.get("id")
        if group == "/":
            query = RawComponentModel.fetch_one(repository_id=repository_id, data_id=data_id)
            if not query:
                query = RawComponentModel.create(repository_id=repository_id, data_dict=component, data_id=data_id)
            else:
                query.update(repository_id=repository_id, data_dict=component, data_id=data_id)
        else:
            group_list = group.split("/")
            group_list.remove("")
            group_query, parent = None, None
            for g in group_list:
                group_query = RawComponentGroupModel.fetch_one(name=g, parent=parent, repository_id=repository_id)
                if not group_query:
                    group_query = RawComponentGroupModel.create(name=g, parent=parent, repository_id=repository_id)
                parent = group_query
                group_code_list.append(group_query.code)

            query = RawComponentModel.fetch_one(repository_id=repository_id, data_id=data_id)
            if not query:
                query = RawComponentModel.create(repository_id=repository_id, data_dict=component, group=group_query, data_id=data_id)
            else:
                query.update(repository_id=repository_id, data_dict=component, group=group_query, data_id=data_id)
        new_id_list.append(data_id)
    RawComponentModel.objects.filter(repository_id=repository_id, data_id__nin=new_id_list).delete()
    RawComponentGroupModel.objects.filter(repository_id=repository_id, code__nin=group_code_list).delete()

    t2 = time.time()
    # print("同步 {} 仓库资源耗时：".format(str(repository_id)), t2-t1)
    return "Success"
