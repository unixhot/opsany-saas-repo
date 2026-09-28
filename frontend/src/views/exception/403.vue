<template>
    <!-- <exception-page type="403" /> -->
    <div class="center">
        <img src="@/assets/image/platform_not_authorized.png" alt="">
        <p>您暂未授权此平台，请联系管理员授权。</p>
        <div style="display:none">
            切换制品库右侧自动切换回文件列表;新建Docker类型默认端口为8015
        </div>
    </div>

</template>

<script>
import { ExceptionPage } from '@/components'

export default {
    components: {
        ExceptionPage
    }
}
</script>

<style scoped>
.center {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
}
img {
    width: 360px;
    height: 360px;
    margin: -100px 0 50px 0;
}
p {
    font-size: 24px;
    color: #333;
}
</style>
