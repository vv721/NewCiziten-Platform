<script setup>
import { computed, ref } from 'vue'
import { uiState } from '@/store/uiState'
import ServiceNavigationIntro from '@/modules/RightSidebar/Intro/ServiceNavigationIntro.vue'
import {
  Guide,
  List,
  MapLocation,
  CircleCheckFilled
} from '@element-plus/icons-vue'

const data = computed(() => uiState.activeProcess)

// 交互状态
const currentStep = ref(-1)
const checkedMaterials = ref(new Set())

const handleStartNavigation = () => {
  if (data.value && data.value.latlng) {
    uiState.dispatchCommand('START_NAV', data.value.latlng);
  }
};

const toggleMaterial = (idx) => {
  const set = checkedMaterials.value
  if (set.has(idx)) {
    set.delete(idx)
  } else {
    set.add(idx)
  }
  // 触发响应式更新
  checkedMaterials.value = new Set(set)
}
</script>

<template>
  <div class="service-nav-wrapper">
    <!-- A. 固定头部：事项名称 -->
    <div v-if="data" class="nav-header">
      <div class="header-tag">政务导办</div>
      <h2 class="title">{{ data.title }}</h2>
      <div class="dept-info">受理：{{ data.dept }}</div>
    </div>

    <!-- B. 中部可滚动区：流程与材料 -->
    <div v-if="data" class="nav-scroll-body">
      <!-- 流程步骤 -->
      <div class="section">
        <div class="section-label"><el-icon><Guide /></el-icon> 办理流程</div>
        <el-steps direction="vertical" :active="currentStep" class="custom-steps">
          <el-step
            v-for="(step, idx) in data.steps"
            :key="idx"
            :title="step.name"
            :description="step.desc"
            class="clickable-step"
            @click="currentStep = idx"
          />
        </el-steps>
      </div>

      <!-- 材料清单 -->
      <div class="section">
        <div class="section-label"><el-icon><List /></el-icon> 所需材料</div>
        <div class="material-card-list">
          <div
            v-for="(m, idx) in data.materials"
            :key="idx"
            class="material-card"
            :class="{ checked: checkedMaterials.has(idx) }"
            @click="toggleMaterial(idx)"
          >
            <el-icon class="check-icon" :class="{ checked: checkedMaterials.has(idx) }">
              <CircleCheckFilled />
            </el-icon>
            <div class="m-info">
              <div class="m-name" :class="{ checked: checkedMaterials.has(idx) }">{{ m.name }}</div>
              <div class="m-type">{{ m.type }} | {{ m.paper_count }}份</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- C. 底部固定按钮：一键导航 -->
    <div v-if="data && data.latlng" class="nav-footer">
      <el-button 
        type="primary" 
        class="nav-main-btn" 
        @click="handleStartNavigation"
      >
        <el-icon><MapLocation /></el-icon>
        <span>前往办事网点</span>
      </el-button>
    </div>

    <!-- 引导页 -->
    <ServiceNavigationIntro v-if="!data" />
  </div>
</template>

<style scoped>
/* 容器：强制占满 100% 高度并锁定 */
.service-nav-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden;
}

/* 头部样式 */
.nav-header {
  padding: 20px;
  background: linear-gradient(to bottom, #f0f7ff, #ffffff);
  border-bottom: 1px solid #f1f5f9;
}
.header-tag {
  font-size: 10px;
  background: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 8px;
}
.title { margin: 0; font-size: 18px; color: #1e293b; }
.dept-info { font-size: 12px; color: #64748b; margin-top: 4px; }

/* 滚动区域：关键在于 flex: 1 和 overflow-y */
.nav-scroll-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.section { margin-bottom: 24px; }
.section-label { 
  display: flex; align-items: center; gap: 8px;
  font-weight: 600; font-size: 14px; margin-bottom: 16px; color: #334155;
}

/* 步骤条样式修正 */
.custom-steps :deep(.el-step__title) { font-size: 13px; line-height: 1.4; }
.custom-steps :deep(.el-step__description) { font-size: 11px; margin-top: 4px; color: #94a3b8; }
.custom-steps :deep(.el-step.is-vertical) { padding-bottom: 20px; }

.clickable-step {
  cursor: pointer;
}
.clickable-step:hover :deep(.el-step__head) {
  transform: scale(1.15);
  transition: transform 0.2s;
}

/* 材料卡片 */
.material-card {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.material-card:hover {
  border-color: #93c5fd;
}
.material-card.checked {
  background: #f0fdf4;
  border-color: #86efac;
}
.check-icon {
  color: #cbd5e1;
  margin-top: 2px;
  transition: color 0.2s;
  flex-shrink: 0;
}
.check-icon.checked {
  color: #22c55e;
}
.m-name {
  font-size: 13px; font-weight: 500; color: #1e293b;
  transition: all 0.2s;
}
.m-name.checked {
  text-decoration: line-through;
  color: #94a3b8;
}
.m-type { font-size: 11px; color: #64748b; }

/* 底部按钮 */
.nav-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  background: #ffffff;
}
.nav-main-btn {
  width: 100%; height: 48px; border-radius: 10px; font-weight: 600; gap: 8px;
}
</style>