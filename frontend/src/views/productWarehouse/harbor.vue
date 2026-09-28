<template>
    <div>
        <content-header>
            <div slot="docs"></div>
        </content-header>
        <a-card>
            <div class="content_main">
                <a-spin :spinning="spinning">
                    <a-tabs default-active-key="1" @change="callback">
                        <a-tab-pane v-for="item in tabList" :key="item.name" :tab="item.name"></a-tab-pane>
                        <a-button @click="reload" :loading="tableLoading" icon="reload" slot="tabBarExtraContent">
                            刷新
                        </a-button>
                    </a-tabs>
                    <a-table style="margin-top: 12px" :scroll="{x:800}" @change="tableChange" :pagination="tableQuery" :columns="columns" :dataSource="tableData" :loading="tableLoading" :row-key="record => record.id">

                    </a-table>
                </a-spin>
            </div>
        </a-card>
    </div>
</template>

<script>
import { getHarborProject, getHarborRepisitory } from "@/api/harbor.js"
import moment from "moment"
export default {
    data() {
        return {
            spinning: false,
            tabList: [],
            tableQuery: {
                current: 1,
                pageSize: 10,
                total: 0,
                showTotal: total => `共 ${total} 条数据`,
                pageSizeOptions: ['10', '20', '40', '50', '100', '150', '200',],
            },
            tableData: [],
            tableLoading: false,
            columns: [
                { title: "名称", dataIndex: 'name', width: 200 },
                { title: "创建时间", dataIndex: 'creatTime', width: 150 },
                { title: "更新时间", dataIndex: 'updateTime', width: 150 },
                { title: "制品数量", dataIndex: 'artifact_count', width: 100 },
                { title: "下载次数", dataIndex: 'pull_count', width: 100 },

            ],
            project_name: "",
        }
    },
    methods: {
        // 获取项目
        getHarborProjectData() {
            this.spinning = true
            getHarborProject().then(res => {
                this.tabList = res.data
                if (this.project_name) {
                    this.getTableData()
                } else if (this.tabList[0]) {
                    this.project_name = this.tabList[0].name
                    this.getTableData()
                }
            }).finally(() => {
                this.spinning = false
            })
        },
        callback(val) {
            this.project_name = val
            this.getTableData()
        },
        tableChange({ current, pageSize }) {
            this.tableQuery.current = current
            this.tableQuery.pageSize = pageSize
            this.getTableData()
        },
        // 获取镜像数据
        getTableData() {
            let params = {
                project_name: this.project_name,
                current: this.tableQuery.current,
                pageSize: this.tableQuery.pageSize,
            }
            this.tableLoading = true
            getHarborRepisitory(params).then(res => {
                if (res.data?.data) {
                    this.tableQuery.total = res.data.total
                    res.data.data.map(item => {
                        item.creatTime = item.creation_time && moment(item.creation_time).format('YYYY-MM-DD HH:mm:ss')
                        item.updateTime = item.update_time && moment(item.update_time).format('YYYY-MM-DD HH:mm:ss')
                    })
                    this.tableData = res.data.data
                } else {
                    this.tableData = []
                }
            }).finally(() => {
                this.tableLoading = false
            })
        },
        reload() {
            this.getHarborProjectData()
        },
    },
    mounted() {
        this.getHarborProjectData()
    }
}
</script>

<style lang="less" scoped>
.content_main {
}
</style>