import request from '@/utils/request'

import config from '@/config/defaultSettings'
const api = config.baseUrl


// 获取制品库数据
export function getproductWarehouse(data) {
    return request({
        url: 'nexus/repository/',
        method: 'get',
        params: data,
        showDialog:false
    })
}

// 新增制品库
export function addproductWarehouse(data) {
    return request({
        url: 'nexus/repository/',
        method: 'post',
        data,
    })
}

// 删除制品库
export function deleteproductWarehouse(data) {
    return request({
        url: 'nexus/repository/',
        method: 'delete',
        data,
    })
}

// 获取制品库资源
export function getRepositoryComponent(data) {
    return request({
        url: 'nexus/repository/component/',
        method: 'get',
        params: data,
    })
}

// 获取制品库类型
export function getFormatType(data) {
    return request({
        url: 'nexus/repository/format/',
        method: 'get',
        params: data,
    })
}

// 获取制品库指引
export function getGuide(data) {
    return request({
        url: 'nexus/repository/guide/',
        method: 'get',
        params: data,
    })
}

// 上传
export function upload(data) {
    return request({
        url: 'nexus/repository/component/upload/',
        method: 'post',
        data,
    })
}

// 获取单条制品库信息
export function getProductInformation(data) {
    return request({
        url: 'repo/',
        method: 'get',
        params: data,
    })
}
// 修改
export function editproductWarehouse(data) {
    return request({
        url: 'repo/',
        method: 'put',
        data,
    })
}

// 制品库文件搜索
export function searchComponent(data) {
    return request({
        url: 'nexus/search/component/',
        method: 'get',
        params: data,
    })
}


// 获取制品库资源树(持续部署选择软件包)  不再使用
// export function getRepositoryComponentTree(data) {
//     return request({
//         url: 'nexus/repository/component/tree-v2/',
//         method: 'get',
//         params: data,
//     })
// }

// 制品库文件(持续部署选择软件包)  不再使用
// export function getRepositoryComponentv2(data) {
//     return request({
//         url: 'nexus/repository/component-v2/',
//         method: 'get',
//         params: data,
//     })
// }

// 删除制品库文件
export function deleteproductWarehouseFile(data) {
    return request({
        url: 'nexus/repository/component/',
        method: 'delete',
        data,
    })
}

// 收藏
export function collectNexus(data) {
    return request({
        url: 'nexus/tags/',
        method: 'put',
        data,
    })
}
