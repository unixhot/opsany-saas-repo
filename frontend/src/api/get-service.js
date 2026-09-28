import request from '@/utils/request';

//获取关联服务
export const getService = (data = {}) => {
    return request({
        url: "get-service/",
        method: "get",
        data
    })
}