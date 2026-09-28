<template>
	<div>
		<a-spin :spinning="spinning">
			<div class="first_row">
				<div class="box">
					<ve-ring
						class="left"
						:judge-width="true"
						:data="chartData"
						:graphic="groupGraphic"
						:extend="chardExtend"
						:settings="chartSetting"
						:colors="['#00cbba', '#8aeee6', '#51E9A1']"
						height="100px"
					></ve-ring>
					<div class="right">
						<h3>制品库总数 {{ (number.repo_count && number.repo_count.repo_all_count) || 0 }}</h3>
						<p>公共仓库：{{ (number.repo_count && number.repo_count.repo_public_count) || 0 }}</p>
						<p>应用内仓库：{{ (number.repo_count && number.repo_count.repo_inner_count) || 0 }}</p>
					</div>
				</div>
				<div class="box">
					<img src="@/assets/image/repository_type_raw.png" alt="" />
					<div class="right">
						<h3>Raw仓库 {{ (number.repo_raw_count && number.repo_raw_count.repo_all_raw_count) || 0 }}</h3>
						<p>公共仓库：{{ (number.repo_raw_count && number.repo_raw_count.repo_public_raw_count) || 0 }}</p>
						<p>应用内仓库：{{ (number.repo_raw_count && number.repo_raw_count.repo_inner_raw_count) || 0 }}</p>
					</div>
				</div>
				<div class="box">
					<img src="@/assets/image/repository_type_docker.png" alt="" />
					<div class="right">
						<h3>Docker仓库 {{ (number.repo_docker_count && number.repo_docker_count.repo_all_docker_count) || 0 }}</h3>
						<p>公共仓库：{{ (number.repo_docker_count && number.repo_docker_count.repo_public_docker_count) || 0 }}</p>
						<p>应用内仓库：{{ (number.repo_docker_count && number.repo_docker_count.repo_inner_docker_count) || 0 }}</p>
					</div>
				</div>
				<div class="box">
					<img src="@/assets/image/repository_type_maven.png" alt="" />
					<div class="right">
						<h3>Maven仓库 {{ (number.repo_maven_count && number.repo_maven_count.repo_all_maven_count) || 0 }}</h3>
						<p>公共仓库：{{ (number.repo_maven_count && number.repo_maven_count.repo_public_maven_count) || 0 }}</p>
						<p>应用内仓库：{{ (number.repo_maven_count && number.repo_maven_count.repo_inner_maven_count) || 0 }}</p>
					</div>
				</div>
				<div class="box">
					<img src="@/assets/image/repository_type_pypi.png" alt="" />
					<div class="right">
						<h3>PyPI仓库 {{ (number.repo_pypi_count && number.repo_pypi_count.repo_all_pypi_count) || 0 }}</h3>
						<p>公共仓库：{{ (number.repo_pypi_count && number.repo_pypi_count.repo_public_pypi_count) || 0 }}</p>
						<p>应用内仓库：{{ (number.repo_pypi_count && number.repo_pypi_count.repo_inner_pypi_count) || 0 }}</p>
					</div>
				</div>
			</div>
		</a-spin>
		<div style="margin:16px 8px">
			<a-row :gutter="[16, 16]">
				<a-col v-bind="colSize">
					<a-card :bodyStyle="{ height: '642px' }" :loading="loading1" title="最近活跃的制品库">
						<div v-if="productWarehouseList.length > 0">
							<div class="productWarehouseCell_box" v-for="(item, index) in productWarehouseList" :key="index">
								<div class="productWarehouseCell">
									<img v-if="item.format == 'raw'" src="@/assets/image/repository_type_raw.png" alt="" />
									<img v-else-if="item.format == 'docker'" src="@/assets/image/repository_type_docker.png" alt="" />
									<img v-else-if="item.format == 'maven2'" src="@/assets/image/repository_type_maven.png" alt="" />
									<img v-else-if="item.format == 'pypi'" src="@/assets/image/repository_type_pypi.png" alt="" />
									<img v-else-if="item.format == 'nuget'" src="@/assets/image/repository_type_nuget.png" alt="" />
									<div class="cell_center">
										<p class="p1">
											<span :title="item.name" class="span2">{{ item.name }}</span>
										</p>
										<p class="p2">
											<span :title="item.is_app && item.application && item.application.name" class="span4"
												>{{ item.format }} {{ language.warehouse }} | {{ item.is_app ? item.application && item.application.name || '--' : "公共仓库" }}</span
											>
										</p>
									</div>
								</div>
								<div class="productWarehouseCell_right">
									<span class="round"></span>
									<span>最后活跃时间：{{ item.active_time }}</span>
									<div v-if="index > 0" class="line"></div>
								</div>
							</div>
						</div>
						<a-empty v-else></a-empty>
					</a-card>
				</a-col>
				<a-col v-bind="colSize">
					<a-card :bodyStyle="{ height: '642px' }" :loading="loading2" title="制品库文件数量统计排名Top10">
						<a-table :pagination="false" :columns="columns" :data-source="tableData" :loading="tableLoading">
							<div slot="index" slot-scope="text, record">
								<div v-if="record.index == 1" class="ranking first">{{ text }}</div>
								<div v-else-if="record.index == 2" class="ranking second">{{ text }}</div>
								<div v-else-if="record.index == 3" class="ranking third">{{ text }}</div>
								<div v-else class="ranking fourth">{{ text }}</div>
							</div>
							<span slot="repository" slot-scope="text, record">
								<a
									@click="
										$router.push({ name: 'productWarehouse', query: { repository: text, appCode: record.app_id || undefined } })
									"
									:title="text"
									>{{ text }}</a
								>
							</span>
						</a-table>
					</a-card>
				</a-col>
			</a-row>
		</div>
	</div>
