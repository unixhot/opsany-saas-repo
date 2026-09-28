<template>
    <div>
        <a-modal okText="添加" cancelText="取消" width="1100px" v-model="visible" @ok="handleOk">
            <a-tabs v-model="activeTab">
                <a-tab-pane v-for="item in tabList" :key="item.key" :tab="item.name">
                    <component v-if="activeTab == item.key" :is="activeTab" :ref="item.key"></component>
                </a-tab-pane>
            </a-tabs>
        </a-modal>
    </div>
</template>
<script>
import Host from './components/host'
import Group from './components/Group'
export default {
    components: { Host, Group },
    data() {
        return {
            visible: false,
            activeTab: 'Host',
            tabList: [
                { key: 'Host', name: '选择主机' },
                // { key: 'Group', name: '选择主机分组' },
            ],
            parentType: '', //父级组件可能会用到
        }
    },
    watch: {},
    methods: {
        // type  由父组件传过来的 用户区分文件分发时的选择
        // whetherToDisplayTheGroup 不展示分组 默认为true
        showModal(type, whetherToDisplayTheGroup = true) {
            this.tabList = this.$options.data().tabList
            if (whetherToDisplayTheGroup === false) this.tabList.splice(1, 1)
            this.activeTab = ''
            this.$nextTick(() => {
                this.activeTab = this.$options.data().activeTab
            })
            this.parentType = type
            this.visible = true
        },

        handleOk(e) {
            this.$nextTick(() => {
                let selectedRows = this.$refs[this.activeTab][0]?.selectedRows
                if (this.activeTab == "Group") {
                    let flag = selectedRows.find(item => {
                        return item.code == "all"
                    })
                    if (flag) {
                        selectedRows = this.$refs.Group[0].allTreeRowList
                    }
                }
                this.$emit('func', selectedRows, this.parentType, this.activeTab)
                this.parentType = ''
                this.visible = false
            })
        },
    },
}
</script>
<style lang="less" scoped>
/deep/.ant-modal-body {
    height: 700px;
    overflow-y: scroll;
}
/deep/.ant-modal {
    margin: -30px auto 0;
}
</style>
