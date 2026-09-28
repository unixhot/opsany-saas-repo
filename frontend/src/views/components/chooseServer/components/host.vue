<template>
    <div class="content_main">
        <div class="content_main_left">
            <a-tree v-if="showTree" @select="treeSelect" :tree-data="treeData" :selectedKeys="selectedKeys" defaultExpandAll :show-line="true">
                <template slot="action" slot-scope="row">
                    <span :title="row.title + ' ('+row.self_count+'/'+ row.count +')' " class="treetitle">{{ row.title }} ({{row.self_count}}/{{row.count}})</span>
                </template>
            </a-tree>
            <a-skeleton style="padding:10px;" v-else />
        </div>
        <div class="content_main_right">
            <div class="title">
                <div>
                    <a-input-search v-model="tableQuery.search_data" @search="changeTableQuery" placeholder="请输入关键字搜索" style="width: 300px" allowClear>
                        <a-select slot="addonBefore" style="width: 100px" v-model="tableQuery.search_type">
                            <a-select-option v-for="item in searchList" :key="item.key">{{ item.name }}</a-select-option>
                        </a-select>
                    </a-input-search>
                    <a-select v-model="tableQuery.system_type" style="width: 200px; margin-left: 10px" @change="changeTableQuery">
                        <a-select-option v-for="item in system_type_list" :key="item.key" :value="item.key">{{
                        item.name
                    }}</a-select-option>
                    </a-select>
                </div>
                <p style="margin-top: 10px">
                    共{{ countData.normal + countData.not_normal || 0 }}台 正常:{{ countData.normal || 0 }} 异常:{{
                    countData.not_normal || 0
                }}
                </p>
            </div>

            <a-table style="margin-top: 10px" :row-selection="{ selectedRowKeys, onChange: onSelectChange }" :columns="columns" :dataSource="tableData" :pagination="{
                pageSize,
                current,
                showSizeChanger: true,
                showQuickJumper:true,
            }" @change="tableChange" :rowKey="(row) => row.host_name" :loading="tableLoading">
                <template slot="show_name" slot-scope="text,record">
                    <div class="show_name_cell">
                        <div class="show_name_cell_left">
                            <a-tooltip v-if="record.system_type == 'Windows'" title="Windows" placement="top">
                                <img src="~@/assets/icons1/Windows.png" alt="">
                            </a-tooltip>

                            <a-tooltip v-else-if="record.system_type == 'Linux'" title="Linux" placement="top">
                                <img src="~@/assets/icons1/Linux.png" alt="">
                            </a-tooltip>

                            <a-tooltip v-else placement="top">
                                <template slot="title">
                                    <span>未纳管，可点击右侧操作更多中【加入纳管】按钮进行纳管操作。</span>
                                </template>
                                <img src="~@/assets/icons1/未知.png" alt="">
                            </a-tooltip>

                        </div>
                        <div class="show_name_cell_right">
                            <p :title="record.show_name" style="margin:0 0 0px 0">{{record.show_name}}</p>
                            <p :title="record.host_name" style="margin:0;font-size:12px;">{{record.host_name}}</p>
                        </div>
                    </div>
                </template>

                <span slot="tube_state" slot-scope="text,record">
                    <span v-if="record.control_type == 'SSH'">
                        <p style="margin: 0">
                            <a-tooltip placement="left" title="SSH">
                                <img src="~@/assets/icons/ssh.png" alt="" />
                            </a-tooltip>
                            <span v-if="text.ssh_state == 'SSH正常'" style="color: #52c41a">
                                <a-badge style="margin: 0 0 0 8px" status="success" />{{text.ssh_state.replace('SSH', '')}}
                            </span>
                            <span v-else-if="text.ssh_state == 'SSH异常'" style="color: #f5222d">
                                <a-badge style="margin: 0 0 0 8px" status="error" />{{text.ssh_state.replace('SSH', '')}}
                            </span>
                            <span v-else style="color: #2db7f5">
                                <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />
                                {{text.ssh_state.replace('SSH', '')}}
                            </span>
                        </p>
                    </span>

                    <span v-if="record.control_type == 'Agent'">
                        <p style="margin: 0">
                            <a-tooltip placement="left" title="Agent">
                                <img src="~@/assets/icons/agent.png" alt="" />
                            </a-tooltip>
                            <span v-if="text.agent_state == 'Agent正常'" style="color: #52c41a">
                                <a-badge style="margin: 0 0 0 8px" status="success" />
                                {{text.agent_state.replace('Agent', '') }}
                            </span>
                            <span v-else-if="text.agent_state == 'Agent异常'" style="color: #f5222d">
                                <a-badge style="margin: 0 0 0 8px" status="error" />
                                {{text.agent_state.replace('Agent', '')}}
                            </span>
                            <span v-else style="color: #2db7f5">
                                <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />
                                {{text.agent_state.replace('Agent', '')}}
                            </span>
                        </p>
                    </span>

                    <span v-if="record.control_type == 'SSH/Agent'">
                        <p style="margin: 0">
                            <span>
                                <a-tooltip placement="left" title="SSH">
                                    <img src="~@/assets/icons/ssh.png" alt="" />
                                </a-tooltip>
                                <span v-if="text.ssh_state == 'SSH正常'" style="color: #52c41a">
                                    <a-badge style="margin: 0 0 0 8px" status="success" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                                <span v-else-if="text.ssh_state == 'SSH异常'" style="color: #f5222d">
                                    <a-badge style="margin: 0 0 0 8px" status="error" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                                <span v-else style="color: #2db7f5">
                                    <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                            </span>
                        </p>
                        <p style="margin: 0">
                            <span>
                                <a-tooltip placement="left" title="Agent">
                                    <img src="~@/assets/icons/agent.png" alt="" />
                                </a-tooltip>
                                <span v-if="text.agent_state == 'Agent正常'" style="color: #52c41a">
                                    <a-badge style="margin: 0 0 0 8px" status="success" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                                <span v-else-if="text.agent_state == 'Agent异常'" style="color: #f5222d">
                                    <a-badge style="margin: 0 0 0 8px" status="error" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                                <span v-else style="color: #2db7f5">
                                    <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                            </span>
                        </p>
                    </span>

                    <span v-if="record.control_type == 'Agent/SSH'">
                        <p style="margin: 0">
                            <span>
                                <a-tooltip placement="left" title="Agent">
                                    <img src="~@/assets/icons/agent.png" alt="" />
                                </a-tooltip>
                                <span v-if="text.agent_state == 'Agent正常'" style="color: #52c41a">
                                    <a-badge style="margin: 0 0 0 8px" status="success" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                                <span v-else-if="text.agent_state == 'Agent异常'" style="color: #f5222d">
                                    <a-badge style="margin: 0 0 0 8px" status="error" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                                <span v-else style="color: #2db7f5">
                                    <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />{{
                                        text.agent_state.replace('Agent', '')
                                    }}
                                </span>
                            </span>
                        </p>
                        <p style="margin: 0">
                            <span>
                                <a-tooltip placement="left" title="SSH">
                                    <img src="~@/assets/icons/ssh.png" alt="" />
                                </a-tooltip>
                                <span v-if="text.ssh_state == 'SSH正常'" style="color: #52c41a">
                                    <a-badge style="margin: 0 0 0 8px" status="success" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                                <span v-else-if="text.ssh_state == 'SSH异常'" style="color: #f5222d">
                                    <a-badge style="margin: 0 0 0 8px" status="error" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                                <span v-else style="color: #2db7f5">
                                    <a-badge style="margin: 0 0 0 8px" color="#2db7f5" />{{
                                        text.ssh_state.replace('SSH', '')
                                    }}
                                </span>
                            </span>
                        </p>
                    </span>
                </span>
            </a-table>
            <a-button v-if="tableData.length" class="all_check_btn" @click="handleAllCheck">批量全选</a-button>
        </div>
    </div>
