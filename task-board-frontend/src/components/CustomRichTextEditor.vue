<template>
  <div class="custom-editor-container">
    <div class="wangeditor-container" :class="{ 'readonly': readonly }">
      <Toolbar 
        v-if="!readonly"
        :editor="editorRef"
        :defaultConfig="toolbarConfig"
        :mode="mode"
        style="border-bottom: 1px solid #dcdfe6;"
      />
      <Editor 
        :defaultConfig="editorConfig"
        :mode="mode"
        @onCreated="handleCreated"
        @onChange="handleChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onBeforeUnmount, computed } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: Number,
    default: 300
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  mode: {
    type: String,
    default: 'default'
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const editorRef = shallowRef()
const readonly = computed(() => props.readonly)

const toolbarConfig = {}
toolbarConfig.excludeKeys = [
  'group-video',
  'insertTable',
  'table',
  'group-more-style',
]

const editorConfig = {
  placeholder: props.placeholder,
  height: props.height,
  menu: [
    'bold', 'italic', 'underline', 'strikethrough',
    'head', 'list', 'justify', 'quote',
    'link', 'image', 
    'code', 'undo', 'redo',
    'fullScreen'
  ],

  MENU_CONF: {
    uploadImage: {
      customUpload(file, insertFn) {
        if (props.readonly) return
        
        const formData = new FormData()
        formData.append('file', file)
        
        const token = localStorage.getItem('token')
        
        fetch('/api/upload/image', {
          method: 'POST',
          headers: {
            'Authorization': token ? `Bearer ${token}` : ''
          },
          body: formData
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`上传失败: ${response.status} ${response.statusText}`)
          }
          return response.json()
        })
        .then(data => {
          console.log('上传成功:', data)
          insertFn(data.url)
        })
        .catch(err => {
          console.error('上传失败:', err)
          ElMessage.error('图片上传失败，请重试（可能是图片大小超过限制）')
        })
      },
      maxFileSize: 5 * 1024 * 1024,
      allowedFileTypes: ['image/*']
    }
  }
}

const handleCreated = (editor) => {
  editorRef.value = editor
  if (props.readonly) {
    editor.disable()
  }
  
  // 初始化编辑器内容
  try {
    if (props.modelValue) {
      // 确保内容是字符串
      let content = props.modelValue
      if (typeof content !== 'string') {
        // 如果是对象，尝试转换为字符串
        if (typeof content === 'object') {
          if (content.text) {
            content = content.text
          } else {
            content = JSON.stringify(content)
          }
        } else {
          content = String(content)
        }
      }
      
      // 确保内容是有效的HTML
      let htmlContent = content
      if (!htmlContent.includes('<p>') && !htmlContent.includes('<div>')) {
        htmlContent = `<p>${htmlContent}</p>`
      }
      
      editor.setHtml(htmlContent)
    } else {
      // 空内容时设置默认值
      editor.setHtml('<p></p>')
    }
  } catch (error) {
    console.error('编辑器初始化错误:', error)
    // 发生错误时设置默认值
    editor.setHtml('<p></p>')
  }
}

const handleChange = (editor) => {
  if (props.readonly) return
  
  try {
    const html = editor.getHtml()
    emit('update:modelValue', html)
    emit('change', html)
  } catch (error) {
    console.error('编辑器内容更新错误:', error)
  }
}

watch(() => props.modelValue, (newVal) => {
  if (editorRef.value) {
    try {
      if (newVal) {
        // 确保内容是字符串
        let content = newVal
        if (typeof content !== 'string') {
          // 如果是对象，尝试转换为字符串
          if (typeof content === 'object') {
            if (content.text) {
              content = content.text
            } else {
              content = JSON.stringify(content)
            }
          } else {
            content = String(content)
          }
        }
        
        // 确保内容是有效的HTML
        let htmlContent = content
        if (!htmlContent.includes('<p>') && !htmlContent.includes('<div>')) {
          htmlContent = `<p>${htmlContent}</p>`
        }
        
        // 只有当内容不同时才更新
        if (editorRef.value.getHtml() !== htmlContent) {
          editorRef.value.setHtml(htmlContent)
        }
      } else {
        // 空内容时设置默认值
        if (editorRef.value.getHtml() !== '<p></p>') {
          editorRef.value.setHtml('<p></p>')
        }
      }
    } catch (error) {
      console.error('编辑器内容更新错误:', error)
    }
  }
})

watch(() => props.readonly, (newVal) => {
  if (editorRef.value) {
    if (newVal) {
      editorRef.value.disable()
    } else {
      editorRef.value.enable()
    }
  }
})

onBeforeUnmount(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
  }
})
</script>

<style scoped>
.custom-editor-container {
  width: 100%;
}

.wangeditor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.wangeditor-container.readonly {
  border: none;
}

.wangeditor-container.readonly :deep(.w-e-text-container) {
  min-height: 100px;
}

.wangeditor-container :deep(.w-e-text-container) {
  background-color: #fff;
}

.wangeditor-container :deep(.w-e-text-container [data-slate-editor]) {
  min-height: 300px;
}

.wangeditor-container :deep(.w-e-text-placeholder) {
  color: #a8abb2;
  font-style: normal;
}

.wangeditor-container :deep(.w-e-toolbar) {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.wangeditor-container :deep(.w-e-bar-item button) {
  color: #606266;
}

.wangeditor-container :deep(.w-e-bar-item button:hover) {
  background-color: #f5f7fa;
}

.wangeditor-container :deep(.w-e-active) {
  background-color: #ecf5ff;
  color: #409eff;
}
</style>

<style>
.wangeditor-container :deep(.w-e-full-screen-container) {
  z-index: 9999999 !important;
}

.wangeditor-container :deep(.w-e-full-screen-mask) {
  z-index: 9998 !important;
}
</style>
