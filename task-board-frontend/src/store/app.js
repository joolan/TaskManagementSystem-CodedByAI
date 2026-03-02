import { defineStore } from 'pinia'

// 应用状态管理
export const useAppStore = defineStore('app', {
  state: () => ({
    globalLoading: false,
    loadingText: '加载中...'
  }),
  actions: {
    setGlobalLoading(loading, text = '加载中...') {
      this.globalLoading = loading
      this.loadingText = text
    }
  }
})