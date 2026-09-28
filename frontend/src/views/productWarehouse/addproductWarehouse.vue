<template>
    <div class="addproductWarehouse_main">
        <content-header :parent-title="language.parentTitle" :sub-title="$route.query.name?language.subTitle1:language.subTitle2"> </content-header>
        <a-form style="margin:20px 0 0 0" :form="addproductWarehouseForm" :label-col="{ span: 5 }" :wrapper-col="{ span: 15 }">
            <a-form-item :label="language.label11">
                <a-radio-group @change="innerChange" v-decorator="['inner', { rules: [{ required: true, message: language.placeholder1 }] }]">
                    <a-radio :value="true">{{language.selectOption1}}</a-radio>
                    <a-radio :value="false">{{language.selectOption2}}</a-radio>
                </a-radio-group>
                <a-tooltip placement="topLeft">
                    <template slot="title">
                        <span>{{language.tooltipTitle}}</span>
                    </template>
                    <a-icon type="info-circle" />
                </a-tooltip>
            </a-form-item>
            <template v-if="!$route.query.name">
                <a-form-item :label="language.label12">
                    <div class="cells" v-decorator="['repository_type', { rules: [{ required: true, message: language.placeholder2 }] }]">
                        <div @click="repositoryTypeChange(0,'raw')" :class="{cell:true, active:repositoryTypeIndex==0}">
                            <img src="@/assets/image/repository_type_raw.png" alt="">
                            <p>Raw</p>
                        </div>
                        <div @click="repositoryTypeChange(1,'docker')" :class="{cell:true, active:repositoryTypeIndex==1}">
                            <img src="@/assets/image/repository_type_docker.png" alt="">
                            <p>Docker</p>
                        </div>
                        <div @click="repositoryTypeChange(2,'maven2')" :class="{cell:true, active:repositoryTypeIndex==2}">
                            <img src="@/assets/image/repository_type_maven.png" alt="">
                            <p>Maven</p>
                        </div>
                        <div @click="repositoryTypeChange(3,'pypi')" :class="{cell:true, active:repositoryTypeIndex==3}">
                            <img src="@/assets/image/repository_type_pypi.png" alt="">
                            <p>PyPI</p>
                        </div>
                    </div>
                </a-form-item>
                <a-form-item :label="language.label13">
                    <a-input :placeholder="language.placeholder3" v-decorator="['repository_id', { rules: [{ required: true,pattern:/^[0-9a-zA-Z-_]{1,}$/, message: language.placeholder3 }] }]" :addon-before="baseWarehouseUrl">
                        <a-input slot="addonBefore"></a-input>
                    </a-input>
                </a-form-item>
                <a-form-item v-if="isDocker" :label="language.label14">
                    <a-input :placeholder="language.placeholder4" v-decorator="['httpPort', { rules: [{ required: true, message: language.placeholder4 }] }]"></a-input>
                </a-form-item>
            </template>
            <a-form-item :label="language.label15">
                <a-textarea :placeholder="language.placeholder5" v-decorator="['describe', { rules: [{ required: false,max:100, message: language.placeholder5 }] }]" :rows="5"></a-textarea>
            </a-form-item>

        </a-form>
        <div class="footer">
            <a-button :loading="btnLoading" @click="handleok" type="primary" style="margin:0 20.83% 0 10px">{{language.ok}}</a-button>
            <a-button @click="handlecancel" style="margin:0 10px 0 10px">{{language.cancel}}</a-button>
            <div style="height:30px;border-right:1px solid #ddd;margin:0 20px 0 20px"></div>
            <a class="delete" v-if="$store.state.btnAuth.btnAuth&&$route.query.name" @click="deleteproductWarehouse">{{language.deleteproductWarehouse}}</a>
        </div>
    </div>
</template>

