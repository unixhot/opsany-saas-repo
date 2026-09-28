<template>
    <a-modal width="860px" :maskClosable="false" title="主机列表" v-model="visible" @ok="handleOk">
        <a-table :columns="columns" :dataSource="tableData" bordered :rowKey="(item) => item.host_name" :loading="tableLoading">
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
    </a-modal>
</template>
<script>
import getinstApi from '@/api/getInst.js'
export default {
    data() {
        return {
            visible: false,
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
                    width: '280px',
                },
                { title: '纳管状态', dataIndex: 'tube_state', scopedSlots: { customRender: 'tube_state' } },
            ],
            tableLoading: false,
        }
    },
    methods: {
        showModal(group_id) {
            this.tableData = []
            this.getTableData(group_id)
            this.visible = true
        },
        getTableData(group_type) {
            this.tableLoading = true
            getinstApi.getList({ group_type ,group_level:"self"})
                .then((res) => {
                    this.tableData = res.data[0].agent_info
                    this.tableData.map(item => {
                        item.tube_state = {}
                        if (item.agent_state) {
                            item.tube_state.agent_state = item.agent_state.state
                        }
                        if (item.ssh_state) {
                            item.tube_state.ssh_state = item.ssh_state.state
                        }
                        item.control_type = item.control_type.state
                    })
                })
                .finally(() => {
                    this.tableLoading = false
                })
        },
        handleOk(e) {
            this.visible = false
        },
    },
}
</script>
<style scoped="scoped" lang="less" >
/deep/ .ant-table-thead > tr > th,
.ant-table-tbody > tr > td {
    padding: 8px;
}
/deep/ .ant-table-tbody > tr > td {
    padding: 8px;
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
        min-width: 240px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
}
</style>