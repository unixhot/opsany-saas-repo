<template>
	<div>
		<div v-if="noNexus" style="background: #fff">
			<a-empty
				image="https://gw.alipayobjects.com/mdn/miniapp_social/afts/img/A*pevERLJC9v0AAAAAAAAAAABjAQAAAQ/original"
				:image-style="{ height: '80px' }"
				style="padding: 280px 0 280px 0"
			>
				<p style="margin: 20px 0 0 0" slot="description">
					{{ language.noNexus1
					}}<a style="color: #076aff" @click="$router.push({ path: '/setting/systemSettings' })">{{ language.noNexus2 }}</a
					>{{ language.noNexus3 }}
				</p>
			</a-empty>
		</div>
		<div v-else class="productWarehouse_main">
			<div class="main_left">
				<div class="header">
					<h3>{{ language.productWarehouse }}</h3>
					<a-button
						v-if="$store.state.btnAuth.btnAuth.repo_repository_create"
						@click="$refs.AddproductWarehouse.onShow(appCode)"
						type="primary"
						style="border-radius: 2px"
					>
						<a-icon type="plus" />新建制品库
					</a-button>
				</div>
				<a-spin :spinning="productWarehouseLoading">
					<a-tree-select
						dropdownClassName="resource-tree-select-productWarehouse"
						:dropdownStyle="{ width: '420px' }"
						@change="onSearch1"
						v-model="appCode"
						showSearch
						:treeData="treeData"
						treeNodeFilterProp="title"
						style="width: 180px; margin: 0 0 0 12px"
						placeholder="请选择所属应用"
					>
						<template slot="title_name" slot-scope="{ name, job_count }">
							<span :title="name">{{ name || "--" }}</span> ({{ job_count || 0 }})
						</template>
					</a-tree-select>
					<a-input-search
						@search="onSearch2"
						allowClear
						v-model="search_data"
						:placeholder="language.search_placeholder"
						style="margin: 10px 0 10px 10px; width: 180px"
					></a-input-search>
					<div class="productWarehouseList" v-if="productWarehouseList.length">
						<div
							:id="'#' + item.code"
							:class="{ productWarehouseCell: true, active: item.name == productWarehouse.name }"
							v-for="(item, index) in productWarehouseList"
							:key="index"
							@click="productWarehouseChange($event, index, item)"
						>
							<img v-if="item.format == 'raw'" src="@/assets/image/repository_type_raw.png" alt="" />
							<img v-else-if="item.format == 'docker'" src="@/assets/image/repository_type_docker.png" alt="" />
							<img v-else-if="item.format == 'maven2'" src="@/assets/image/repository_type_maven.png" alt="" />
							<img v-else-if="item.format == 'pypi'" src="@/assets/image/repository_type_pypi.png" alt="" />
							<img v-else-if="item.format == 'nuget'" src="@/assets/image/repository_type_nuget.png" alt="" />
							<img v-else-if="item.format == 'helm'" src="@/assets/image/repository_type_helm.png" alt="" />

							<div class="cell_center">
								<p class="p1" :title="item.name">
									{{ item.name }}
								</p>
								<p class="p2">
									<span class="span4"
										>{{ item.format }} {{ language.warehouse }} <a-divider style="margin:0 5px;" type="vertical" />
										{{ item.isinner }}</span
									>
								</p>
							</div>
							<div class="cell_right">
								<a style="margin:0 20px 0 0" class="span4">
									<a-icon v-if="item.tags" style="color: #ff9600;" @click.stop="collect(item)" type="star" theme="filled" />
									<a-icon v-else-if="!item.tags" type="star" @click.stop="collect(item)" />
								</a>
								<span v-if="item.can_update" class="span3" @click.stop="$refs.AddproductWarehouse.onShow(appCode, item)">
									<a-icon type="edit" />
								</span>
							</div>
						</div>
					</div>
					<a-empty v-else />
				</a-spin>
			</div>
			<div class="main_right">
				<div class="header" v-if="productWarehouse.name">
					<h3>
						{{ productWarehouse.name }}
					</h3>
					<p>{{ productWarehouse.describe || "暂无描述" }}</p>
					<p>
						<!-- 所属应用：<span class="span1">{{ productWarehouse.name }}</span><a-divider style="margin:0 12px 0 16px;" type="vertical" /> -->
						格式：<span class="span1">{{ productWarehouse.format }}</span
						><a-divider style="margin:0 12px 0 16px;" type="vertical" /> 类型：<span class="span1">{{ productWarehouse.type }}</span
						><a-divider style="margin:0 12px 0 16px;" type="vertical" /> 权限：<span class="span1">{{ productWarehouse.isinner }}</span>
					</p>
					<div style="border-bottom:1px solid #e8e8e8;margin:0 -20px 10px;"></div>
				</div>
				<a-tabs v-if="productWarehouse.name" :activeKey="activeKey" @change="activeKeyChange">
					<a-tab-pane key="1" :tab="language.tabTitle1">
						<a-input-search
							allowClear
							:loading="moreLoading"
							v-model="search_data_file"
							@search="onSearch"
							:placeholder="language.searchPlaceholder1"
							style="width: 400px; margin: 0px 0 10px 0"
						></a-input-search>
						<a-upload
							v-if="productWarehouse.can_file_upload"
							style="float: right; margin: 0px 0 10px 10px"
							:showUploadList="false"
							:before-upload="beforeUpload"
						>
							<a-button
								type="primary"
								icon="upload"
								v-if="
									productWarehouse.format &&
										(productWarehouse.format == 'pypi' ||
											productWarehouse.format == 'raw' ||
											productWarehouse.format == 'nuget' ||
											productWarehouse.format == 'maven2')
								"
								style="border-radius: 2px; margin: 0 10px 0 0"
								>{{ language.uploadProduct }}</a-button
							>
						</a-upload>
						<a-button :loading="moreLoading" style="float:right;" @click="onReload" icon="reload">刷新</a-button>
						<a-table :pagination="false" :columns="columns" :scroll="{x:500}" :data-source="tableData" :loading="tableLoading">
							<span slot="name" slot-scope="text, record">
								<a v-if="productWarehouse.can_file_detail" @click="showView(record)">{{ text }}</a>
								<span v-else>{{ text }}</span>
							</span>
							<span slot="action" slot-scope="text, record">
								<a v-if="productWarehouse.can_file_detail" @click="showView(record)">{{ language.details }}</a>
								<a
									v-if="productWarehouse.can_file_delete"
									style="margin: 0 0 0 10px"
									@click="deleteproductWarehouseFileData(record)"
									>{{ language.delete }}</a
								>
								<span v-if="!productWarehouse.can_file_detail && !productWarehouse.can_file_delete">--</span>
							</span>
						</a-table>
						<div v-if="ismore">
							<a-spin :spinning="moreLoading">
								<a-button @click="getMore" style="margin: 20px auto 0; display: block">{{ language.loadMore }}</a-button>
							</a-spin>
						</div>
					</a-tab-pane>
					<a-tab-pane key="2" :tab="language.tabTitle2" force-render>
						<div class="guide" v-html="guideHtml"></div>
					</a-tab-pane>
				</a-tabs>
				<a-empty v-else style="margin:200px 0 0 0;"></a-empty>
			</div>
			<a-modal :title="language.uploadProduct" v-model="uploadProductModel" @ok="handleok" :confirmLoading="btnLoading">
				<a-form :form="uploadForm" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
					<a-form-item :label="language.label1">
						<a-input :readOnly="true" v-decorator="['filename', { rules: [{ required: true, message: language.rule1 }] }]"></a-input>
					</a-form-item>
					<template v-if="productWarehouse.format == 'maven2'">
						<a-form-item :label="language.label2">
							<a-input v-decorator="['groupId', { rules: [{ required: true, message: language.rule2 }] }]"></a-input>
						</a-form-item>
						<a-form-item :label="language.label3">
							<a-input v-decorator="['artifactId', { rules: [{ required: true, message: language.rule3 }] }]"></a-input>
						</a-form-item>
						<a-form-item :label="language.label4">
							<a-input v-decorator="['version', { rules: [{ required: true, message: language.rule4 }] }]"></a-input>
						</a-form-item>
						<a-form-item :label="language.label5">
							<a-input v-decorator="['extension', { rules: [{ required: true, message: language.rule5 }] }]"></a-input>
						</a-form-item>
					</template>
				</a-form>
			</a-modal>
			<a-drawer class="drawer" width="800px" @close="onClose" :title="filedetails.repository" :visible="visible">
				<a-collapse default-active-key="0" :bordered="false">
					<template #expandIcon="props">
						<a-icon type="caret-right" :rotate="props.isActive ? 90 : 0" />
					</template>
					<a-collapse-panel
						class="cell"
						v-for="(item, index) in filedetails.assets"
						:key="index + ''"
						style="background: #fff; border-radius: 4px; margin-bottom: 24px; border: 0; overflow: hidden"
					>
						<h3 slot="header" class="title">
							{{ item.path }}
							<span v-if="item.format != 'docker'" style="float: right">
								<a v-if="productWarehouse.can_file_download" @click.stop target="_blank" :href="item.downloadUrl">{{
									language.download
								}}</a>
								<a-tooltip v-else title="无操作权限">
									<a-button disabled type="link" size="small">{{ language.download }}</a-button>
								</a-tooltip>
							</span>
						</h3>
						<p>
							<span class="span1">{{ language.label6 }}：</span> <span :title="item.path">{{ item.path }}</span>
						</p>
						<p>
							<span class="span1">{{ language.label7 }}：</span>
							<span :title="item.repository">{{ item.repository }}</span>
						</p>
						<p>
							<span class="span1">{{ language.label8 }}：</span> <span :title="item.format">{{ item.format }}</span>
						</p>
						<p v-if="productWarehouse.format != 'raw'">
							<span class="span1">{{ language.label9 }}：</span>
							<span :title="filedetails.version">{{ filedetails.version }}</span>
						</p>
						<p>
							<span class="span1">{{ language.label10 }}：</span> <span :title="item.id">{{ item.id }}</span>
						</p>
						<p>
							<span class="span1">下载路径：</span> <span style="flex:1 1 0;overflow:hidden" :title="item.downloadUrl">{{ item.downloadUrl }}</span>
							<a style="margin:0 0 0 10px;flex:0 0 30px;" v-clipboard:copy="item.downloadUrl" v-clipboard:success="() => $message.success('复制成功')"
                                v-clipboard:error="() => $message.error('复制失败')">复制</a>
						</p>
						<p>
							<span class="span1">文件大小：</span> <span :title="unitConversion(item.size)">{{ unitConversion(item.size) }}</span>
						</p>
						<p>
							<span class="span1">创建时间：</span> <span :title="timeConversion(item.blobCreated)">{{ timeConversion(item.blobCreated) }}</span>
						</p>
						<p>
							<span class="span1">更新时间：</span> <span :title="timeConversion(item.lastModified)">{{ timeConversion(item.lastModified) }}</span>
						</p>
						<p>
							<span class="span1">最后下载时间：</span> <span :title="timeConversion(item.lastDownloaded)">{{ timeConversion(item.lastDownloaded) }}</span>
						</p>
					</a-collapse-panel>
				</a-collapse>
			</a-drawer>
			<AddproductWarehouse @ref-list="data => getproductWarehouseData(data)" ref="AddproductWarehouse"></AddproductWarehouse>
		</div>
	</div>
