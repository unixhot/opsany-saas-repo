<template>
    <div>
        <content-header :parent-title="language.parentTitle">
            <div slot="docs">支持对接Nexus，进行制品库的管理。</div>
        </content-header>
        <a-card>
            <a-spin :spinning="spinning">
                <div class="empty_box" v-if="tableData.length == 0 && isOver">
                    <a-empty style="width:200px;" />
                    <div class="right">
                        <h3>工具配置</h3>
                        <p style="width:400px;">
                            应用制品仓库工具管理，兼容Nexus进行多语言制品仓库管理。
                        </p>
                        <a-button v-if="$store.state.btnAuth.btnAuth.repo_tool_create" @click="
                            toolModel = true
                            toolTitle = language.addTools
                        " icon="plus" type="primary" style="border-radius: 2px">{{ language.addTools }}</a-button>
                    </div>
                </div>
                <div v-else>
                    <a-table :columns="columns" :data-source="tableData" :loading="tableLoading" :rowKey="
                    (record, index) => {
                        return index
                    }
                ">
                        <span slot="tool_type" slot-scope="text">
                            <img style="margin:0 10px 0 0" width="24px" src="~@/assets/image/Nexus.png" alt="">
                            Nexus
                        </span>
                        <span slot="description" slot-scope="text">
                            <span>{{ text || '--' }}</span>
                        </span>
                        <span slot="link_status" slot-scope="text">
                            <span v-if="text == '正常'" style="color: #0c6">
                                <a-icon style="margin:0 10px 0 0" type="check-circle" theme="filled" />{{ language.normal }}
                            </span>
                            <span v-else style="color: red">
                                <a-icon style="margin:0 10px 0 0" type="close-circle" theme="filled" />{{ language.abnormal }}
                            </span>
                        </span>
                        <span slot="action" slot-scope="record">
                            <span v-if="
                            !$store.state.btnAuth.btnAuth.repo_tool_update &&
                            !$store.state.btnAuth.btnAuth.repo_tool_delete
                        ">--</span>
                            <a-button v-if="$store.state.btnAuth.btnAuth.repo_tool_update" type="link" style="color: @primary-color" @click="toolEdit(record)">{{ language.edit }}</a-button>
                            <a-button v-if="$store.state.btnAuth.btnAuth.repo_tool_delete" type="link" @click="toolDelect(record)">{{ language.delete }}</a-button>
                        </span>
                    </a-table>
                </div>
            </a-spin>

            <!-- 新增或修改工具弹框 -->
            <a-modal width="900px" :destroyOnClose="true" v-model="toolModel" :confirmLoading="okBtnLoading" @ok="toolHandelOK" @cancel="toolCancel">
                <h3 class="title_h3" style="margin: 0" slot="title">
                    <span>{{ toolTitle }}</span>
                </h3>
                <a-form :form="toolForm">

                    <a-form-item :label="language.label1" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-input :placeholder="language.placeholder1" v-decorator="[
                                    'tool_name',
                                    { rules: [{ required: true, message: language.placeholder1 }] },
                                ]">
                        </a-input>
                    </a-form-item>

                    <a-form-item :label="language.label2" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-radio-group :placeholder="language.placeholder2" v-decorator="[
                                    'tool_type',
                                    { initialValue:'repository',rules: [{ required: true, message: language.placeholder2, }] },
                                ]" optionFilterProp="label" showSearch>
                            <a-radio value="repository">
                                <img style="margin:0 10px 0 0" width="24px" src="~@/assets/image/Nexus.png" alt="">Nexus
                            </a-radio>
                        </a-radio-group>
                    </a-form-item>

                    <a-form-item :label="language.label3" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-input :placeholder="language.placeholder3" v-decorator="['api_addr', { rules: [{ required: true, message: language.placeholder3 }] }]"></a-input>
                    </a-form-item>
                    <a-form-item :label="language.label4" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-input :placeholder="language.placeholder4" v-decorator="['username', { rules: [{ required: true, message: language.placeholder4 }] }]"></a-input>
                    </a-form-item>

                    <a-form-item :label="passwordLabel" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-input-password autocomplete="new-password" :placeholder="language.placeholder5 + passwordLabel" v-decorator="[
                            'api_token',
                            { rules: [{ required: true, message: language.placeholder5 + passwordLabel }] },
                        ]"></a-input-password>
                    </a-form-item>
                    <a-form-item :label="language.label6" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
                        <a-textarea :placeholder="language.placeholder6" :auto-size="{ minRows: 6, maxRows: 6 }" v-decorator="['description', { rules: [{ required: false }] }]" />
                    </a-form-item>
                    <div style="display:flex">
                        <a-button @click="toolTest" :loading="btnLoading" style="margin:-5px 20px 0 106px;">连接测试</a-button>
                        <span v-if="textState == 1">
                            <a-icon style="color: #0ba360; margin: 0 3px 0 0px" theme="filled" type="check-circle" />
                            测试通过
                        </span>
                        <div v-else-if="textState == 2">
                            <a-icon style="color: red; margin: 4px 3px 0 0px" theme="filled" type="close-circle" />
                            <span style="color: red;">{{textMessage}}</span>
                            <a-tooltip :title="errorsMessage">
                                <a-icon style="margin:0 0 0 10px;" type="exclamation-circle" />
                            </a-tooltip>
                        </div>
                    </div>

                </a-form>
            </a-modal>
        </a-card>
    </div>
