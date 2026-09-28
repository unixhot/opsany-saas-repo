from repo.utils import constant
from repo.utils.nexus_api import NexusApi


def flash_all_tool_status(request, tool_queryset):
    """刷新状态(jenkins, git, repository)"""
    error_count, success_count = 0, 0
    for tool_query in tool_queryset:
        tool_dic = tool_query.link_tool_dict()
        try:
            # if tool_query.tool_type == "jenkins":
            #     jenkins_api = JenkinsApi(request, **tool_dic)
            #     status = jenkins_api.jenkins_status()
            # elif tool_query.tool_type == "git":
            #     gitlab_api = GitLabApi(**tool_query.link_git_dict())
            #     status = gitlab_api.status()
            if tool_query.tool_type == "repository":
                status = NexusApi(request, **tool_dic).status()
            else:
                status = False
        except Exception as e:
            print("flash_all_tool_status_error", e)
            status = False
        if status == True:
            tool_query.update(link_status=constant.TOOL_LINK_STATUS_SUCCESS)
            success_count += 1
        else:
            tool_query.update(link_status=constant.TOOL_LINK_STATUS_ERROR)
            error_count += 1
    return success_count, error_count
