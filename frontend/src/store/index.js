import Vue from 'vue'
import Vuex from 'vuex'

import app from './modules/app'
import user from './modules/user'
import btnAuth from './modules/btnAuth'
import serviceTest from "./modules/serviceTest"
import language from './modules/language'
// import permission from './modules/permission'

import permission from './modules/async-router' //后端返回的菜单
import getters from './getters'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        app,
        user,
        permission,
        btnAuth,
        serviceTest,
        language,
    },
    state: {

    },
    mutations: {

    },
    actions: {

    },
    getters
})