<script>
import { getFormatType, addproductWarehouse, editproductWarehouse, getProductInformation, deleteproductWarehouse } from "@/api/productWarehouse"
import storage from 'store'
export default {
    data() {
        return {
            addproductWarehouseForm: this.$form.createForm(this, { name: 'addproductWarehouseForm' }),
            // 制品库种类选项
            repositoryTypeList: [],
            // 
            isDocker: false,
            // 选中制品库的index
            repositoryTypeIndex: -1,
            // 基础仓库地址
            baseWarehouseUrl: "",
            baseUrl1: "",
            baseUrl2: "",
            btnLoading: false
        }
    },
    created() {
        this.appCode = storage.get('__applicationInfo').code
        this.language = Object.assign({}, this.$store.state.language.languageAuth.public1 || {}, this.$store.state.language.languageAuth.productWarehouse || {} )
    },
    mounted() {
        this.getFormatType()
        if (this.$route.query && this.$route.query.name) {
            this.getProductInformation()
        } else {
            this.addproductWarehouseForm.setFieldsValue({ inner: true })
            this.baseUrl2 = storage.get("__applicationInfo").name + "-"
        }

    },
    methods: {
        // 提交
        handleok() {
            this.addproductWarehouseForm.validateFields((err, values) => {
                if (!err) {
                    this.btnLoading = true
                    if (this.$route.query && this.$route.query.name) {
                        let updata = {
                            code: this.appCode,
                            inner: values.inner,
                            describe: values.describe,
                            repository_id: this.$route.query.name,
                        }
                        editproductWarehouse(updata).then(res => {
                            if (res.code == 200) {
                                this.$message.success(res.message)
                                this.$router.go(-1)
                            } else {
                                this.$message.error(res.message)
                            }
                        }).finally(res => {
                            console.log(res)
                            this.btnLoading = false
                        })

                    } else {
                        let updata = {
                            code: this.appCode,
                            inner: values.inner,
                            repository_type: values.repository_type,
                            repository_id: (values.inner == true ? storage.get('__applicationInfo').name + "-" : "") + values.repository_id,
                            describe: values.describe,
                        }

                        if (values.httpPort) {
                            updata.parameters = {
                                httpPort: values.httpPort - 0
                            }
                        }
                        addproductWarehouse(updata).then(res => {
                            if (res.code == 200) {
                                this.$message.success(res.message)
                                this.$router.go(-1)
                            } else {
                                this.$message.error(res.message)
                            }
                        }).finally(res => {
                            this.btnLoading = false
                        })
                    }

                }
            })
        },
        handlecancel() {
            this.$router.go(-1)
        },
        getProductInformation() {
            getProductInformation({ repository_id: this.$route.query.name, code: storage.get('__applicationInfo').code }).then(res => {
                if (res.code == 200 && res.data) {
                    this.addproductWarehouseForm.setFieldsValue({ inner: res.data.is_app == true, describe: res.data.describe })
                }
            })
        },
        // 获取制品库类型
        getFormatType() {
            getFormatType().then(res => {
                if (res.code == 200 && res.data) {
                    this.repositoryTypeList = res.data
                }
            }).then(() => {
                // 如果是新建进行初始化
                if (!this.$route.query.name) {
                    this.repositoryTypeIndex = 0
                    this.addproductWarehouseForm.setFieldsValue({ repository_type: "raw" })
                    this.baseUrl1 = this.repositoryTypeList.filter(item => {
                        return item.format_name == "raw"
                    })[0].url
                    this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2
                }
            })
        },
        // 选择制品库类型
        repositoryTypeChange(index, value) {
            this.repositoryTypeIndex = index
            this.addproductWarehouseForm.setFieldsValue({ repository_type: value })

            this.baseUrl1 = this.repositoryTypeList.filter(item => {
                return item.format_name == value
            })[0].url
            this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2
            if (value == "docker") {
                this.isDocker = true
            } else {
                this.isDocker = false
            }

        },
        // 选择应用内外
        innerChange(e) {
            // console.log(e.target.value)
            if (e.target.value == true) {
                this.baseUrl2 = storage.get('__applicationInfo').name + "-"
            } else {
                this.baseUrl2 = ""
            }
            this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2
        },
        // 删除
        deleteproductWarehouse() {
            let _this = this
            this.$warning({
                title: "确认要删除吗？删除后当前仓库地址和其下所有制品都会被删除且不可恢复！",
                onOk() {
                    deleteproductWarehouse({ repository_id: _this.$route.query.name, code: _this.appCode, }).then(res => {
                        if (res.code == 200) {
                            _this.$message.success(res.message)
                            _this.$router.go(-1)
                        } else {
                            _this.$message.error(res.message)
                        }
                    })
                }
            })

        }
    }
}
</script>

<style lang="less" scoped>
.addproductWarehouse_main {
    // height:calc(100vh - 180px);
    background: #fff;
    .cells {
        display: flex;
        .cell {
            border: 1px solid #ccc;
            width: 108px;
            height: 108px;
            cursor: pointer;
            margin: 0 10px 0 0;
            &:hover {
                border-color: blue;
            }
            img {
                width: 58px;
                height: 58px;
                margin: 15px 0 0 25px;
            }
            p {
                font-size: 16px;
                font-weight: 1000;
                line-height: 20px;
                text-align: center;
            }
        }
        .active {
            border: 1px solid blue;
            position: relative;
            border-radius: 3px;
            &:after {
                content: '';
                display: inline-block;
                width: 30px;
                height: 30px;
                background: url('~@/assets/image/check.png');
                background-size: 30px;
                position: absolute;
                top: -1px;
                right: -1px;
            }
        }
    }

    .footer {
        height: 60px;
        padding: 0 0 20px 0;
        display: flex;
        flex-direction: row-reverse;
        align-items: center;
        .delete{
            margin:0 0 0 0;color:#888
        }
        .delete:hover{
            color:#333;
        }
    }
}
</style>