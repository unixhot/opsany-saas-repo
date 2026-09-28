<template>
    <div class="content_main">
        <div class="content_main_left">
            <a-tree v-if="showTree" checkable checkStrictly @check="treeCheck" @select="treeSelect" :checkedKeys="treeCheckedKeys" :tree-data="treeData" :selectedKeys="treeSelectedKeys" defaultExpandAll :show-line="true">
                <template slot="action" slot-scope="row">
                    <span :title="row.title + ' ('+row.self_count+'/'+ row.count +')' " class="treetitle">{{ row.title }} ({{row.self_count}}/{{row.count}})</span>
                </template>
            </a-tree>
            <a-skeleton style="padding:10px;" v-else />
        </div>
        <div class="content_main_right">
            <a-table style="margin-top: 10px" :row-selection="{ selectedRowKeys, onChange: onSelectChange,getCheckboxProps:getCheckboxProps }" :columns="columns" :dataSource="tableData" :pagination="{
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
        </div>
    </div>
</template>
<script>
import getinstApi from '@/api/getInst.js'
import { getHostGroup } from "@/api/get-host-group-v2.js"
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
            // tree被选中的项
            selectedRows: [],
            // table选中行
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
                { name: '主机名称', key: 'show_name' },
                { name: 'IP地址', key: 'ip' },
            ],
            treeData: [
                {
                    key: "all",
                    title: "全部主机",
                    scopedSlots: { title: "action" },
                    count: 0,
                    code: "all",
                    self_count: 0,
                    children: []
                }
            ],
            showTree: false,
            // 分组树点击选中项
            treeSelectedKeys: ["all"],
            treeCheckedKeys: [],
        }
    },
    methods: {
        changeTableQuery() {
            this.current = 1
            this.selectedRows = []
            this.selectedRowKeys = []
            this.getTableData()
        },
        // 选中分组(树)
        treeSelect(val) {
            this.treeSelectedKeys = val
            this.tableQuery.group_type = val[0]
            this.getTableData()
        },
        getTableData() {
            this.tableLoading = true
            getinstApi
                .getList({
                    code: 'all',
                    ...this.tableQuery,
                    group_level: 'self',
                })
                .then((res) => {
                    if (res.data.result === false) return
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

                    let group_id = this.treeSelectedKeys[0]
                    let list = this.treeCheckedKeys.checked
                    let flag
                    if (list) {
                        flag = list.find((item) => {
                            return item == group_id
                        })
                        if (flag) {
                            let arr = []
                            this.tableData.map(item => {
                                arr.push(item.host_name)
                            })
                            this.selectedRowKeys = arr
                        } else {
                            this.selectedRowKeys = []
                        }
                    }
                })
                .finally(() => {
                    this.tableLoading = false
                })
        },
        getHostGroup() {
            getHostGroup().then((res) => {
                if (res.code == 200 && res.data) {
                    this.treeData[0].children = res.data
                    res.data.map(item => {
                        this.treeData[0].count += item.count
                    })
                    this.treeData[0].self_count = this.treeData[0].count
                    let arr = []
                    treeFn(res.data)
                    function treeFn(data) {
                        data.map(item => {
                            item.title = item.name
                            item.key = item.code
                            item.disabled = !item.auth
                            item.scopedSlots = { title: "action" }
                            let group = JSON.parse(JSON.stringify(item))
                            delete group.children
                            arr.push(group)
                            if (item.children && item.children.length > 0) {
                                treeFn(item.children)
                            }
                        })
                    }

                    this.allTreeRowList = arr
                    this.showTree = false
                    this.$nextTick(() => {
                        this.showTree = true
                    })
                }
            })
        },
        //选中取消表格事件
        onSelectChange(selectedRowKeys, selectedRows) {
            this.selectedRowKeys = selectedRowKeys
        },
        tableChange({ current, pageSize }) {
            this.pageSize = pageSize
            this.current = current
        },
        getCheckboxProps: record => ({
            props: {
                disabled: true
            },
        }),
        treeCheck(checkedKeys, e) {
            let _this = this
            if (e.node.eventKey == "all") {
                if (e.checked) {
                    // 全选
                    let arr = ['all'], arr1 = []
                    checkeAll(this.treeData[0].children, arr, arr1)
                    this.treeCheckedKeys = arr
                    this.selectedRows = arr1
                } else {
                    // 全取消
                    this.treeCheckedKeys = []
                    this.selectedRows = []
                }
            } else {
                this.treeCheckedKeys = checkedKeys
                let arr = []
                e.checkedNodes.map(item => {
                    arr.push(item.data.props)
                })
                this.selectedRows = arr
                if (this.treeSelectedKeys[0] == e.node.eventKey) {
                    this.getTableData()
                }
                // 判断是否选择了全部分组
                if (e.checked) {
                    let isall = []
                    isAll(this.treeData[0].children, isall)
                    if (isall.length == 0) {
                        this.treeCheckedKeys.checked.push("all")
                    }
                } else {
                    let index = this.treeCheckedKeys.checked.findIndex(item => {
                        return item == "all"
                    })
                    if (index > -1) {
                        this.treeCheckedKeys.checked.splice(index, 1)
                    }
                    let index1 = this.selectedRows.findIndex(item => {
                        return item.code == "all"
                    })
                    if (index1 > -1) {
                        this.selectedRows.splice(index1, 1)
                    }
                }
            }
            // 是否选中全部分组
            function isAll(data, isall) {
                data.map(item => {
                    let flag = _this.treeCheckedKeys.checked.find(ele => {
                        return ele == item.code
                    })
                    if (!flag) {
                        isall.push(1)
                    }
                    if (item.children && item.children.length > 0) {
                        isAll(item.children, isall)
                    }
                })
            }
            // 全选
            function checkeAll(data, arr, arr1) {
                data.map(item => {
                    let group = JSON.parse(JSON.stringify(item))
                    delete group.children
                    arr.push(group.code)
                    arr1.push(group)
                    if (item.children && item.children.length > 0) {
                        checkeAll(item.children, arr, arr1)
                    }
                })
            }
        }
    },
    mounted() {
        this.tableQuery = this.$options.data().tableQuery
        this.changeTableQuery()
        this.getHostGroup()
    },
    computed: {

    }
}
</script>
<style scoped lang='less'>
.title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.all_check_btn {
    margin: -50px 0 0 0;
    display: block;
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
