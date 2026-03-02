/**
 * 导出文件工具函数
 * 支持让用户选择保存位置（需要浏览器支持 File System Access API）
 * 不支持的浏览器会回退到传统下载方式
 */

/**
 * 检查浏览器是否支持 File System Access API
 */
export function isFileSystemAccessSupported() {
  return 'showSaveFilePicker' in window
}

/**
 * 导出文件到用户选择的位置
 * @param {Blob} blob - 文件内容
 * @param {string} defaultFileName - 默认文件名
 * @param {string} fileType - 文件类型，如 'xlsx'
 * @param {string} mimeType - MIME类型，如 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
 * @returns {Promise<boolean>} - 是否成功
 */
export async function exportFile(blob, defaultFileName, fileType = 'xlsx', mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
  try {
    if (isFileSystemAccessSupported()) {
      // 使用 File System Access API 让用户选择保存位置
      const handle = await window.showSaveFilePicker({
        suggestedName: defaultFileName,
        types: [{
          description: 'Excel 文件',
          accept: { [mimeType]: [`.${fileType}`] }
        }]
      })
      
      const writable = await handle.createWritable()
      await writable.write(blob)
      await writable.close()
      
      return true
    } else {
      // 回退到传统下载方式
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = defaultFileName
      document.body.appendChild(link)
      link.click()
      
      // 清理
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(link)
      }, 100)
      
      return true
    }
  } catch (error) {
    // 用户取消选择
    if (error.name === 'AbortError') {
      return false
    }
    throw error
  }
}

/**
 * 从响应中获取文件名
 * @param {Object} response - axios 响应对象
 * @param {string} defaultName - 默认文件名
 * @returns {string} - 文件名
 */
export function getFileNameFromResponse(response, defaultName) {
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    const matches = /filename="([^"]+)"/.exec(contentDisposition)
    if (matches && matches[1]) {
      return matches[1]
    }
  }
  return defaultName
}
