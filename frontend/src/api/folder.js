import request from '@/utils/request'
// export const baseUrl = process.env.NODE_ENV === "development" ? 'https://dev.opsany.cn/t/monitor/api/grafana/v0_1/' : window.location.origin + window.API_ROOT + "api/grafana/v0_1/"
// export const baseUrl = 'api/grafana/v0_2/'

//删除folder
export const delFolder = (folder_name = '') => {
    return request({
        url: `grafana/folder/`,
        method: 'delete',
        data: { folder_name }
    })
}

//增加dashboard列表folder
export const addFolder = (data = {}) => {
    return request({
        url: `grafana/folder/`,
        method: 'post',
        data
    })
}

//修改dashboard列表folder名
export const editFolder = (data = {}) => {
    return request({
        url: `grafana/folder/`,
        method: 'put',
        data
    })
}