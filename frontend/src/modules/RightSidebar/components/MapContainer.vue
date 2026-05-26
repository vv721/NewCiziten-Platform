<script setup>
import { onMounted, onUnmounted, watch } from 'vue';
import { uiState } from '@/store/uiState'
import AMapLoader from '@amap/amap-jsapi-loader';

let map = null;
let markers = [];
let walkRender = null;

const updateMarkers = (points) => {
  if (!map || !window.AMap) return

  // 1. 清除旧标记
  map.remove(markers)
  markers = []

  // 2. 循环添加新标记
  points.forEach(item => {
    const marker = new window.AMap.Marker({
      position: [parseFloat(item.latlng.split(',')[0]), parseFloat(item.latlng.split(',')[1])],
      title: item.name,
    })

    // 绑定点击事件，弹出信息窗体
    marker.on('click', () => {
      const infoWindow = new window.AMap.InfoWindow({
        content: `<div style="padding:10px;font-size:12px;">
                    <b style="font-size:14px;color:#409EFF;">${item.name}</b><br/>
                    ${item.distance != null ? `距您约: ${item.distance} 公里<br/>` : ''}
                    地址: ${item.address}<br/>
                    电话: ${item.phone}
                  </div>`,
        offset: new window.AMap.Pixel(0, -30)
      })
      infoWindow.open(map, marker.getPosition())
    })

    markers.push(marker)
  })

  // 3. 渲染到地图上
  map.add(markers)

  // 4. 自动调整视野，让所有点都出现在屏幕内
  if (markers.length > 0) {
    map.setFitView(markers)
  }
}


onMounted(async () => {
  // 必须：在加载前配置安全密钥（高德 API 2.0 强制要求）
  window._AMapSecurityConfig = {
    securityJsCode: import.meta.env.VITE_AMAP_SECURITY_KEY, 
  };

  AMapLoader.load({
    key: import.meta.env.VITE_AMAP_KEY, // 申请好的Key
    version: "2.0",              // 指定 JS API 版本
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.Walking', 'AMap.Geolocation'], // 需要使用的插件
  }).then((AMap) => {
    map = new AMap.Map("amap-container", {
      viewMode: "3D",           // 开启3D视图，毕设视觉效果更好
      zoom: 11,                 // 初始缩放级别
      center: [121.5, 38.9],
      resizeEnable: true,
    });
    
    // 添加基础控件
    map.addControl(new AMap.Scale());
    map.addControl(new AMap.ToolBar());
  }).catch(e => {
    console.error("高德地图加载失败:", e);
  });
});

const getCurrentPosition = () => {
  return new Promise((resolve) => {
    const geolocation = new window.AMap.Geolocation({
      enableHighAccuracy: true, // 优先使用 GPS 定位
      timeout: 5000,            // 5秒超时
    });

    geolocation.getCurrentPosition((status, result) => {
      if (status === 'complete') {
        resolve([result.position.lng, result.position.lat]);
      } else {
        // [论文演示兜底] 如果定位失败（如非HTTPS），返回一个模拟的起始点坐标
        console.warn("定位受限，使用演示模拟起点");
        resolve([121.53185438568383,38.97131009007171]); // 示例
      }
    });
  });
};


const drawRoute = async (destLatLng) => {
  if (!map || !window.AMap) return;

  // 1. 清理旧图层：移除散点 Marker 和 之前的导航线
  map.clearMap(); 
  if (walkRender) {
    walkRender.clear();
  }

  // 2. 获取起点和终点
  const startPos = await getCurrentPosition();
  const endPos = destLatLng.split(',').map(Number);

  // 3. 调用步行路径规划插件
  walkRender = new window.AMap.Walking({
    map: map,
    panel: false,      // 不显示文字列表，只看线
    autoFitView: true  // 自动缩放视角
  });

  walkRender.search(startPos, endPos, (status, result) => {
    if (status === 'complete') {
      console.log("✅ 导航线绘制成功");
    } else {
      console.error("❌ 导航失败:", result);
    }
  });
};

watch(() => uiState.mapPoints, (newPoints) => {
  updateMarkers(newPoints)
}, { deep: true })

watch(() => uiState.navigationTarget, (newTarget) => {
  if (newTarget) {
    drawRoute(newTarget);
  }
});

onUnmounted(() => {
  map?.destroy(); // 组件销毁时销毁地图实例，释放内存
});
</script>

<template>
  <div id="amap-container" class="map-box"></div>
</template>


<style scoped>
.map-box {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>