import request from '@/utils/request';

//获取用户信息
export const getUserInfo = (data = {}) => {
	return request({
		url: "user-info/",
		method: "get",
		params: data
	})
}

//上传图标
export const uploadHeadImg = (data = {}) => {
	return request({
		url: "user-icon/",
		method: "post",
		data
	})
}

//获取所有用户列表
export const getUserList = (data = {}) => {
	return request({
		url: "user/",
		method: "get",
		params: data
	})
}
