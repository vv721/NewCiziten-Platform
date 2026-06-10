<script setup>
import FeatureCarousel from './components/FeatureCarousel.vue'
import NavSegmented from './components/NavSegmented.vue'

</script>

<template>
    <div class="right-sidebar-container">
        <!-- 1. 功能引导区：用于展示当前模块的辅助信息或标题 -->
        <div class="funcArea">
            <NavSegmented />
        </div>

        <!-- 2. 核心模块展示区：承载地图、轮播图等关键业务 -->
        <div class="moudleArea">
            <div class="moudle-inner">
                <FeatureCarousel />
            </div>
        </div>

        <div class="settingArea"></div>
    </div>
</template>

<style scoped>
.right-sidebar-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: #ffffff;
    border-left: 1px solid #e5e7eb;
    box-sizing: border-box;
}

/* 顶部：功能引导区 */
.funcArea {
  height: auto;
}

/* 中间：核心模块展示区 */
.moudleArea {
    flex: 1;
    min-height: 0;
    padding: 0 12px 12px;
    background-color: #f9fafb;
}

.moudle-inner {
    height: 100%;
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    /* 给内容区加一个精致的边框和阴影，使其看起来像浮在底板上 */
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* 底部：设置区域 */
.settingArea {
    height: 10%; /* 稍作调整，15% 略高 */
    padding: 0 20px;
    display: flex;
    align-items: center;
    border-top: 1px solid #f3f4f6;
}

/* 响应式调整 */
@media (max-height: 700px) {
    .funcArea, .settingArea {
        height: 12%;
    }
}
</style>