</template>

<script>
import {
	getproductWarehouse,
	getRepositoryComponent,
	deleteproductWarehouseFile,
	getGuide,
	upload,
	searchComponent,
	collectNexus,
} from "@/api/productWarehouse";
import { getBusinessTree } from "@/api/business.js";
import marked from "marked";
import AddproductWarehouse from "./addproductWarehouse1.vue";
import moment from 'moment';
export default {
	data() {
		return {
			// 左侧loading
			productWarehouseLoading: false,
			// 左侧列表数据
			productWarehouseList: [],
			tableData: [],
			tableLoading: false,
			// 上传制品弹框
			uploadProductModel: false,
			// 指引
			guideHtml: "",
			// 选中的制品库信息(右侧数据)
			productWarehouse: {},
			// 上传文件
			file: {},
			uploadForm: this.$form.createForm(this, { name: "uploadForm" }),

			visible: false,
			// 文件(详情)信息
			filedetails: {},
			// 加载更多是否显示
			ismore: false,
			// 加载更多的token
			continuationToken: "",
			// 上传提交loading
			btnLoading: false,
			moreLoading: false,
			// 是否是搜索
			isSearch: false,
			noNexus: false,
			treeData: [],
			appCode: undefined,
			search_data: "",
			search_data_file: "",
			activeKey: "1",
		};
	},
	computed: {
		columns() {
            if (this.productWarehouse.format == "raw") {
                return [
                    {
                        title: this.language.columns1,
                        dataIndex: "name",
                        key: "name",
                        width: 200,
                        ellipsis: "false",
                        scopedSlots: { customRender: "name" },
                    },
					{
                        title: "文件大小",
                        dataIndex: "fileSize",
                        width: 100,
                    },
					{
                        title: "创建时间",
                        dataIndex: "createdTime",
                        width: 160,
                    },
                    {
                        title: this.language.columns4,
                        key: "action",
                        scopedSlots: { customRender: "action" },
                        width: 100,
                    },
                ];
            } else {
				return [
                    {
                        title: this.language.columns1,
                        dataIndex: "name",
                        key: "name",
                        width: 200,
                        ellipsis: "false",
                        scopedSlots: { customRender: "name" },
                    },
                    {
                        title: this.language.columns2,
                        dataIndex: "version",
                        key: "version",
                        width: 70,
                    },
                    {
                        title: this.language.columns3,
                        dataIndex: "versions_number",
                        key: "versions_number",
                        width: 70,
                    },
                    {
                        title: this.language.columns4,
                        key: "action",
                        scopedSlots: { customRender: "action" },
                        width: 100,
                    },
                ];
			}
        },
	},
	created() {
		this.language = Object.assign(
			{},
			this.$store.state.language.languageAuth.public1 || {},
			this.$store.state.language.languageAuth.productWarehouse || {}
		);
	},
	mounted() {
		this.getBusinessTreeData(true);
		if (this.$route.query.isOpen) {
			this.$refs.AddproductWarehouse.onShow(this.$route.query.appCode);
		}
	},
	methods: {
		// 文件大小单位转换
		unitConversion(metadata) {
			if (metadata < 1024) {
                return metadata + "B"
            } else if (metadata < (1024 * 1024)) {
                return (metadata / 1024).toFixed(2) + "KB"
            } else if (metadata < (1024 * 1024 * 1024)) {
                return (metadata / (1024 * 1024)).toFixed(2) + "MB"
            } else if (metadata < (1024 * 1024 * 1024 * 1024)) {
                return (metadata / (1024 * 1024 * 1024)).toFixed(2) + "GB"
            }
		},
		// 时间格式转换
		timeConversion(time) {
			return time ? moment(time).format("YYYY-MM-DD HH:mm:ss") : "--"
		},
		activeKeyChange(val) {
			this.activeKey = val;
		},
		// 获取更多
		getMore() {
			this.getRepositoryComponentData(this.productWarehouse);
			this.moreLoading = true;
		},
		// 收藏
		collect(record) {
			this.productWarehouseLoading = true;
			collectNexus({ code: this.appCode, repo_code: record.code, tags: !record.tags })
				.then(res => {
					if (res.code == 200) {
						this.getproductWarehouseData("reload");
					}
				})
				.finally(() => {
					this.productWarehouseLoading = false;
				});
		},
		// 删除文件
		deleteproductWarehouseFileData(record) {
			this.$confirm({
				title: "删除确认",
				content: "请确认是否删除?",
				okType: "danger",
				onOk: () => {
					return new Promise((resolve, reject) => {
						deleteproductWarehouseFile({
							repository_id: this.productWarehouse.name,
							component_id: record.id,
							code: this.appCode,
						})
							.then(res => {
								if (res.code == 200) {
									this.$message.success(res.message);
									this.tableData = [];
									this.continuationToken = "";
									this.getRepositoryComponentData(this.productWarehouse);
									resolve();
								}
							})
							.catch(() => {
								reject();
							});
					});
				},
			});
		},
		onReload() {
			this.moreLoading = true;
			if (this.search_data_file) {
				this.onSearch();
			} else {
				this.tableData = [];
				this.continuationToken = "";
				this.getRepositoryComponentData(this.productWarehouse);
			}
		},
		// 搜索
		onSearch1(val) {
			this.appCode = val;
			this.assemblyLineIndex = 0;
			this.getproductWarehouseData();
		},
		// 搜索
		onSearch2() {
			this.assemblyLineIndex = 0;
			this.getproductWarehouseData();
		},
		// 搜索
		onSearch() {
			this.moreLoading = true;
			if (this.search_data_file) {
				this.continuationToken = "";
				this.searchValue = this.search_data_file;
				this.tableData = [];
				this.isSearch = true;
				this.getSearchData(this.search_data_file);
			} else {
				this.tableData = [];
				this.continuationToken = "";
				this.getRepositoryComponentData(this.productWarehouse);
			}
		},
		// 搜索
		getSearchData(val) {
			this.tableLoading = true;
			let updata = {
				repository: this.productWarehouse.name,
				code: this.appCode,
				name: val,
			};
			if (this.continuationToken) {
				updata.continuationToken = this.continuationToken;
			}
			searchComponent(updata)
				.then(res => {
					if (res.code == 200) {
						let obj = {};
						if (res.data.continuationToken) {
							this.ismore = true;
						} else {
							this.ismore = false;
						}
						this.continuationToken = res.data.continuationToken;
						res.data.items.map(item => {
							let key = item.name;
							if (obj[key]) {
								obj[key]++;
							} else {
								obj[key] = 1;
							}
						});

						if (
							this.productWarehouse.format == "docker" ||
							this.productWarehouse.format == "raw" ||
							this.productWarehouse.format == "nuget" ||
							this.productWarehouse.format == "maven2" ||
							this.productWarehouse.format == "pypi"
						) {
							res.data.items.map(item => {
								item.versions_number = obj[item.name];
								item.version = item.version ? item.version : "--";
								item.key = item.id;
								this.tableData.push(item);
							});
						}

						this.tableLoading = false;
						this.moreLoading = false;
					}
				})
				.catch(res => {
					this.tableLoading = false;
					this.moreLoading = false;
				});
		},
		// 获取制品库数据(左侧)
		getproductWarehouseData(getdata) {
			this.productWarehouseLoading = true;
			let updata = { code: this.appCode };
			if (this.search_data) {
				updata.search_type = "repo_name";
				updata.search_data = this.search_data;
			}
			getproductWarehouse(updata)
				.then(res => {
					if (res.code == 200 && res.data) {
						res.data.inner_list.map(item => {
							item.isinner = "当前应用";
						});
						res.data.public_list.map(item => {
							item.isinner = "公共仓库";
						});
						this.productWarehouseList = res.data.inner_list.concat(res.data.public_list);
						if (this.productWarehouseList.length) {
							if (getdata != "reload") {
								this.tableData = [];
								this.search_data_file = "";
							}
							if (getdata == "first" && this.$route.query.repository) {
								let obj = this.productWarehouseList.find(item => {
									return item.name == this.$route.query.repository;
								});
								if (obj) {
									this.productWarehouse = obj;
									this.getRepositoryComponentData(obj);
									this.getGuideData(obj);
									this.$nextTick(() => {
										let object = document.getElementById("#" + obj.code);
										if (object) {
											object.scrollIntoView(true);
											document.documentElement.scrollTop = 0;
										}
									});
								} else {
									this.tableLoading = false;
								}
							} else if (getdata == "reload") {
								this.productWarehouse = this.productWarehouseList.find(item => {
									return item.name == this.productWarehouse.name;
								});
								// this.getRepositoryComponentData(this.productWarehouse)
							} else if (getdata != "reload") {
								this.continuationToken = "";
								this.productWarehouse = this.productWarehouseList[0];
								this.getRepositoryComponentData(this.productWarehouseList[0]);
								this.getGuideData(this.productWarehouseList[0]);
							}
						} else {
							this.tableLoading = false;
							this.productWarehouse = {};
							this.tableData = [];
						}
					} else {
					}
				})
				.catch(res => {
					if (res?.code == 404 && res?.errcode == 40402) {
						this.noNexus = true;
					} else {
					}
				})
				.finally(() => {
					if (this.productWarehouseList.length == 0 || getdata == "reload") {
						this.productWarehouseLoading = false;
					}
				});
		},
		// 获取文件数据(右侧)
		getRepositoryComponentData(record) {
			this.tableLoading = true;
			let updata = { repository_id: record.name, code: this.appCode };
			if (this.continuationToken) {
				updata.continuationToken = this.continuationToken;
			}
			getRepositoryComponent(updata)
				.then(res => {
					if (res.code == 200) {
						let obj = {};
						if (res.data.continuationToken) {
							this.ismore = true;
						} else {
							this.ismore = false;
						}
						this.continuationToken = res.data.continuationToken;
						res.data.items.map(item => {
							let key = item.name;
							if (obj[key]) {
								obj[key]++;
							} else {
								obj[key] = 1;
							}
						});
						if (
							record.format == "docker" ||
							record.format == "raw" ||
							record.format == "nuget" ||
							record.format == "maven2" ||
							record.format == "pypi"
						) {
							res.data.items.map(item => {
								item.versions_number = obj[item.name];
								item.version = item.version ? item.version : "--";
								item.key = item.id;
								if(item.format == "raw") {
									item.createdTime = item.assets[0]?.lastModified && this.timeConversion(item.assets[0]?.lastModified)
									item.fileSize = item.assets[0]?.size && this.unitConversion(item.assets[0]?.size) || '0B'
								}
								this.tableData.push(item);
							});
						}
					}
				})
				.catch(res => {})
				.finally(() => {
					this.tableLoading = false;
					this.moreLoading = false;
					this.productWarehouseLoading = false;
				});
		},
		// 获取指引(markdown)
		getGuideData(record) {
			getGuide({
				repository_format: record.format,
				repository_id: record.name,
				code: this.appCode,
			})
				.then(res => {
					if (res.code == 200 && res.data) {
						this.guideHtml = marked(res.data.content);
					} else {
						this.guideHtml = "";
					}
				})
				.catch(res => {
					this.guideHtml = "";
				});
		},
		// 点击切换制品库
		productWarehouseChange(e, index, record) {
			console.log(record);
			this.activeKey = "1";
			this.productWarehouseLoading = true;
			this.productWarehouse = record;
			this.tableData = [];
			this.continuationToken = "";
			this.search_data_file = "";
			this.ismore = false;
			this.isSearch = false;
			this.getRepositoryComponentData(record);
			this.getGuideData(record);
		},
		beforeUpload(file) {
			this.file = file;
			this.uploadProductModel = true;
			let _this = this;
			this.$nextTick(function() {
				_this.uploadForm.setFieldsValue({ filename: _this.file.name });
			});
			return false;
		},
		// 上传提交
		handleok() {
			this.uploadForm.validateFields((err, values) => {
				if (!err) {
					let formData = new FormData();
					formData.append("repository_id", this.productWarehouse.name);
					formData.append("filename", values.filename);
					formData.append("file", this.file);
					if (values.groupId) {
						formData.append("groupId", values.groupId);
					}
					if (values.artifactId) {
						formData.append("artifactId", values.artifactId);
					}
					if (values.version) {
						formData.append("version", values.version);
					}
					if (values.extension) {
						formData.append("extension", values.extension);
					}
					this.btnLoading = true;
					upload(formData)
						.then(res => {
							if (res.code == 200) {
								this.$message.success(res.message);
								this.uploadProductModel = false;
								this.tableData = [];
								this.continuationToken = "";
								this.getRepositoryComponentData(this.productWarehouse);
							}
						})
						.finally(() => {
							this.btnLoading = false;
							this.isSearch = false;
						});
				}
			});
		},
		// 文件详情展示
		showView(record) {
			this.visible = true;
			this.filedetails = record;
		},
		// 抽屉关闭
		onClose() {
			this.visible = false;
		},
		// 获取业务与应用(用于选择应用)
		getBusinessTreeData(first) {
			this.productWarehouseLoading = true;
			getBusinessTree()
				.then(res => {
					if (res.data && res.data.length > 0) {
						this.treeData = res.data;
						this.treeData = res.data.filter(item => {
							return item.children && item.children.length > 0;
						});
						if (this.treeData.length == 0) {
							this.tableLoading = false;
							this.assemblyLineListLoading = false;
							return;
						}
						this.treeData.map(item => {
							item.key = "n" + item.code;
							item.value = "n" + item.code;
							item.title = item.name;
							let job_count = 0;
							item.children.map(ele => (job_count += ele.job_count || 0));
							item.job_count = job_count;
                        	item.selectable = false
							this.$set(item, "scopedSlots", { title: "title_name" });
							item.children.map(ele => {
								ele.key = ele.code + "";
								ele.value = ele.code + "";
								ele.title = ele.name;
								this.$set(ele, "scopedSlots", { title: "title_name" });
							});
						});
						if (first && this.$route.query.appCode) {
							this.appCode = this.$route.query.appCode;
						} else {
							this.appCode = this.treeData[0].children[0].code;
						}
						this.getproductWarehouseData("first");
					}
				})
				.finally(() => {
					if (this.treeData.length == 0) {
						this.productWarehouseLoading = false;
					}
				});
		},
	},
	components: {
		AddproductWarehouse,
	},
};
</script>