</template>
<script>
import getinstApi from '@/api/getInst.js'
export default {
    data() {
        return {
            tableData: [],
            columns: [
                {
                    title: '名称/唯一标识',
                    dataIndex: 'show_name',
                    scopedSlots: { customRender: 'show_name' },
                    width: "280px",
                },
                {
                    title: 'IP地址',
                    dataIndex: 'ip',
                    width: '150px',
                },
                {
                    title: "所属分组",
                    dataIndex: "group",
                },
                { title: '纳管状态', dataIndex: 'tube_state', scopedSlots: { customRender: 'tube_state' } },
            ],
            countData: {},
            selectedRows: [],
            selectedRowKeys: [],
            current: 1,
            pageSize: 10,
            tableLoading: false,
            system_type_list: [
                { key: 'all', name: '全部系统' },
                { key: 'Linux', name: 'Linux' },
                { key: 'Windows', name: 'Windows' },
            ],
            tableQuery: {
                system_type: 'all',
                group_type: undefined,
                search_data: undefined,
                search_type: 'show_name',
            },
            searchList: [
                { name: '名称', key: 'show_name' },
                { name: 'IP地址', key: 'ip' },
            ],
            treeData: [
                {
                    key: "all",
                    title: "全部主机",
                    scopedSlots: { title: "action" },
                    count: 0,
                    self_count: 0,
                    children: []
                }
            ],
            showTree: false,
            selectedKeys: ["all"],
            allHostList: [],
        }
    },
    methods: {
        changeTableQuery() {
            this.current = 1
            this.getTableData()
        },
        // 选中分组(树)
        treeSelect(val) {
            this.selectedKeys = val
            this.tableQuery.group_type = val[0]
            this.getTableData()
        },
        getTableData(first) {
            this.tableLoading = true
            getinstApi
                .getList({
                    code: 'all',
                    ...this.tableQuery,
                })
                .then((res) => {
                    if (res.data.result === false) return
                    if (first) {
                        this.allHostList = res.data[0].agent_info
                    }
                    this.countData = res.data[0]
                    res.data[0].agent_info.map(item => {
                        item.tube_state = {}
                        if (item.agent_state) {
                            item.tube_state.agent_state = item.agent_state.state
                        }
                        if (item.ssh_state) {
                            item.tube_state.ssh_state = item.ssh_state.state
                        }
                        item.control_type = item.control_type.state
                    })
                    this.tableData = res.data[0].agent_info || []

                })
                .finally(() => {
                    this.tableLoading = false
                })
        },
        getGroupList() {
            //...
            this.axios({
                url: 'host-inst-group/',
                method: 'get',
            }).then((res) => {
                if (res.code == 200 && res.data) {
                    this.treeData[0].children = res.data
                    res.data.map(item => {
                        this.treeData[0].count += item.count
                    })
                    this.treeData[0].self_count = this.treeData[0].count
                    treeFn(res.data)
                    function treeFn(data) {
                        data.map(item => {
                            item.title = item.name
                            item.key = item.code
                            item.scopedSlots = { title: "action" }
                            if (item.children && item.children.length > 0) {
                                treeFn(item.children)
                            }
                        })
                    }
                    this.showTree = false
                    this.$nextTick(() => {
                        this.showTree = true
                    })
                }
            })
        },
        //选中取消表格事件
        onSelectChange(selectedRowKeys, selectedRows) {
            let arr = []
            selectedRowKeys.map(code => {
                let host = this.allHostList.find(item => {
                    return item.host_name == code
                })
                if (host) {
                    arr.push(host)
                }
            })
            this.selectedRows = arr
            this.selectedRowKeys = selectedRowKeys
        },
        tableChange({ current, pageSize }) {
            this.pageSize = pageSize
            this.current = current
        },
        handleAllCheck() {
            this.selectedRows = this.selectedRows.length == this.tableData.length ? [] : this.tableData
            this.selectedRowKeys =
                this.selectedRowKeys.length == this.tableData.length ? [] : this.tableData.map((item) => item.host_name)
        },
    },
    mounted() {
        this.tableQuery = this.$options.data().tableQuery
        this.getTableData(true)
        this.getGroupList()
    },
}
</script>
<style scoped lang='less'>
.title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.all_check_btn {
    display: block;
    margin: -50px 0 0 0;
}

.content_main {
    display: flex;
}
.content_main_left {
    flex: 0 0 260px;
    border-right: 1px solid #e8e8e8;
    min-width: 200px;
    .treetitle {
        width: 100%;
        display: inline-block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    /deep/.ant-tree-node-content-wrapper {
        max-width: calc(100% - 50px);
    }
}
.content_main_right {
    flex: 1325 1325 0;
    padding: 0 0 0px 20px;
    overflow: hidden;
}
.show_name_cell {
    display: flex;
    align-items: center;
}
.show_name_cell_left {
    flex: 0 0 30px;
    img {
        width: 20px;
        height: 20px;
        margin: 0 20px 0 0;
    }
}
.show_name_cell_right {
    flex: 20 20 240px;
    p {
        max-width: 240px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
}
</style>
