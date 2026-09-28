# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
"""

from django.urls import path

from repo import nexus_views, base_views

urlpatterns = [
    # delete:delete_nexus_repository
    path("delete-nexus-repository/", nexus_views.NexusRepositoryDeleteView.as_view()),  # 删除制品库
    # delete:delete_nexus_repository_component
    path("delete-nexus-repository-component/", nexus_views.NexusComponentDeleteView.as_view()),  # 删除制品
    # get:get_home_page
    path("get-home-page/", nexus_views.GetHomePageView.as_view()),  # 获取制品库资源统计数量   √
    # get:get_nexus_repository
    path("get-nexus-repository/", nexus_views.NexusRepositoryGetView.as_view()),  # 获取制品库
    # get:get_nexus_repository_component
    path("get-nexus-repository-component/", nexus_views.NexusComponentGetView.as_view()),  # 获取制品库的组件
    # get:get_nexus_repository_component_asset
    path("get-nexus-repository-component-asset/", nexus_views.NexusAssetView.as_view()),  # 制品库资源
    # get:get_nexus_repository_component_tree
    path("get-nexus-repository-component-tree/", nexus_views.NexusComponentTreeView.as_view()),  # 获取版本资源(树结构-带资源)
    # get:get_nexus_repository_component_tree_v2
    path("get-nexus-repository-component-tree-v2/", nexus_views.NexusComponentTreeV2View.as_view()),  # 获取版本资源(树结构不带资源)
    # get:get_nexus_repository_component_v2
    path("get-nexus-repository-component-v2/", nexus_views.NexusComponentV2View.as_view()),  # 获取资源(根据组)
    # get:get_nexus_repository_format
    path("get-nexus-repository-format/", nexus_views.RepositoryFormatView.as_view()),  # 制品库格式
    # get:get_nexus_repository_guide
    path("get-nexus-repository-guide/", nexus_views.RepositoryGuideGetView.as_view()),  # 获取制品库使用指引
    # get:get_nexus_search_component
    path("get-nexus-search-component/", nexus_views.SearchComponentView.as_view()),  # 组件搜索
    # get:get_repo
    path("get-repo/", nexus_views.RepoGetView.as_view()),  # 获取制品库信息
    # get:get_repository_pagination
    path("get-repository-pagination/", nexus_views.GetRepositoryPaginationView.as_view()),  # 获取所有的制品库（包括公共）   √
    # post:post_clone_project
    path("post-clone-project/", nexus_views.CloneProjectView.as_view()),  # 克隆操作
    # post:post_nexus_project
    path("post-nexus-project/", nexus_views.NexusRepositoryView.as_view()),  # 制品库下载
    # post:post_nexus_repository
    path("post-nexus-repository/", nexus_views.NexusRepositoryPostView.as_view()),  # 新建制品库
    # post:post_nexus_repository_component_upload
    path("post-nexus-repository-component-upload/", nexus_views.NexusComponentPostView.as_view()),  # 上传制品
    # post:post_nexus_repository_guide
    path("post-nexus-repository-guide/", nexus_views.RepositoryGuidePostView.as_view()),  # 更新制品库使用指引
    # put:put_repo
    path("put-repo/", nexus_views.RepoPutView.as_view()),  # 修改制品库权限
    # get:sync_user_info
    path("update-director/", base_views.UpdateDirectorView.as_view()),  # 被动同步rbac用户到本地
]