<style lang="less" scoped>
.productWarehouse_main {
	background: #f0f2f5;
	height: 100%;
	display: flex;
}
.main_left {
	// min-width: 450px;
	margin: 0 10px 0 0;
	flex-basis: 400px;
	// border-right: 1px solid #ddd;
	height: calc(100vh - 145px);
	position: relative;
	background: #f9fbfd;
	.ant-empty {
		position: absolute;
		top: calc(50vh - 195px);
		left: 0;
		right: 0;
	}
	.ant-spin-nested-loading {
		height: calc(100% - 70px);
	}
	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: #fff;
		padding: 12px;
		box-shadow: -1px 1px 3px 3px #eee;
		h3 {
			margin: 0;
			font-size: 20px;
			font-weight: 1000;
		}
	}
	.productWarehouseList {
		height: calc(100vh - 260px);
		overflow-y: scroll;
		padding: 5px 0 0 0;
		.productWarehouseCell {
			box-shadow: 0px 0px 5px 3px #e8e8e8;
			padding: 10px;
			color: #333;
			height: 90px;
			position: relative;
			display: flex;
			align-items: center;
			cursor: pointer;
			margin: 0px 12px 12px;
			border-radius: 4px;
			background: #fff;
			&:hover {
				// background: fade(@primary-color, 10%);
				border: 1px solid @primary-color;
			}
			img {
				width: 46px;
				height: 46px;
				margin: 0 20px 0 10px;
			}
			.cell_right {
				display: flex;
				align-items: flex-end;
				position: absolute;
				bottom: 12px;
				right: 40px;
				.span3 {
					text-align: center;
					line-height: 25px;
					font-size: 14px;
					padding: 0 5px;
					border-radius: 6px;
					color: #666;
					height: 25px;
					width: 25px;
					cursor: pointer;
					float: right;
					box-shadow: 1px 2px 10px 0px rgba(61, 68, 80, 0.4);
					&:hover {
						color: @primary-color;
						transform: translateY(-2px);
					}
				}
				.span4 {
					cursor: pointer;
					font-size: 14px;
				}
			}
			.cell_center {
				// margin: 0 0 0 20px;
				flex: 1 1 0;
				.p1 {
					margin: 0px 0 0 0px;
					align-items: center;
					font-size: 16px;
					color: #333;
					font-weight: 500;
					overflow: hidden;
					text-overflow: ellipsis;
					white-space: nowrap;
					width: 270px;
				}
				.p2 {
					margin: 10px 0 0 0px;
					color: #888;
					display: flex;
					align-items: center;
					font-size: 12px;
					.span4 {
						width: 175px;
					}
				}
			}
		}
		.active {
			// background: fade(@primary-color, 7%);
			border: 1px solid @primary-color;
			&:after {
				content: "";
				display: inline-block;
				width: 3px;
				// background: @primary-color;
				height: 90px;
				position: absolute;
				top: 0;
				right: 0;
			}
		}
	}
}
.main_right {
	flex-grow: 1;
	flex: 1 1 0px;
	padding: 20px 20px 20px 20px;
	min-width: 500px;
	height: calc(100vh - 145px);
	overflow-y: scroll;
	background: #fff;
	.header {
		padding: 0 0 5px 0;
		h3 {
			margin: 0 0 0 10px;
			font-size: 20px;
			span {
				color: #aaa;
				font-size: 16px;
			}
		}
		p {
			padding: 5px 10px;
			margin: 0;
			color: #888;
			font-size: 12px;
		}
	}
}
.productWarehouseList {
	scrollbar-color: #e5e5e5 #f7f7f9; /* 滑块颜色  滚动条背景颜色 */
	scrollbar-width: thin; /* 滚动条宽度有三种：thin、auto、none */
}
::-webkit-scrollbar {
	width: 6px;
}
::-webkit-scrollbar-button {
	display: none;
}

