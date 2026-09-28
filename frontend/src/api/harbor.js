import request from '@/utils/request'

// 获取项目列表
export const getHarborProject = (data = {}) => {
    return request({
        url: "harbor-project/",
        method: "get",
        params: data
    })
}

//获取Harbor镜像列表
export const getHarborRepisitory = (data = {}) => {
    return request({
        url: "harbor-repisitory/",
        method: "get",
        params: data
    })
}