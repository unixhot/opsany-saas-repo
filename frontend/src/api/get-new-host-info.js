import request from '@/utils/request';

export const updateDataHostInfo = (data = {}) => {
    return request({
        url: "get-new-host-info/",
        method: "post",
        data
    })
}