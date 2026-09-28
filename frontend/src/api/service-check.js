import request from '@/utils/request';

export const getServiceCheckData = (data = {}) => {
    return request({
        url: "service-check/",
        method: "get",
        params: data
    })
}
export const addServiceCheckData = (data = {}) => {
    return request({
        url: "service-check/",
        method: "post",
        data
    })
}
export const editServiceCheckData = (data = {}) => {
    return request({
        url: "service-check/",
        method: "put",
        data
    })
}
export const delServiceCheckData = (data = {}) => {
    return request({
        url: "service-check/",
        method: "delete",
        data
    })
}
