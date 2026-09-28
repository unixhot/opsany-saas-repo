import request from '@/utils/request'

// 获取主机分组
export const getAllHostGroup = (data = {}) => {
    return request({
        url: "get-all-host-group/",
        method: "get",
        params: data
    })
}

//获取分组主机列表
export const getHostInfo = (data = {}) => {
    return request({
        url: "get-host-info/",
        method: "get",
        params: data
    })
}