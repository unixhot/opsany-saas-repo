import {
  axios
} from '@/utils/request'

const api = 'host-inst/'

function add(parameter) {
  return axios({
    url: api,
    method: 'post',
    data: parameter
  })
}

function edit(parameter) {
  return axios({
    url: api,
    method: 'put',
    data: parameter
  })
}
function getList(parameter) {
  return axios({
    url: api,
    method: 'get',
    params: parameter
  })
}

function del(parameter) {
  return axios({
   url: api,
   method: 'delete',
   data: parameter,
  })
}
export default {
  add,
  del,
  getList,
  edit
}