</template>

<script>
import { getHomePage, gethomePageActive, gethomePageCount } from "@/api/home.js";
export default {
	data() {
		return {
			number: {},
			spinning: false,
			chartData: {
				columns: ["name", "number"],
				rows: [
					{ name: "公共仓库", number: 0 },
					{ name: "应用内仓库", number: 0 },
				],
			},
			groupGraphic: [
				{
					type: "text",
					left: "center",
					top: "45%",
					cursor: "default",
					style: {
						text: 0,
						textAlign: "center",
						fill: "rgba(0,0,0)",
						fontSize: 18,
						color: "rgba(0,0,0)",
					},
				},
			],
			chardExtend: {
				legend: {
					show: false,
				},
				cursor: "default",
				color: ["#69D288", "#FF7461"],
				series: {
					center: ["50%", "50%"],
				},
				tooltip: {
					position: [20, 0],
				},
			},
			chartSetting: {
				radius: ["60%", "75%"],
				labelLine: {
					show: false,
				},
				label: {
					show: false,
				},
			},
			productWarehouseList: [],
			columns: [
				{
					title: "序号",
					dataIndex: "index",
					scopedSlots: { customRender: "index" },
					align: "center",
					width: 60,
				},
				{
					title: "制品库名称",
					dataIndex: "repository",
					scopedSlots: { customRender: "repository" },
					width: 100,
					ellipsis: "true",
				},
				{
					title: "制品库类型",
					dataIndex: "type",
					width: 80,
					ellipsis: "true",
				},
				{
					title: "所属应用",
					dataIndex: "application",
					width: 100,
					ellipsis: "true",
					customRender: text => text || "--",
				},
				{
					title: "文件数量统计",
					dataIndex: "count",
					width: 80,
					ellipsis: "true",
				},
			],
			tableData: [],
			tableLoading: false,
			colSize: {
				xxl: 12,
				xl: 12,
				lg: 24,
				md: 24,
				sm: 24,
				xs: 24,
			},
			loading1: false,
			loading2: false,
		};
	},
	created() {
		this.language = Object.assign(
			{},
			this.$store.state.language.languageAuth.public1 || {},
			this.$store.state.language.languageAuth.productWarehouse || {}
		);
	},
	mounted() {
		this.getHomePageData();
		this.gethomePageActiveData();
		this.gethomePageCountData();
	},
	methods: {
		//获取顶部数据
		getHomePageData() {
			this.spinning = true;
			getHomePage()
				.then(res => {
					if (res.code == 200 && res.data) {
						this.number = res.data;
						this.chartData.rows = [
							{ name: "公共仓库", number: res.data.repo_count?.repo_public_count || 0 },
							{ name: "应用内仓库", number: res.data.repo_count?.repo_inner_count || 0 },
						];
						this.groupGraphic[0].style.text = res.data.repo_count?.repo_all_count || 0;
					}
				})
				.catch(res => {})
				.finally(() => {
					this.spinning = false;
				});
		},
		//最近活跃的制品库
		gethomePageActiveData() {
			this.loading1 = true;
			gethomePageActive()
				.then(res => {
					if (res.code == 200 && res.data) {
						this.productWarehouseList = res.data.slice(0, 6);
					}
				})
				.catch(res => {
					if (res.errcode != 40402) {
						// this.$message.warning(res.message)
					}
				})
				.finally(() => {
					this.loading1 = false;
				});
		},
		//制品库文件数量统计排名
		gethomePageCountData() {
			this.tableLoading = true;
			gethomePageCount()
				.then(res => {
					this.tableData = res.data.slice(0, 10);
					this.tableData.map((item, index) => {
						item.index = index + 1;
					});
				})
				.catch(res => {
					if (res.errcode != 40402) {
						// this.$message.warning(res.message)
					}
				})
				.finally(() => {
					this.tableLoading = false;
				});
		},
	},
};
</script>

