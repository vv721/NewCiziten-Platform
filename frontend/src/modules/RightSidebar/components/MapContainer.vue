<script setup>
import { onMounted, onUnmounted, watch } from 'vue';
import { uiState } from '@/store/uiState'
import AMapLoader from '@amap/amap-jsapi-loader';

let map = null;
let markers = [];
let walkRender = null;
let activeMarker = null;
let defaultIcon = null;
let activeIcon = null;

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
      icon: defaultIcon,
      offset: new window.AMap.Pixel(-10, -32),
    })

    // 绑定点击事件，切换图标 + 弹出信息窗体
    marker.on('click', () => {
      if (activeMarker && activeMarker !== marker) {
        activeMarker.setIcon(defaultIcon)
        activeMarker.setOffset(new window.AMap.Pixel(-10, -32))
      }
      marker.setIcon(activeIcon)
      marker.setOffset(new window.AMap.Pixel(-12, -38))
      activeMarker = marker

      const closeId = `iw-close-${Date.now()}`
      const infoWindow = new window.AMap.InfoWindow({
        isCustom: true,
        content: `<div style="
              position:relative;
              width:210px;
              padding:14px 28px 14px 16px;
              background:#fff;
              border-radius:10px;
              box-shadow:0 4px 16px rgba(0,0,0,0.12);
              font-family:system-ui,-apple-system,sans-serif;
            ">
              <span id="${closeId}" style="
                position:absolute;top:8px;right:10px;
                width:18px;height:18px;line-height:18px;
                text-align:center;font-size:14px;color:#94a3b8;
                cursor:pointer;border-radius:50%;transition:all 0.15s;
              " onmouseover="this.style.background='#f1f5f9';this.style.color='#475569'"
                 onmouseout="this.style.background='transparent';this.style.color='#94a3b8'"
              >&times;</span>
              <div style="font-size:15px;font-weight:600;color:#1e293b;margin-bottom:8px;padding-right:4px;">
                ${item.name}
              </div>
              ${item.distance != null ? `<div style="font-size:13px;font-weight:600;color:#409EFF;margin-bottom:6px;">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#409EFF;margin-right:6px;vertical-align:middle;"></span>
                距您约 ${item.distance} 公里
              </div>` : ''}
              <div style="font-size:13px;color:#475569;margin-bottom:6px;">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#94a3b8;margin-right:6px;vertical-align:middle;"></span>
                ${item.address}
              </div>
              <div style="font-size:13px;color:#475569;">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#94a3b8;margin-right:6px;vertical-align:middle;"></span>
                ${item.phone}
              </div>
            </div>`,
        offset: new window.AMap.Pixel(0, -30)
      })
      infoWindow.open(map, marker.getPosition())
      // 绑定关闭按钮
      setTimeout(() => {
        const btn = document.getElementById(closeId)
        if (btn) btn.onclick = () => infoWindow.close()
      }, 50)
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
      center: [121.528503, 38.973333],  // 大连工业大学
      resizeEnable: true,
    });
    
    // 预创建两种图标
    defaultIcon = new AMap.Icon({
      size: new AMap.Size(20, 32),
      image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_bs.png',
      imageSize: new AMap.Size(20, 32),
      imageOffset: new AMap.Pixel(0, 0),
    })
    activeIcon = new AMap.Icon({
      size: new AMap.Size(24, 38),
      image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
      imageSize: new AMap.Size(24, 38),
      imageOffset: new AMap.Pixel(0, 0),
    })

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
        const pos = [result.position.lng, result.position.lat];
        console.log('[定位] GPS 成功，起点坐标:', pos);
        resolve(pos);
      } else {
        const fallback = [121.528503, 38.973333];
        console.warn('[定位] 失败 (' + status + ')，使用兜底坐标:', fallback);
        resolve(fallback);
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
  console.log('[导航] 起点:', startPos, '→ 终点:', endPos);

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