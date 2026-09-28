import request from '@/utils/request';

export const getServiceCheckFolder = (data = {}) => {
    return request({
        url: "service-check-folder/",
        method: "get",
        params: data
    })
}
export const addServiceCheckFolder = (data = {}) => {
    return request({
        url: "service-check-folder/",
        method: "post",
        data
    })
}
export const editServiceCheckFolder = (data = {}) => {
    return request({
        url: "service-check-folder/",
        method: "put",
        data
    })
}
export const delServiceCheckFolder = (data = {}) => {
    return request({
        url: "service-check-folder/",
        method: "delete",
        data
    })
}