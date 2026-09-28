<template>
	<div>
		<a-drawer
			:bodyStyle="{ padding: '24px 24px 64px 24px' }"
			width="800px"
			:title="drawerTitle"
			placement="right"
			:visible="visible"
			@close="onClose"
		>
			<a-spin :spinning="spinning" tip="正在加载中，请耐心等待...">
				<a-form style="margin:20px 0 0 0" :form="addproductWarehouseForm" :label-col="{ span: 3 }" :wrapper-col="{ span: 20 }">
					<a-form-item :label="language.label11">
						<a-radio-group @change="innerChange" v-decorator="['inner', { rules: [{ required: true, message: language.placeholder1 }] }]">
							<a-tooltip placement="topLeft" title="只能在当前应用系统内访问" arrow-point-at-center>
								<a-radio :value="true">
									{{ language.selectOption1 }}
								</a-radio>
							</a-tooltip>
							<a-tooltip placement="topLeft" title="所有应用均可访问" arrow-point-at-center>
								<a-radio :value="false">{{ language.selectOption2 }}</a-radio>
							</a-tooltip>
						</a-radio-group>
					</a-form-item>
					<template v-if="!isEdit">
						<a-form-item class="special" :label="language.label12">
							<div class="cells" v-decorator="['repository_type', { rules: [{ required: true, message: language.placeholder2 }] }]">
								<div @click="repositoryTypeChange(0, 'raw')" :class="{ cell: true, active: repositoryTypeIndex == 0 }">
									<img src="@/assets/image/repository_type_raw.png" alt="" />
									<p>Raw</p>
								</div>
								<div @click="repositoryTypeChange(1, 'docker')" :class="{ cell: true, active: repositoryTypeIndex == 1 }">
									<img src="@/assets/image/repository_type_docker.png" alt="" />
									<p>Docker</p>
								</div>
								<div @click="repositoryTypeChange(2, 'maven2')" :class="{ cell: true, active: repositoryTypeIndex == 2 }">
									<img src="@/assets/image/repository_type_maven.png" alt="" />
									<p>Maven</p>
								</div>
								<div @click="repositoryTypeChange(3, 'pypi')" :class="{ cell: true, active: repositoryTypeIndex == 3 }">
									<img src="@/assets/image/repository_type_pypi.png" alt="" />
									<p>PyPI</p>
								</div>
								<div @click="repositoryTypeChange(4, 'helm')" :class="{ cell: true, active: repositoryTypeIndex == 4 }">
									<img src="@/assets/image/repository_type_helm.png" alt="" />
									<p>Helm</p>
								</div>
							</div>
						</a-form-item>
						<div v-if="addproductWarehouseForm.getFieldValue('repository_type') === 'docker'">
							<a-form-item label="仓库类型">
								<a-radio-group v-decorator="['docker_type', { rules: [{ required: true, message: '请选择仓库类型' }] }]">
									<a-radio value="hosted">hosted</a-radio>
									<a-radio value="proxy">proxy</a-radio>
								</a-radio-group>
							</a-form-item>
							<a-form-item v-if="addproductWarehouseForm.getFieldValue('docker_type') === 'proxy'" label="Harbor地址">
								<a-input
									placeholder="请输入Harbor地址"
									v-decorator="[
										'remoteUrl',
										{
											rules: [
												{ required: true, message: '请输入Harbor地址' },
											],
										},
									]"
								/>
							</a-form-item>
						</div>
						<a-form-item label="所属应用">
							<a-tree-select
								:dropdownStyle="{ width: '420px' }"
								treeNodeFilterProp="title"
								v-decorator="['code', { rules: [{ required: true, message: '请选择所属应用' }] }]"
								showSearch
								:treeData="treeData"
								style="width: 530px"
								placeholder="请选择所属应用"
								tree-default-expand-all
								@change="treeChange"
							>
							</a-tree-select>
							<span style="position: absolute; right: -90px">
								<a-button icon="redo" type="link" :loading="btnLoading2" @click="getBusinessTreeData"></a-button>
								<a target="_blank" :href="otherAppUrl + 'devops/#/configure/application'">创建应用</a>
							</span>
						</a-form-item>
						<a-form-item :label="language.label13">
							<a-input
								:placeholder="language.placeholder3"
								v-decorator="[
									'repository_id',
									{ rules: [{ required: true, pattern: /^[0-9a-zA-Z-_]{1,}$/, message: language.placeholder3 }] },
								]"
								:addon-before="baseWarehouseUrl"
							>
								<a-input slot="addonBefore"></a-input>
							</a-input>
						</a-form-item>
						<a-form-item v-if="addproductWarehouseForm.getFieldValue('repository_type') === 'docker'" :label="language.label14">
							<a-input
								:placeholder="language.placeholder4"
								v-decorator="['httpPort', { initialValue: 8015, rules: [{ required: true, message: language.placeholder4 }] }]"
							></a-input>
						</a-form-item>
					</template>
					<a-form-item :label="language.label15">
						<a-textarea
							:placeholder="language.placeholder5"
							v-decorator="['describe', { rules: [{ required: false, max: 100, message: language.placeholder5 }] }]"
							:rows="5"
						></a-textarea>
					</a-form-item>
					<a-form-item v-if="(!isEdit && (addproductWarehouseForm.getFieldValue('repository_type') != 'docker' ||
						addproductWarehouseForm.getFieldValue('docker_type') != 'proxy')) || (isEdit && activeObj.type == 'hosted' && activeObj.writePolicy)" 
						:label="language.label16">
						<a-select :placeholder="language.placeholder6" v-decorator="['writePolicy', { rules: [{ required: true, message: language.placeholder6 }] }]">
							<a-select-option value="ALLOW">允许重新部署 (Allow redeploy)</a-select-option>
							<a-select-option value="ALLOW_ONCE">禁用重新部署 (Disable redeploy)</a-select-option>
							<a-select-option value="DENY">只读 (Read-only)</a-select-option>
							<a-select-option value="REPLICATION_ONLY">仅通过复制进行部署 (Deploy by Replication Only)</a-select-option>
						</a-select>
					</a-form-item>
				</a-form>
			</a-spin>
			<div class="footer">
				<a-button :loading="btnLoading" @click="handleok" type="primary" style="float:right">{{ language.ok }}</a-button>
				<a-button @click="onClose" style="margin:0 10px 0 10px;float:right">{{ language.cancel }}</a-button>
				<span v-if="isEdit">
					<a v-if="activeObj.can_delete" class="delete" @click="deleteproductWarehouse" style="float:right;margin:6px 20px 0 0">{{
						language.deleteproductWarehouse
					}}</a>
					<a-tooltip v-else title="无操作权限">
						<a-button class="delete" type="link" size="small" disabled style="float:right;margin:6px 20px 0 0">{{
							language.deleteproductWarehouse
						}}</a-button>
					</a-tooltip>
				</span>
			</div>
		</a-drawer>
		<a-modal v-model="deleteModel" @cancel="onCancel" @ok="onDeleteOk" :confirmLoading="deleteLoading">
			<h3 style="font-size: 18px">
				<a-icon style="color: red" type="exclamation-circle" /> <span>{{ language.deleteMessage1 }}</span>
			</h3>
			<p>{{ language.deleteMessage2 }}【{{ activeObj.name }}】？</p>
			<a-form-item :label="language.deleteMessage3">
				<a-input :placeholder="language.deleteMessage3" v-model="delete_name"></a-input>
			</a-form-item>
		</a-modal>
	</div>
