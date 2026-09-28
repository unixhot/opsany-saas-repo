import request from '@/utils/request';

//  获取收藏的导航
export const getNavList = (data = {}) => {
    return request({
        url: "get-nav-and-collection/",
        method: "get",
        params: data
    })
}



//上传图标
export const collection = (data = {}) => {
    return request({
        url: "collection/",
        method: "post",
        data
    })
}
