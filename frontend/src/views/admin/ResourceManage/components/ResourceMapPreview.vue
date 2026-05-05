<script setup>
import { onMounted, onUnmounted, watch, ref } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { Location, Compass } from '@element-plus/icons-vue'

const props = defineProps({
  activeResource: {
    type: Object,
    default: null
  }
})

let map = null
let marker = null

// 1. 初始化地图
const initMap = () => {
  window._AMapSecurityConfig = {
    securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
  }

  AMapLoader.load({
    key: import.meta.env.VITE_AMAP_KEY,
    version: "2.0",
    plugins: ['AMap.ToolBar']
  }).then((AMap) => {
    map = new AMap.Map("admin-map-preview", {
      zoom: 12,
      center: [121.5, 38.9], // 默认大连中心点
      viewMode: "3D"
    })
    map.addControl(new AMap.ToolBar())
  })
}

// 2. 接洽逻辑：当选中的资源变化时，更新地图位置和标记
watch(() => props.activeResource, (newVal) => {
  if (!newVal || !map || !newVal.latlng) return

  // [核心改动]：将 "lng,lat" 字符串拆分为高德需要的数字数组 [lng, lat]
  const coords = newVal.latlng.split(',')
  const pos = [parseFloat(coords[0]), parseFloat(coords[1])]

  // 防御性检查：确保解析出的坐标是有效数字
  if (isNaN(pos[0]) || isNaN(pos[1])) {
    console.error("无效的坐标数据:", newVal.latlng)
    return
  }

  // 如果之前有标记，先移除
  if (marker) {
    map.remove(marker)
  }

  // 创建新标记
  marker = new window.AMap.Marker({
    position: pos,
    title: newVal.name
  })

  map.add(marker)
  
  // 平滑移动并缩放
  map.setZoomAndCenter(15, pos, false, 500) // 缩放级15，动画时长500ms
})

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  map?.destroy()
})
</script>


<template>
  <div class="preview-container">
    <!-- 地图容器 -->
    <div id="admin-map-preview" class="map-box"></div>
    
    <!-- 未选中时的遮罩提示 -->
    <div v-if="!activeResource" class="empty-overlay">
      <el-empty description="请从左侧列表选择一个资源点进行预览" />
    </div>

    <!-- 选中时的浮窗详情 -->
    <div v-else class="detail-float-card">
      <h4>{{ activeResource.name }}</h4>
      <p><el-icon><Location /></el-icon> {{ activeResource.address }}</p>
      <p><el-icon><Compass /></el-icon> 坐标: {{ activeResource.latlng }}</p>
    </div>
  </div>
</template>


<style scoped>
.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-box {
  width: 100%;
  height: 100%;
}

/* 提示遮罩 */
.empty-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* 浮动信息卡片 */
.detail-float-card {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 11;
  border: 1px solid #409eff;
}

.detail-float-card h4 { margin: 0 0 8px 0; color: #303133; }
.detail-float-card p { margin: 4px 0; font-size: 12px; color: #606266; display: flex; align-items: center; gap: 5px; }
</style>