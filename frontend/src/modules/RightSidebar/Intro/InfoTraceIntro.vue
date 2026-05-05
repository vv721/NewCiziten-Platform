<script setup>
import { Search, Checked, Collection } from '@element-plus/icons-vue'
</script>

<template>
  <div class="trace-intro-container">
    <div class="intro-inner">
      <!-- 状态标识 -->
      <div class="status-tag">RAG ENGINE READY</div>
      
      <!-- 核心视觉：带有动态扫描效果的图标 -->
      <div class="visual-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <div class="scan-bar"></div>
      </div>

      <h3 class="intro-title">政策检索就绪</h3>
      <p class="intro-desc">
        请在对话框输入您的咨询需求，系统将实时检索知识库并在此处还原原文证据。
      </p>

      <!-- 技术特性暗示 -->
      <div class="feature-list">
        <div class="feature-item">
          <el-icon><Checked /></el-icon>
          <span>多模态原文溯源</span>
        </div>
        <div class="feature-item">
          <el-icon><Collection /></el-icon>
          <span>高维语义向量匹配</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trace-intro-container {
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
  background: #f0fdf4;
  color: #16a34a;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #dcfce7;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
}

.visual-box {
  position: relative;
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

.search-icon {
  font-size: 42px;
  color: #3b82f6;
}

/* 扫描线动画：体现 RAG 检索的动态感 */
.scan-bar {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  animation: scanning 2.5s infinite ease-in-out;
}

@keyframes scanning {
  0%, 100% { top: 15%; opacity: 0; }
  50% { top: 85%; opacity: 1; }
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