<style lang="less" scoped>
.first_row {
	display: flex;
	overflow: hidden;
	.box {
		display: flex;
		flex: 1 1 0px;
		background: #fff;
		margin: 0 8px;
		align-items: center;
		padding: 20px 0 20px 0;
		flex-shrink: 1;
		// overflow: hidden;
		.left {
			flex: 0 0 90px;
		}
		img {
			width: 80px;
			height: 80px;
			flex: 0 0 80px;
			margin: 0 10px;
		}
		.right {
			flex: 1 0 0;
			// width:100%;
			h3 {
				font-size: 20px;
				white-space: nowrap;
				overflow: hidden;
				width: 100%;
			}
			p {
				margin: 0;
			}
		}
	}
}
.productWarehouseCell_box {
	height: 80px;
	margin: 0 0 20px 0;
	display: flex;
	.productWarehouseCell {
		flex: 0 0 300px;
		position: relative;
		width: 300px;
		box-shadow: 0px 0px 5px 3px #e8e8e8;
		padding: 10px;
		color: #333;
		height: 80px;
		position: relative;
		display: flex;
		align-items: center;
		// cursor: pointer;
		border-radius: 4px;
		background: #fff;
		&:hover {
			border: 1px solid @primary-color;
		}
		img {
			width: 40px;
			height: 40px;
			margin: 0 20px 0 10px;
		}
		.cell_center {
			.p1 {
				margin: 0px 0 0 0px;
				align-items: center;
				font-size: 16px;
				color: #333;
				.span2 {
					width: 195px;
					display: inline-block;
					overflow: hidden;
					text-overflow: ellipsis;
					white-space: nowrap;
					vertical-align: top;
				}
			}
			.p2 {
				margin: 10px 0 0 0px;
				color: #888;
				display: flex;
				align-items: center;
				font-size: 12px;
				.span4 {
					width: 175px;
					text-overflow: ellipsis;
					white-space: nowrap;
					overflow: hidden;
				}
			}
		}
	}
	.productWarehouseCell_right {
		position: relative;
		margin: 30px 0 0 40px;
		flex: 1 1 0;
		.round {
			display: inline-block;
			width: 15px;
			height: 15px;
			border: 3px solid @primary-color;
			margin: 0px 5px 0 -20px;
			border-radius: 50%;
			position: relative;
			top: 3px;
			background: #fff;
			z-index: 10;
		}
		.line {
			height: 100px;
			border-left: 1px solid #e8e8e8;
			position: absolute;
			bottom: 35px;
			left: -13px;
		}
	}
}
.first {
	background: url("~@/assets/image/first.png");
}
.second {
	background: url("~@/assets/image/second.png");
}
.third {
	background: url("~@/assets/image/third.png");
}
.fourth {
	background: url("~@/assets/image/fourth.png");
}
.ranking {
	background-size: 30px;
	background-repeat: no-repeat;
	background-position: center 8px;
	width: 30px;
	text-align: center;
	color: #fff;
	margin: 0 auto;
	font-weight: 600;
}
/deep/.ant-table-thead > tr > th,
/deep/.ant-table-tbody > tr > td {
	padding: 1px 10px;
	height: 54px;
	line-height: 40px;
}
@media screen and (max-width: 1550px) {
	.first_row {
		.box {
			padding: 5px 0;
			.left {
				flex: 0 0 60px;
			}
			img {
				height: 60px;
				flex: 0 0 60px;
			}
			.right {
				h3 {
					font-size: 16px;
				}
				p {
					font-size: 12px;
				}
			}
		}
	}
}
@media screen and (max-width: 1350px) {
	.first_row {
		.box {
			.left {
			}
			img {
				height: 40px;
				flex: 0 0 40px;
				margin: 0 5px;
			}
			.right {
				h3 {
					font-size: 14px;
				}
				p {
					font-size: 12px;
				}
			}
		}
	}
}
</style>