</template>

<script>
import { getTool, addTool, delTool, editTool, refreshState, toolTest } from '@/api/tool'
export default {
    data() {
        return {
            tableData: [],
            tableLoading: false,
            // 弹框是否显示
            toolModel: false,
            toolForm: this.$form.createForm(this, { name: 'toolForm' }),
            // 工具类型选项
            toolTypeList: [],
            // 弹框标题
            toolTitle: '',
            // 该工具的id，编辑提交时使用
            toolCode: '',
            // 刷新按钮loading
            refreshBtnLoading: false,
            // ok按钮loading
            okBtnLoading: false,
            // 已有工具类型
            hasToolTypeList: [],
            // 密码展示的label
            passwordLabel: '密码',
            spinning: false,
            isOver: false,
            btnLoading: false,
            textState: 0,
            errorsMessage: "",
            textMessage: "",
        }
    },
    computed: {
        columns() {
            return [
                {
                    title: "工具名称",
                    dataIndex: 'tool_name',
                },
                {
                    title: "工具",
                    dataIndex: 'tool_type',
                    scopedSlots: { customRender: 'tool_type' },
                },
                {
                    title: this.language.columns3,
                    dataIndex: 'api_addr',
                    key: 'api_addr',
                },
                {
                    title: this.language.columns4,
                    dataIndex: 'description',
                    key: 'description',
                    scopedSlots: { customRender: 'description' },
                    ellipsis: true,
                },
                {
                    title: this.language.columns5,
                    dataIndex: 'link_status',
                    key: 'link_status',
                    scopedSlots: { customRender: 'link_status' },
                },
                {
                    title: this.language.columns6,
                    key: 'action',
                    scopedSlots: { customRender: 'action' },
                    width: 200,
                    align: 'center',
                },
            ]
        },
    },
    created() {
        this.language = this.$store.state.language.languageAuth.toolsmanage || {}
    },
    mounted() {
        this.getToolData()
    },
    methods: {
        // 获取工具信息
        getToolData() {
            this.tableData = []
            this.hasToolTypeList = []
            this.tableLoading = true
            this.spinning = true
            this.isOver = false
            getTool().then((res) => {
                if (res.data && res.data.data) {
                    if (res.data.data.length == 0 && res.data.current > 1) {
                        this.tableQuery.current--
                        this.getTableData()
                        return
                    }
                    this.pagetion = {
                        total: res.data.total,
                        current: res.data.current,
                        pageSize: res.data.pageSize,
                    }
                    res.data.data.map((item) => {
                        let tool_type_name
                        if (item.tool_type == 'repository') {
                            tool_type_name = this.language.toolTypeList1
                        } else if (item.tool_type == 'git') {
                            tool_type_name = this.language.toolTypeList2
                        } else {
                            tool_type_name = this.language.toolTypeList3
                        }
                        this.hasToolTypeList.push(item.tool_type)
                        this.tableData.push({
                            key: item.code,
                            tool_name: item.tool_name,
                            tool_type: item.tool_type,
                            tool_type_name: tool_type_name,
                            username: item.username,
                            api_token: item.api_token,
                            api_addr: item.api_addr,
                            description: item.description,
                            link_status: item.link_status,
                        })
                    })
                }
            }).finally(() => {
                this.tableLoading = false
                this.spinning = false
                this.refreshBtnLoading = false
                this.isOver = true
            })
        },
        // 编辑
        toolEdit(record) {
            this.toolModel = true
            this.toolTitle = this.language.editTools
            this.toolCode = record.key
            this.$nextTick(function () {
                this.toolForm.setFieldsValue({
                    tool_name: record.tool_name,
                    tool_type: record.tool_type,
                    username: record.username,
                    api_token: record.api_token,
                    api_addr: record.api_addr,
                    description: record.description,
                })
            })
            if (record) {
                this.isEdit = true
            } else {
                this.isEdit = false

            }
        },
        //新增或修改提交
        toolHandelOK() {
            this.toolForm.validateFields((err, values) => {
                if (!err) {
                    this.okBtnLoading = true
                    let updata = { ...values }
                    if (!this.isEdit) {
                        addTool(updata)
                            .then((res) => {
                                if (res?.code == 200) {
                                    this.$message.success(res.message)
                                    this.toolCancel()
                                    this.getToolData()
                                }
                            })
                            .finally(() => {
                                this.okBtnLoading = false
                            })
                    } else {
                        updata.code = this.toolCode
                        editTool(updata)
                            .then((res) => {
                                if (res?.code == 200) {
                                    this.$message.success(res.message)
                                    this.toolCancel()
                                    this.getToolData()
                                }
                            })
                            .finally(() => {
                                this.okBtnLoading = false
                            })
                    }
                }
            })
        },
        // 弹框取消
        toolCancel() {
            this.textState = 0
            this.textMessage = ""
            this.errorsMessage = ""
            this.toolForm.resetFields()
            this.toolModel = false
        },
        // 删除工具
        toolDelect(record) {
            let _this = this
            this.$confirm({
                title: this.language.deleteMessage,
                okType: 'danger',
                onOk() {
                    return new Promise((resolve, reject) => {
                        delTool({ code: record.key }).then((res) => {
                            if (res.code == 200) {
                                _this.$message.success(res.message)
                                _this.getToolData()
                                resolve()
                            } else {
                                _this.$message.error(res.message)
                            }
                        }).finally(() => {
                            reject()
                        })
                    })
                },
            })
        },
        toolTest() {
            this.toolForm.validateFields((err, values) => {
                if (!err) {
                    this.btnLoading = true
                    let params = {
                        tool_url: values.api_addr,
                        tool_username: values.username,
                        tool_password: values.api_token,
                        code : this.toolCode,
                    }
                    toolTest(params).then(res => {
                        if (res.data?.data) {
                            this.textState = 1
                            this.$message.success(res.data.data)
                        }
                    }).catch(res => {
                        this.textState = 2
                        this.errorsMessage = res.errors
                        this.textMessage = res.message
                        // this.$message.error(res.errors)
                    }).finally(() => {
                        this.btnLoading = false
                    })
                }
            })
        }
    }
}
</script>

<style lang="less" scoped>
.empty_box {
    display: flex;
    justify-content: center;
    margin: 80px 0 80px 0;
}
</style>