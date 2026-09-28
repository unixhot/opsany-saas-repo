import { axios } from '@/utils/request'


export const getHostGroup = (data = {}) => {
    return axios({
        url: 'host-inst-group/',
        method: 'get',
        params: data
    })
}