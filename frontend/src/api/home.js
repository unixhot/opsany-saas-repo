import request from '@/utils/request';

//获取首页数据
export const getHomePage = (data = {}) => {
    return request({
        url: "home-page/",
        method: "get",
        params: data,
        showDialog: false,
    })
}

//最近活跃的制品库
export const gethomePageActive = (data = {}) => {
    return request({
        url: "home-page-active/",
        method: "get",
        params: data,
        showDialog: false,
    })
}

//制品库文件数量统计排名
export const gethomePageCount = (data = {}) => {
    return request({
        url: "home-page-count/",
        method: "get",
        params: data,
        showDialog: false,
    })
}