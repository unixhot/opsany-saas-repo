import { axios } from '@/utils/request'


export const getAlert = (data = {}) => {
    return axios({
        url: 'get-alert/',
        method: 'get',
        params: data
    })
}