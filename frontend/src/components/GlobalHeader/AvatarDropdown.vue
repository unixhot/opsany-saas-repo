<template>
    <a-dropdown class="drop" :getPopupContainer="triggerNode => triggerNode" v-model="visible">
        <span class="action ant-dropdown-link user-dropdown-menu">
            <a-avatar class="avatar" size="small" :src="userInfo.icon_url" />
			<a-icon :type="visible ? 'up' : 'down'" class="action_icon"></a-icon>
        </span>
        <a-menu slot="overlay" class="user-dropdown-menu-wrapper">
            <a-menu-item class="name" style="cursor: auto">
                <p style="margin: 0; font-size: 16px; font-weight: 1000" @click.stop>
                    {{ userInfo.username }}
                </p>
                <p style="margin: 0; font-size: 12px; color: #888" @click.stop>
                    中文名称：{{ userInfo.ch_name || '暂无' }}
                </p>
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="0">
                <a :href="otherAppUrl + 'workbench/#/personSetting/personCenter'" class="menu_box">
                    <a-icon type="user" />
                    <span>个人中心</span>
                </a>
            </a-menu-item>
            <a-menu-item key="3">
                <a :href="url + '/accounts/logout/'" class="menu_box">
                    <a-icon type="logout" />
                    <span>退出登录</span>
                </a>
            </a-menu-item>
        </a-menu>
    </a-dropdown>
</template>

<script>
import { getUserInfo } from '@/api/user'
import config from '@/config/defaultSettings'
import storage from 'store'
import { mapState } from 'vuex'
import { updateTheme } from '@/utils/util'
export default {
    name: 'UserMenu',
    data() {
        return {
            url: window.API_ROOT.split('/')[0],
            otherAppUrl: window.API_ROOT.replace(`/${config.appCode}`, ''),
            userInfo: {},
			visible: false,
        }
    },
	computed: {
        ...mapState({ themeList: (state) => state.user.themeList }),
    },
    methods: {
        getUserInfo() {
            getUserInfo().then((res) => {
                this.userInfo = res.data
                this.userInfo.icon_url = config.baseUrlOfImg + res.data.icon_url
				if (this.themeList.map((item) => item.key).includes(res.data.theme)) {
                    updateTheme(res.data.theme)
                } else {
                    updateTheme('theme-default')
                }
            })
        },
    },
    mounted() {
        this.getUserInfo()
    },
}
</script>
<style lang="less" scoped>
.drop {
    min-width: 80px;
    text-align: center;
	.action_icon {
		color: #fff;
		margin-left: 6px;
		font-size: 12px;
	}
}
.ant-pro-drop-down {
    /deep/ .action {
        margin-right: 8px;
    }
    /deep/ .ant-dropdown-menu-item {
        min-width: 160px;
    }
}
.ant-dropdown-menu-item {
    padding: 10px 18px 10px 18px;
    a i {
        margin: 0 8px 0 0;
    }
}
.ant-dropdown-menu {
    border-radius: 6px;
}
.name {
    &:hover {
        background: #fff;
    }
}
.menu_box {
	i {
		color: #333;
		transform: translateY(-1.5px);
	}
	span {
		color: #333;
	}
}
</style>
