import { reactive, shallowRef, ref } from 'vue'

export const uiState = reactive({
  // 1. 核心模式定义：'auto' (智能), 'policy' (政策), 'map' (资源), 'service' (办事)
  activeMode: 'auto', 
  
  // 2. 轮播图索引与模式的映射关系
  // 0: 政策溯源, 1: 地图, 2: 办事指南
  modeToIndex: {
    'policy': 0,
    'map': 1,
    'service': 2
  },

  currentCarouselIndex: 0,
  mapPoints: [],
  citationList: [],
  activeProcess: null,
  navigationTarget: null, 

  // 3. 动作：手动切换模式（用户点击胶囊触发）
  setMode(mode) {
    this.activeMode = mode;
    // 如果不是自动模式，立即切页
    if (mode !== 'auto') {
      this.currentCarouselIndex = this.modeToIndex[mode];
    }
    console.log(`[UI切换] 当前模式: ${mode}`);
  },

  // 4. 动作：接收后端指令（AI 响应触发）
  dispatchCommand(command, data) {
    // 逻辑接洽：根据 AI 返回的指令，自动同步胶囊状态（实现自动纠偏）
    const cmdToMode = {
      'SHOW_TRACE': 'policy',
      'SHOW_MAP': 'map',
      'SHOW_PROCESS': 'service',
      'START_NAV': 'map'
    };

    if (cmdToMode[command]) {
      this.activeMode = cmdToMode[command];
      this.currentCarouselIndex = this.modeToIndex[this.activeMode];
    }

    // 分发具体数据
    if (command === 'SHOW_MAP') {
      this.mapPoints = data;
      this.navigationTarget = null;
    }
    if (command === 'START_NAV') {
      // [新增] 导航模式下，存入目的地坐标，并清空之前的散点
      this.navigationTarget = data; 
      this.mapPoints = []; 
    }
    if (command === 'SHOW_TRACE') this.citationList = data;
    if (command === 'SHOW_PROCESS') this.activeProcess = data;
  }
})
