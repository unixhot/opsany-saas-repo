import request from '@/utils/request'
// export const baseUrl = process.env.NODE_ENV === "development" ? 'https://dev.opsany.cn/t/monitor/api/grafana/v0_2/' : window.location.origin + window.API_ROOT + "api/grafana/v0_2/"
// export const baseUrl = 'api/grafana/v0_2/'

//获取grafana信息
export const getGrafana = (id = '') => {
    return request({
        url: `grafana/grafana-url/`,
        method: 'get',
        params: {}
    })
}

//提交grafana信息
export const addGrafana = (data = {}) => {
    return request({
        url: baseUrl + `grafana/`,
        method: 'post',
        data
    })
}

//提交grafana信息
export const editGrafana = (data = {}) => {
    return request({
        url: baseUrl + `grafana/`,
        method: 'put',
        data
    })
}


//--以下为dashboard相关--

//获取默认dashboard url
export const getDefaultGrafanaUrl = (data = {}) => {
    return request({
        url:`grafana/dashboard/`,
        method: 'get',
        params: { data_type: 'home', ...data }
    })
}

//获取新建dashboard的url链接
export const getNewDashboardUrl = (data = {}) => {
    return request({
        url: `grafana/dashboard/`,
        method: 'get',
        params: { data_type: 'new', ...data }
    })
}

//获取dashboardList
export const getDashboardList = (data = {}) => {
    return request({
        url: `grafana/dashboard/`,
        method: 'get',
        params: { data_type: 'list', ...data }
    })
}

//获取某个主机的dashboardURL
export const getDashboardHostUrl = (data = {}) => {
    return request({
        url: `grafana/dashboard-url/`,
        method: 'get',
        params: data
    })
}

//修改dashboard的name
export const editDashboardName = (data = {}) => {
    return request({
        url: `grafana/dashboard/`,
        method: 'put',
        data: { update_type: 'data', ...data }
    })
}

//删除dashboard
export const delDashboard = (data = {}) => {
    return request({
        url: `grafana/dashboard/`,
        method: 'delete',
        data
    })
}

//获取导入dashboard的url
export const getImportDashboardUrl = (data = {}) => {
    return request({
        url: `grafana/dashboard-import/`,
        method: 'get',
        params: data
    })
}
