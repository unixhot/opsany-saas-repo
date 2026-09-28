import request from '@/utils/request'

import config from '@/config/defaultSettings'
const api = config.baseUrl+'tool-type/'



export function getToolType(data) {
    return request({
        url: api,
        method: 'get',
        params: data
    })
}

