import { axios } from '@/utils/request'


// table数据
export const getApp = (data = {}) => {
    return axios({
        url: 'app/',
        method: 'get',
        params: data
    })
}
// 分组
export const getModel = (data = {}) => {
    return axios({
        url: 'model/',
        method: 'get',
        params: data
    })
}


// 指标采集（管控）
export const getMetricCollect = (data = {}) => {
    return axios({
        url: 'get-metric-collect/',
        method: 'get',
        params: data
    })
}

// 获取Prometheus监控实例
export const getPromTree = (data = {}) => {
    return axios({
        url: 'get-prom-tree/',
        method: 'get',
        params: data
    })
}

// 分发文件
export const metricSend = (data = {}) => {
    return axios({
        url: 'metric-send/',
        method: 'post',
        data
    })
}

// 安装
export const metricInstall = (data = {}) => {
    return axios({
        url: 'metric-install/',
        method: 'post',
        data
    })
}

// 获取日志
export const getMetricInstallLog = (data = {}) => {
    return axios({
        url: 'metric-install-log/',
        method: 'get',
        params: data
    })
}

// 注册Prom
export const metricRegisterProm = (data = {}) => {
    return axios({
        url: 'metric-register-prom/',
        method: 'post',
        data
    })
}

// 测试(最后一步)
export const metricInstStatus = (data = {}) => {
    return axios({
        url: 'metric-inst-status/',
        method: 'post',
        data
    })
}

// 刷新
export const flushInstStatus = (data = {}) => {
    return axios({
        url: 'flush-inst-status/',
        method: 'get',
        params: data
    })
}