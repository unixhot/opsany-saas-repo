# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa
from django.urls import path
from repo import base_views, views, nexus_views
from repo.utils import deploy_esb_api

urlpatterns = [
    # 基础接口
    path("get-menu/", base_views.DeployMenuStrategyCtrl.as_view()),  # 获取导航拦
    path("guide/", base_views.GuideCtrl.as_view()),  # 获取导航拦
    path('user-info/', base_views.GetUserInfoCtrl.as_view()),  # 获取用户信息
    path("get-nav-and-collection/", base_views.GetNavCollectionView.as_view()),  # 获取导航收藏
    path("collection/", base_views.CollectionNavView.as_view()),  # 收藏操作
    path("get-user-message/", base_views.GetUserMessageView.as_view()),  # 获取站内信
    path("read-all-message/", base_views.ReadAllMessageView.as_view()),  # 全部已读操作
    path("copyright-config/", base_views.CopyrightConfigView.as_view()),  # 底部版权信息

    # 通用接口
    path("update-director/", base_views.UpdateDirectorView.as_view()),  # 被动同步rbac用户到本地


    # 概览页
    path("home-page/", base_views.HomePageView.as_view()),  # 概览页制品库数量统计                              √
    path("home-page-active/", base_views.HomePageLeftView.as_view()),  # 概览页最近活跃                        √
    path("home-page-count/", base_views.HomePageVolumeView.as_view()),     # 概览页数量排名                    √

    path("business-tree/", views.BusinessTreeView.as_view()),  # 业务树                                       √

    path("nexus/repository/format/", views.RepositoryFormatView.as_view()),  # 制品库格式                            esb1
    path("nexus/repository/", views.NexusRepositoryView.as_view()),  # 制品库                                √删除/查看
    path("repo/", views.RepoView.as_view()),                        # 修改获取制品库描述应用权限                 √编辑
    path("nexus/repository/guide/", views.RepositoryGuideView.as_view()),  # 制品库导引                              esb2
    path("nexus/repository/component/", views.NexusComponentView.as_view()),  # 获取版本资源-get                    √删除制品
    path("nexus/repository/component/upload/", views.NexusComponentView.as_view()),  # 上传资源-post          √上传制品/删除制品

    path("nexus/repository/component/asset/", views.NexusAssetView.as_view()),  # 制品库资源                          esb
    path("nexus/search/component/", views.SearchComponentView.as_view()),  # 搜索                                    esb
    path("nexus/repository/component-v2/", views.NexusComponentV2View.as_view()),  # 获取资源(根据组)                  esb
    path("nexus/repository/component/tree/", views.NexusComponentTreeView.as_view()),  # 获取版本资源(树结构-带资源)     esb
    path("nexus/repository/component/tree-v2/", views.NexusComponentTreeV2View.as_view()),  # 获取版本资源(树结构不带资源) esb

    path("nexus/tags/", views.RepositoryTagsView.as_view()),                # 收藏制品库
    path("app-repo/", views.ApplicationRepoView.as_view()),  # 应用-制品库
    # esb-event
    path("clone-project/", deploy_esb_api.CloneProjectView.as_view()),          # 克隆操作                          esb
    path("nexus-project/", deploy_esb_api.NexusRepositoryView.as_view()),       # 制品库下载                         esb
    path("tool/", views.ToolView.as_view()),                            # Nexus工具CRUD
    path("tool/status/", views.ToolStatusView.as_view()),               # 测试状态、工具列表刷新
    path("tool/test/", views.ToolTestView.as_view()),                   # 添加工具连接测试

    # harbor项目列表
    path("harbor-project/", views.HarborProjectView.as_view()),
    path("harbor-repisitory/", views.HarborRepositoryView.as_view()),


    # esb接口
    path("get-nexus-repository-format/", nexus_views.RepositoryFormatView.as_view()),               # 制品库格式
    path("get-nexus-repository/", nexus_views.NexusRepositoryGetView.as_view()),                    # 获取制品库
    path("post-nexus-repository/", nexus_views.NexusRepositoryPostView.as_view()),                  # 新建制品库
    path("delete-nexus-repository/", nexus_views.NexusRepositoryDeleteView.as_view()),              # 删除制品库
    path("get-repo/", nexus_views.RepoGetView.as_view()),                                           # 获取制品库信息
    path("put-repo/", nexus_views.RepoPutView.as_view()),                                           # 修改制品库权限
    path("get-nexus-repository-guide/", nexus_views.RepositoryGuideGetView.as_view()),              # 获取制品库使用指引
    path("post-nexus-repository-guide/", nexus_views.RepositoryGuidePostView.as_view()),            # 更新制品库使用指引
    path("get-nexus-repository-component/", nexus_views.NexusComponentGetView.as_view()),           # 获取制品库的组件
    path("post-nexus-repository-component-upload/", nexus_views.NexusComponentPostView.as_view()),  # 上传制品
    path("delete-nexus-repository-component/", nexus_views.NexusComponentDeleteView.as_view()),     # 删除制品
    path("get-nexus-search-component/", nexus_views.SearchComponentView.as_view()),  # 组件搜索

    path("get-nexus-repository-component-asset/", nexus_views.NexusAssetView.as_view()),            # 制品库资源
    path("get-nexus-repository-component-v2/", nexus_views.NexusComponentV2View.as_view()),         # 获取资源(根据组)
    path("get-nexus-repository-component-tree/", nexus_views.NexusComponentTreeView.as_view()),     # 获取版本资源(树结构-带资源)
    path("get-nexus-repository-component-tree-v2/", nexus_views.NexusComponentTreeV2View.as_view()),  # 获取版本资源(树结构不带资源)

    path("post-clone-project/", nexus_views.CloneProjectView.as_view()),                # 克隆操作
    path("post-nexus-project/", nexus_views.NexusRepositoryView.as_view()),             # 制品库下载

    # esb接口：应用平台嵌入页面接口
    path("get-home-page/", nexus_views.GetHomePageView.as_view()),                              # 获取制品库资源统计数量   √
    path("get-repository-pagination/", nexus_views.GetRepositoryPaginationView.as_view()),       # 获取所有的制品库（包括公共）   √
]
