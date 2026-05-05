<script setup>
import { Guide, Document, MapLocation } from '@element-plus/icons-vue'
</script>

<template>
  <div class="guide-intro-container">
    <div class="intro-inner">
      <div class="status-tag">SERVICE READY</div>

      <div class="visual-box">
        <el-icon class="main-icon"><Guide /></el-icon>
      </div>

      <h3 class="intro-title">办事指南就绪</h3>
      <p class="intro-desc">
        直接告诉我想办理的事项，我将为您梳理流程、材料清单与办事网点。
      </p>
      <p class="intro-hint">
        例如："居住证怎么办"、"办理落户需要什么"
      </p>

      <div class="feature-list">
        <div class="feature-item">
          <el-icon><Document /></el-icon>
          <span>结构化流程指引</span>
        </div>
        <div class="feature-item">
          <el-icon><MapLocation /></el-icon>
          <span>一键导航办事网点</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.guide-intro-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 30px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.intro-inner {
  text-align: center;
  max-width: 300px;
}

.status-tag {
  display: inline-block;
  font-family: 'Monaco', monospace;
  font-size: 10px;
  background: #eff6ff;
  color: #3b82f6;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #dbeafe;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
}

.visual-box {
  width: 90px;
  height: 90px;
  margin: 0 auto 20px;
  background: #fff;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
}

.main-icon {
  font-size: 42px;
  color: #3b82f6;
}

.intro-title {
  font-size: 18px;
  color: #1e293b;
  margin-bottom: 12px;
  font-weight: 600;
}

.intro-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 8px;
}

.intro-hint {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 32px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.feature-item .el-icon {
  color: #3b82f6;
  font-size: 14px;
}
</style>