::-webkit-scrollbar-track-piece {
	background: #ddd;
}
::-webkit-scrollbar-thumb {
	background: #c5c5c5;
}

.ant-drawer-content-wrapper {
	.ant-collapse {
		background: #fff;
	}
	.cell {
		margin: 0 0 20px 0;
		.title {
			background: #f7f9fa;
			font-size: 14px;
			padding: 5px;
		}
		p {
			margin: 10px 0 0 0;
			display: flex;
			padding: 5px;
			.span1 {
				width: 150px;
				display: inline-block;
				text-align: right;
				flex:0 0 150px;
			}
		}
	}
}
</style>
<style lang="less" scoped>
/deep/.guide {
	h4 {
		font-size: 18px;
		font-weight: 1000;
	}
	h5 {
		font-size: 14px;
		font-weight: 1000;
	}

	strong {
		font-weight: 1000;
		color: #333;
	}
	p {
		color: #333;
	}
	pre {
		background: #eee;
		padding: 10px;
	}
	ol,
	ul {
		padding: 0;
	}
}
</style>
<style lang="less">
.resource-tree-select-productWarehouse {
    max-height: 400px !important;
}
</style>

<style>
.resource-tree-select-productWarehouse .ant-select-tree-switcher {
	position: relative;
}
.resource-tree-select-productWarehouse .ant-select-tree-switcher_open::before,
.resource-tree-select-productWarehouse .ant-select-tree-switcher_close::before {
	content: "";
	position: absolute;
	right: -370px;
	top: 0;
	left: 0;
	bottom: 0;
}
</style>
