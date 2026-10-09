<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadDocs } from '@/api/admin'
import { ElLoading, ElMessage } from 'element-plus'
import { ragState } from '@/store/ragState'

const emit = defineEmits(['success'])

const limitDocSize = (file) => {
  const maxFileSize = 1024 * 1024 * 10
  
  if (file.size > maxFileSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

const handleUpload = async (param) => {
  const formData = new FormData()
  formData.append('file', param.file)
  formData.append('chunk_size', ragState.size)
  formData.append('chunk_overlap', ragState.overlap)
  formData.append('strategy', ragState.strategy) 

  // 开启全屏加载动画（向量化过程较慢）
  const loading = ElLoading.service({ text: '正在进行深度解析与向量化入库...' })
  
  try {
    const res = await uploadDocs(formData)
    
    if (res.status === 'success') {
      ElMessage.success(`上传成功！共生成 ${res.chunks} 个知识分片`)
      emit('success')
    }
  } catch (error) {
    ElMessage.error('解析失败：' + (error.response?.data?.detail || '服务器响应异常'))
  } finally {
    loading.close()
  }
}
</script>

<template>
  <el-card class="upload-card">
    <el-row :gutter="40">
      <!-- 左侧：上传区 -->
      <el-col :span="10">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :http-request="handleUpload" 
          :show-file-list="false"
          accept=".pdf,.txt,.md,.docx,.doc"
          :before-upload="limitDocSize"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">支持 PDF, TXT, Markdown, DOCX, DOC 格式，单文件不超过 10MB</div>
          </template>
        </el-upload>
      </el-col>

      <!-- 右侧：RAG 参数配置区 -->
      <el-col :span="14">
        <el-form label-width="120px" size="small">
          <el-form-item label="分片策略">
            <el-select v-model="ragState.strategy" style="width: 100%">
              <el-option label="RecursiveCharacter (递归字符分割)" value="recursive" />
              <el-option label="FixedSize (固定大小分割)" value="fixed" />
            </el-select>
          </el-form-item>
          <el-form-item label="分片大小 (Chunk)">
            <el-input-number v-model="ragState.size" :step="100" />
            <span class="unit-tip">字符 / 片</span>
          </el-form-item>
          <el-form-item label="重叠度 (Overlap)">
            <el-input-number v-model="ragState.overlap" :step="10" />
            <span class="unit-tip">字符</span>
          </el-form-item>
          <el-form-item label="Embedding模型">
            <el-tag type="info">BGE-base-zh-v1.5 (本地推理)</el-tag>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
  </el-card>
</template>

<style scoped>
.upload-card { margin-bottom: 20px; }
.unit-tip { margin-left: 10px; color: #909399; font-size: 12px; }
</style>

