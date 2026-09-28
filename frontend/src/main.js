// with polyfills
import 'core-js/stable'
import { initVersionCheck } from './utils/versionCheck'
import 'regenerator-runtime/runtime'

import Vue from 'vue'
import storage from 'store'
import { updateTheme } from '@/utils/util'
import App from './App.vue'
import router from './router'
import store from './store/'
import i18n from './locales'
import { VueAxios } from './utils/request'
import ProLayout, { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import themePluginConfig from '../config/themePluginConfig'
import ContentHeader from '@/views/components/ContentHeader'
import VCharts from 'v-charts'
import VeRing from 'v-charts/lib/ring.common'
import countTo from 'vue-count-to'
import searchBox from './components/searchBox'
import bootstrap from './core/bootstrap'
import './core/lazy_use'
import './utils/filter' // global filter
import './global.less'
import './permission' // permission control
import VueWatermarkDirective from 'vue-watermark-directive'
import mavonEditor from 'mavon-editor'
import 'mavon-editor/dist/css/index.css'
import echarts from "echarts"

Vue.use(mavonEditor)
Vue.use(VueWatermarkDirective)
Vue.prototype.$echarts = echarts
Vue.config.productionTip = false

// mount axios to `Vue.$http` and `this.$http`
Vue.use(VueAxios)
// Vue.use(VCharts)
Vue.component(VeRing.name,VeRing)
Vue.component('pro-layout', ProLayout)
Vue.component('page-header-wrapper', PageHeaderWrapper)
Vue.component('content-header', ContentHeader)
Vue.component('count-to', countTo)
Vue.component('search-box', searchBox)

window.umi_plugin_ant_themeVar = themePluginConfig.theme

initVersionCheck(router)
// 登录失效全局兜底：广播先于组件挂载时记标记，组件挂载补弹；登录完成（storage/BC）刷新恢复
window.addEventListener('opsany-header:auth-failed', () => {
    window.__opsany_relogin_pending = true
})
window.addEventListener('storage', e => {
    if (e.key === 'opsany_relogin_flag' && e.newValue) window.location.reload()
})
try {
    const bc = new BroadcastChannel('opsany_relogin')
    bc.onmessage = e => {
        if (e.data === 'login-complete') window.location.reload()
    }
} catch (e) {}

const themeName = storage.get('opsany-theme') || 'theme-default'
updateTheme(themeName)


new Vue({
    router,
    store,
    i18n,
    created: bootstrap,
    render: h => h(App)
}).$mount('#app')