</template>

<script>
// 编辑时接口的writePolicy为null则writePolicy不展示  （type为proxy）
import { getFormatType, addproductWarehouse, editproductWarehouse, getProductInformation, deleteproductWarehouse } from "@/api/productWarehouse";
import { getBusinessTree } from "@/api/business.js";
export default {
	data() {
		return {
			visible: false,
			drawerTitle: "新建制品库",
			addproductWarehouseForm: this.$form.createForm(this, { name: "addproductWarehouseForm" }),
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
			btnLoading: false,
			appCode: 0,
			// 选中的应用名称
			selectApplication: "",
			treeData: [],
			otherAppUrl: window.API_ROOT.replace("/repo", ""),
			spinning: false,
			isEdit: false,
			activeObj: {}, //所编辑的制品库
			btnLoading2: false,

			deleteModel: false,
			delete_name: "",
			deleteLoading: false,
		};
	},
	created() {
		this.language = Object.assign(
			{},
			this.$store.state.language.languageAuth.public1 || {},
			this.$store.state.language.languageAuth.productWarehouse || {}
		);
	},
	methods: {
		onClose() {
			this.visible = false;
			this.addproductWarehouseForm.resetFields();
			this.repositoryTypeIndex = -1;
		},
		onShow(appCode, record) {
			this.appCode = appCode;
			this.visible = true;
			this.spinning = true;
			if (record) {
				this.isEdit = true;
				this.activeObj = record;
				this.drawerTitle = "编辑制品库";
				this.getProductInformation(record);
			} else {
				this.getBusinessTreeData(true).then(() => this.getFormatType());
				this.isEdit = false;
				this.drawerTitle = "新建制品库";
				this.$nextTick(() => {
					this.addproductWarehouseForm.setFieldsValue({ inner: true, writePolicy: "ALLOW", });
				});
				if (appCode) {
					this.$nextTick(() => {
						this.addproductWarehouseForm.setFieldsValue({ code: appCode });
					});
				}
			}
		},
		getProductInformation(record) {
			getProductInformation({ repository_id: record.name, code: this.appCode, repository_type: record.format })
				.then(res => {
					if (res.code == 200 && res.data) {
						this.activeObj.httpPort = res.data.httpPort
						this.activeObj.writePolicy = res.data.writePolicy
						setTimeout(() =>{
							this.addproductWarehouseForm.setFieldsValue({ inner: res.data.is_app == true, describe: res.data.describe, writePolicy: res.data.writePolicy });
						},10)
					}
				})
				.finally(() => {
					this.spinning = false;
				});
		},
		// 选择应用内外
		innerChange(e) {
			if (e.target.value == true) {
				this.baseUrl2 = this.selectApplication + "-";
			} else {
				this.baseUrl2 = "";
			}
			this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2;
		},
		// 提交
		handleok() {
			this.addproductWarehouseForm.validateFields((err, values) => {
				if (!err) {
					if (this.isEdit) {
						let updata = {
							code: this.appCode,
							inner: values.inner,
							describe: values.describe,
							repository_id: this.activeObj.name,
							writePolicy: values.writePolicy,
							format: this.activeObj.format,
							type: this.activeObj.type,
							httpPort: this.activeObj.httpPort,  //只有docker类型有
						};
						this.btnLoading = true;
						editproductWarehouse(updata)
							.then(res => {
								if (res.code == 200) {
									this.$message.success(res.message);
									this.onClose();
									this.$emit("ref-list", "reload");
								} else {
									this.$message.error(res.message);
								}
							})
							.finally(res => {
								this.btnLoading = false;
							});
					} else {
						let updata = {
							code: this.appCode,
							inner: values.inner,
							repository_type: values.repository_type,
							repository_id: (values.inner == true ? this.selectApplication + "-" : "") + values.repository_id,
							describe: values.describe,
							writePolicy: values.writePolicy,
						};
						if (values.repository_type == "docker") {
							let arr = (this.baseWarehouseUrl + values.repository_id).split(":");
							let docker_user_url;
							if (arr.length == 3) {
								// 有端口的情况
								let arr2 = arr[2].split("/");
								arr2[0] = values.httpPort - 0;
								docker_user_url = arr[0] + ":" + arr[1] + ":" + arr2.join("/");
							} else if (arr.length == 2) {
								// 没有端口的情况
								let arr1 = (this.baseWarehouseUrl + values.repository_id).split("/");
								arr1[2] += ":" + values.httpPort;
								docker_user_url = arr1.join("/");
							}
							updata.docker_user_url = docker_user_url;
						}

						if (values.httpPort) {
							updata.parameters = {
								httpPort: values.httpPort - 0,
							};
						}
						if (values.repository_type == "docker" && values.docker_type == "proxy") {
							updata.parameters.remoteUrl = values.remoteUrl;
							updata.proxy_docker = true;
						}
						this.btnLoading = true;
						addproductWarehouse(updata)
							.then(res => {
								if (res.code == 200) {
									this.$message.success(res.message);
									this.onClose();
									this.$emit("ref-list", "reload");
								} else {
									this.$message.error(res.message);
								}
							})
							.finally(res => {
								this.btnLoading = false;
							});
					}
				}
			});
		},
		// 选择制品库类型
		repositoryTypeChange(index, value) {
			this.repositoryTypeIndex = index;
			this.addproductWarehouseForm.setFieldsValue({ repository_type: value });

			this.baseUrl1 = this.repositoryTypeList.filter(item => {
				return item.format_name == value;
			})[0].url;
			this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2;
			if (value == "docker") {
				this.isDocker = true;
				this.$nextTick(() => {
					this.addproductWarehouseForm.setFieldsValue({ docker_type: "hosted" });
				});
			} else {
				this.isDocker = false;
			}
		},
		// 获取制品库类型
		getFormatType() {
			this.spinning = true;
			getFormatType()
				.then(res => {
					if (res.code == 200 && res.data) {
						this.repositoryTypeList = res.data;
					}
				})
				.then(() => {
					// 如果是新建进行初始化
					if (!this.$route.query.name) {
						this.repositoryTypeIndex = 0;
						this.addproductWarehouseForm.setFieldsValue({ repository_type: "raw" });
						this.isDocker = false;
						this.baseUrl1 = this.repositoryTypeList.filter(item => {
							return item.format_name == "raw";
						})[0].url;
						this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2;
					}
				})
				.finally(() => {
					this.spinning = false;
				});
		},
		// 获取业务与应用
		getBusinessTreeData(first) {
			this.btnLoading2 = true;
			return getBusinessTree()
				.then(res => {
					if (res.data) {
						this.treeData = res.data;
						this.treeData = res.data.filter(item => {
							return item.children && item.children.length > 0;
						});
						this.treeData.map(item => {
							item.key = "n" + item.code;
							item.value = "n" + item.code;
							item.title = item.name;
							item.disabled = true;
							item.children.map(ele => {
								ele.key = ele.code + "";
								ele.value = ele.code + "";
								ele.title = ele.name;
								if (first && this.appCode && this.appCode == ele.code) {
									this.selectApplication = ele.unique_code;
									this.baseUrl2 = this.selectApplication + "-";
									this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2;
								}
							});
						});
					}
				})
				.finally(() => {
					this.btnLoading2 = false;
				});
		},
		treeChange(value, select, extra) {
			this.selectApplication = extra?.triggerNode?.dataRef?.unique_code;
			let inner = this.addproductWarehouseForm.getFieldValue("inner");
			this.appCode = value;
			if (inner == true) {
				this.baseUrl2 = this.selectApplication + "-";
			} else {
				this.baseUrl2 = "";
			}
			this.baseWarehouseUrl = this.baseUrl1 + this.baseUrl2;
		},
		// 取消删除
		onCancel() {
			this.deleteModel = false;
			this.delete_name = "";
		},
		// 确认删除
		onDeleteOk() {
			if (this.delete_name == this.activeObj.name) {
				this.deleteLoading = true;
				deleteproductWarehouse({ repository_id: this.activeObj.name, code: this.appCode })
					.then(res => {
						if (res.code == 200) {
							this.$message.success(res.message);
							this.onCancel();
							this.onClose();
							this.$emit("ref-list");
						} else {
							this.$message.error(res.message);
						}
					})
					.finally(() => {
						this.deleteLoading = false;
					});
			} else {
				return this.$message.warning(this.language.deleteMessage4);
			}
		},

		// 删除
		deleteproductWarehouse(record) {
			this.deleteModel = true;
		},
	},
};
</script>

<style lang="less" scoped>
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
			content: "";
			display: inline-block;
			width: 30px;
			height: 30px;
			background: url("~@/assets/image/check.png");
			background-size: 30px;
			position: absolute;
			top: -1px;
			right: -1px;
		}
	}
}
.footer {
	position: absolute;
	bottom: 0px;
	width: 800px;
	left: 0;
	border: 1px solid #e8e8e8;
	padding: 10px 20px;
	background: #fff;
	z-index: 10;
}
.special {
	.ant-radio-wrapper {
		border: 1px solid #ccc;
		padding: 5px 20px;
		width: 130px;
		height: 33px;
		border-radius: 5px;
	}
	.ant-radio-wrapper-checked {
		border: 1px solid @primary-color;
	}
}
</style>
