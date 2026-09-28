import request from '@/utils/request'

// 获取菜单列表
export const getMenuList = (data = {}) => {
    return request({
        url: "get-menu/",
        method: "get",
        params: data
    })
}