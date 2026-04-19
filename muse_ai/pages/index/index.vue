<template>
  <view class="container">
    <!-- 标题 -->
    <view class="header">
      <text class="title">💄 Muse AI 试妆</text>
      <text class="subtitle">AI美妆 · 触手可及</text>
    </view>

    <!-- 图片展示区 -->
    <view class="image-area">
      <view class="image-box" @click="chooseImage">
        <image v-if="!originalImg" src="/static/upload_placeholder.png" mode="aspectFit"></image>
        <image v-else :src="originalImg" mode="aspectFit"></image>
        <view class="image-label">原始图片</view>
      </view>
      <view class="image-box">
        <image v-if="!resultImg" src="/static/result_placeholder.png" mode="aspectFit"></image>
        <image v-else :src="resultImg" mode="aspectFit"></image>
        <view class="image-label">上妆效果</view>
      </view>
    </view>

    <!-- 处理状态提示 -->
    <view v-if="isLoading" class="status-tip">
      <text>🎨 AI正在处理中，请稍候...</text>
    </view>

    <!-- 快捷风格选择 -->
    <view class="style-section">
      <view class="section-title">✨ 快速选择风格</view>
      <scroll-view class="style-scroll" scroll-x show-scrollbar="false">
        <view class="style-buttons">
          <view 
            v-for="style in styleList" 
            :key="style.name"
            class="style-btn"
            :class="{ active: currentStyle === style.name }"
            @click="applyStyle(style)"
          >
            {{ style.name }}
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 参数控制区标题（可折叠） -->
    <view class="control-header" @click="showControls = !showControls">
      <text class="control-title">🛠️ 妆容参数调节</text>
      <text class="control-arrow">{{ showControls ? '▼' : '▶' }}</text>
    </view>

    <!-- 参数控制区 -->
    <scroll-view class="control-area" scroll-y v-show="showControls" :style="{ maxHeight: controlMaxHeight }">
      <!-- 基础底妆 -->
      <view class="param-group">
        <view class="group-title" @click="toggleGroup('base')">
          <text>🧖‍♀️ 基础底妆</text>
          <text>{{ showGroups.base ? '▼' : '▶' }}</text>
        </view>
        <view v-show="showGroups.base">
          <view class="slider-box">
            <view class="param-label">
              <text>磨皮美白</text>
              <text class="param-value">{{ foundationVal.toFixed(2) }}</text>
            </view>
            <slider 
              :value="foundationVal" 
              @change="e => foundationVal = e.detail.value" 
              min="0" max="1" step="0.05"
              activeColor="#FF6B6B"
              :disabled="isLoading"
            />
          </view>
        </view>
      </view>

      <!-- 魅力彩妆 -->
      <view class="param-group">
        <view class="group-title" @click="toggleGroup('color')">
          <text>💄 魅力彩妆</text>
          <text>{{ showGroups.color ? '▼' : '▶' }}</text>
        </view>
        <view v-show="showGroups.color">
          <!-- 口红颜色 -->
          <view class="color-box">
            <text>💄 口红颜色</text>
            <view class="color-row" @click="openColorPicker('lip')">
              <view class="color-display" :style="{ backgroundColor: lipColor }"></view>
              <text class="color-text">{{ lipColorName }}</text>
              <text class="color-arrow">▼</text>
            </view>
          </view>
          <!-- 口红浓度 -->
          <view class="slider-box">
            <view class="param-label">
              <text>口红浓度</text>
              <text class="param-value">{{ lipAlpha.toFixed(2) }}</text>
            </view>
            <slider 
              :value="lipAlpha" 
              @change="e => lipAlpha = e.detail.value" 
              min="0" max="1" step="0.05"
              activeColor="#FF6B6B"
              :disabled="isLoading"
            />
          </view>
          <!-- 腮红颜色 -->
          <view class="color-box">
            <text>😊 腮红颜色</text>
            <view class="color-row" @click="openColorPicker('blush')">
              <view class="color-display" :style="{ backgroundColor: blushColor }"></view>
              <text class="color-text">{{ blushColorName }}</text>
              <text class="color-arrow">▼</text>
            </view>
          </view>
          <!-- 腮红浓度 -->
          <view class="slider-box">
            <view class="param-label">
              <text>腮红浓度</text>
              <text class="param-value">{{ blushAlpha.toFixed(2) }}</text>
            </view>
            <slider 
              :value="blushAlpha" 
              @change="e => blushAlpha = e.detail.value" 
              min="0" max="1" step="0.05"
              activeColor="#FF6B6B"
              :disabled="isLoading"
            />
          </view>
        </view>
      </view>

      <!-- 眼部精修 -->
      <view class="param-group">
        <view class="group-title" @click="toggleGroup('eye')">
          <text>👁️ 眼部精修</text>
          <text>{{ showGroups.eye ? '▼' : '▶' }}</text>
        </view>
        <view v-show="showGroups.eye">
          <!-- 眼影颜色 -->
          <view class="color-box">
            <text>🎨 眼影颜色</text>
            <view class="color-row" @click="openColorPicker('eye')">
              <view class="color-display" :style="{ backgroundColor: eyeColor }"></view>
              <text class="color-text">{{ eyeColorName }}</text>
              <text class="color-arrow">▼</text>
            </view>
          </view>
          <!-- 眼影浓度 -->
          <view class="slider-box">
            <view class="param-label">
              <text>眼影浓度</text>
              <text class="param-value">{{ eyeAlpha.toFixed(2) }}</text>
            </view>
            <slider 
              :value="eyeAlpha" 
              @change="e => eyeAlpha = e.detail.value" 
              min="0" max="1" step="0.05"
              activeColor="#FF6B6B"
              :disabled="isLoading"
            />
          </view>
          <!-- 睫毛增强 -->
          <view class="slider-box">
            <view class="param-label">
              <text>👁️‍🗨️ 睫毛增强</text>
              <text class="param-value">{{ lashAlpha.toFixed(2) }}</text>
            </view>
            <slider 
              :value="lashAlpha" 
              @change="e => lashAlpha = e.detail.value" 
              min="0" max="1" step="0.05"
              activeColor="#FF6B6B"
              :disabled="isLoading"
            />
          </view>
        </view>
      </view>

      <!-- 智能美发 -->
      <view class="param-group">
        <view class="group-title" @click="toggleGroup('hair')">
          <text>💈 智能美发</text>
          <text>{{ showGroups.hair ? '▼' : '▶' }}</text>
        </view>
        <view v-show="showGroups.hair">
          <!-- 染发开关 -->
          <view class="switch-box">
            <text>开启染发</text>
            <switch :checked="hairEnable" @change="e => hairEnable = e.detail.value" color="#FF6B6B" :disabled="isLoading" />
          </view>
          <view v-if="hairEnable">
            <!-- 发色 -->
            <view class="color-box">
              <text>发色</text>
              <view class="color-row" @click="openColorPicker('hair')">
                <view class="color-display" :style="{ backgroundColor: hairColor }"></view>
                <text class="color-text">{{ hairColorName }}</text>
                <text class="color-arrow">▼</text>
              </view>
            </view>
            <!-- 染发强度 -->
            <view class="slider-box">
              <view class="param-label">
                <text>染发强度</text>
                <text class="param-value">{{ hairAlpha.toFixed(2) }}</text>
              </view>
              <slider 
                :value="hairAlpha" 
                @change="e => hairAlpha = e.detail.value" 
                min="0" max="1" step="0.05"
                activeColor="#FF6B6B"
                :disabled="isLoading"
              />
            </view>
          </view>
        </view>
      </view>

      <!-- SAM 特效 -->
      <view class="param-group">
        <view class="group-title" @click="toggleGroup('sam')">
          <text>📷 SAM 3 特效</text>
          <text>{{ showGroups.sam ? '▼' : '▶' }}</text>
        </view>
        <view v-show="showGroups.sam">
          <view class="switch-box">
            <text>开启背景虚化</text>
            <switch :checked="bokehEnable" @change="e => bokehEnable = e.detail.value" color="#FF6B6B" :disabled="isLoading" />
          </view>
          <view v-if="bokehEnable">
            <view class="slider-box">
              <view class="param-label">
                <text>虚化强度</text>
                <text class="param-value">{{ bokehVal.toFixed(2) }}</text>
              </view>
              <slider 
                :value="bokehVal" 
                @change="e => bokehVal = e.detail.value" 
                min="0" max="1" step="0.05"
                activeColor="#FF6B6B"
                :disabled="isLoading"
              />
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 操作按钮 -->
    <view class="action-section">
      <button type="primary" @click="chooseImage" :disabled="isLoading">📸 选择照片</button>
      <button type="warn" @click="uploadAndProcess" :loading="isLoading" :disabled="!originalImg || isLoading">
        {{ isLoading ? 'AI处理中...' : '✨ 一键上妆' }}
      </button>
      
      <view class="save-buttons" v-if="resultImg">
        <button type="default" @click="saveResult" class="save-btn">💾 保存到相册</button>
        <button type="default" @click="previewResult" class="debug-btn">🔍 预览结果</button>
      </view>
    </view>

    <!-- 🎨 颜色选择器弹窗 -->
    <view class="color-picker-modal" v-if="showColorPicker" @click="closeColorPicker">
      <view class="color-picker-content" @click.stop>
        <view class="picker-header">
          <text class="picker-title">选择{{ currentColorLabel }}颜色</text>
          <text class="picker-close" @click="closeColorPicker">✕</text>
        </view>
        
        <!-- 预设颜色网格 -->
        <view class="color-grid">
          <view 
            v-for="color in colorPalette" 
            :key="color.code"
            class="color-item"
            :class="{ active: currentSelectedColor === color.code }"
            :style="{ backgroundColor: color.code }"
            @click="selectColor(color.code)"
          >
            <text v-if="currentSelectedColor === color.code" class="check-mark">✓</text>
          </view>
        </view>
        
        <!-- 自定义颜色输入 -->
        <view class="custom-color">
          <text class="custom-label">自定义颜色</text>
          <view class="custom-row">
            <input 
              type="text" 
              v-model="customColorInput" 
              placeholder="#RRGGBB"
              maxlength="7"
            />
            <view class="custom-preview" :style="{ backgroundColor: customColorPreview }"></view>
            <button class="apply-btn" @click="applyCustomColor">应用</button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      originalImg: '',
      resultImg: '',
      isLoading: false,
      
      // API地址
      apiUrl: 'http://172.20.89.51:5000/api/makeup',
      
      // 控制面板
      showControls: true,
      controlMaxHeight: '600px',
      showGroups: {
        base: true,
        color: true,
        eye: false,
        hair: false,
        sam: false
      },
      
      // 当前风格
      currentStyle: '自定义',
      styleList: [
        { name: '🍵 日常妆', lipColor: '#E77C8E', lipAlpha: 0.45, blushColor: '#FFB7C5', blushAlpha: 0.3, eyeColor: '#8B5F4D', eyeAlpha: 0.15, lashAlpha: 0.2, foundationVal: 0.4 },
        { name: '🍷 晚宴妆', lipColor: '#990000', lipAlpha: 0.2, blushColor: '#CD5C5C', blushAlpha: 0.2, eyeColor: '#CD5C5C', eyeAlpha: 0.1, lashAlpha: 0.4, foundationVal: 0.5 },
        { name: '🏃‍♀️ 运动妆', lipColor: '#FF7F50', lipAlpha: 0.25, blushColor: '#FFA07A', blushAlpha: 0.2, eyeColor: '#000000', eyeAlpha: 0.0, lashAlpha: 0.0, foundationVal: 0.1 },
        { name: '🍂 裸妆', lipColor: '#D2B48C', lipAlpha: 0.1, blushColor: '#DEB887', blushAlpha: 0.1, eyeColor: '#A0522D', eyeAlpha: 0.0, lashAlpha: 0.1, foundationVal: 0.1 },
        { name: '✨ 高冷妆', lipColor: '#C71585', lipAlpha: 0.3, blushColor: '#B36E90', blushAlpha: 0.3, eyeColor: '#1241DE', eyeAlpha: 0.02, lashAlpha: 0.4, foundationVal: 0.5 }
      ],
      
      // 妆容参数
      foundationVal: 0.4,
      lipColor: '#D62F38',
      lipAlpha: 0.4,
      blushColor: '#FFC0CB',
      blushAlpha: 0.0,
      eyeColor: '#74488A',
      eyeAlpha: 0.0,
      lashAlpha: 0.0,
      hairEnable: false,
      hairColor: '#5C2616',
      hairAlpha: 0.35,
      bokehEnable: false,
      bokehVal: 0.5,
      
      // 🎨 颜色选择器相关
      showColorPicker: false,
      currentColorType: '',
      currentColorLabel: '',
      currentSelectedColor: '',
      customColorInput: '',
      
      // 预设颜色调色板
      colorPalette: [
        // 红色系
        { code: '#FF0000', name: '正红' },
        { code: '#D62F38', name: '复古红' },
        { code: '#990000', name: '酒红' },
        { code: '#E77C8E', name: '豆沙红' },
        { code: '#FF6B6B', name: '珊瑚红' },
        // 粉色系
        { code: '#FFC0CB', name: '粉红' },
        { code: '#FFB7C5', name: '樱花粉' },
        { code: '#FF69B4', name: '热粉' },
        { code: '#C71585', name: '紫红' },
        { code: '#DB7093', name: '苍紫' },
        // 橘色系
        { code: '#FF7F50', name: '珊瑚橘' },
        { code: '#FFA07A', name: '亮鲑鱼' },
        { code: '#FF8C00', name: '暗橙' },
        { code: '#FF6347', name: '番茄红' },
        // 棕色系
        { code: '#8B5F4D', name: '可可棕' },
        { code: '#A0522D', name: '赭色' },
        { code: '#D2B48C', name: '裸色' },
        { code: '#DEB887', name: '布利克' },
        { code: '#CD5C5C', name: '印度红' },
        // 紫色系
        { code: '#74488A', name: '紫罗兰' },
        { code: '#800080', name: '紫色' },
        { code: '#9370DB', name: '中紫' },
        { code: '#BA55D3', name: '兰花紫' },
        // 其他
        { code: '#000000', name: '黑色' },
        { code: '#5C2616', name: '深棕' }
      ]
    }
  },
  
  computed: {
    // 获取颜色名称
    lipColorName() {
      return this.getColorName(this.lipColor)
    },
    blushColorName() {
      return this.getColorName(this.blushColor)
    },
    eyeColorName() {
      return this.getColorName(this.eyeColor)
    },
    hairColorName() {
      return this.getColorName(this.hairColor)
    },
    customColorPreview() {
      let color = this.customColorInput
      if (!color.startsWith('#')) {
        color = '#' + color
      }
      return /^#[0-9A-Fa-f]{6}$/.test(color) ? color : '#CCCCCC'
    }
  },
  
  mounted() {
    const systemInfo = uni.getSystemInfoSync()
    this.controlMaxHeight = (systemInfo.windowHeight * 0.45) + 'px'
  },
  
  methods: {
    toggleGroup(name) {
      this.showGroups[name] = !this.showGroups[name]
    },
    
    chooseImage() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.originalImg = res.tempFilePaths[0]
          this.resultImg = ''
          console.log('📁 选择的图片:', this.originalImg)
        }
      })
    },
    
    applyStyle(style) {
      this.currentStyle = style.name
      this.lipColor = style.lipColor
      this.lipAlpha = style.lipAlpha
      this.blushColor = style.blushColor
      this.blushAlpha = style.blushAlpha
      this.eyeColor = style.eyeColor
      this.eyeAlpha = style.eyeAlpha
      this.lashAlpha = style.lashAlpha
      this.foundationVal = style.foundationVal
      uni.showToast({ title: `已应用${style.name}`, icon: 'success' })
    },
    
    // 获取颜色名称
    getColorName(colorCode) {
      const color = this.colorPalette.find(c => c.code.toLowerCase() === colorCode.toLowerCase())
      return color ? color.name : colorCode
    },
    
    // 🎨 打开颜色选择器
    openColorPicker(type) {
      let label = ''
      let currentColor = ''
      
      switch (type) {
        case 'lip':
          label = '口红'
          currentColor = this.lipColor
          break
        case 'blush':
          label = '腮红'
          currentColor = this.blushColor
          break
        case 'eye':
          label = '眼影'
          currentColor = this.eyeColor
          break
        case 'hair':
          label = '发色'
          currentColor = this.hairColor
          break
      }
      
      this.currentColorType = type
      this.currentColorLabel = label
      this.currentSelectedColor = currentColor
      this.customColorInput = currentColor
      this.showColorPicker = true
    },
    
    // 关闭颜色选择器
    closeColorPicker() {
      this.showColorPicker = false
      this.currentColorType = ''
      this.currentColorLabel = ''
      this.currentSelectedColor = ''
      this.customColorInput = ''
    },
    
    // 选择颜色
    selectColor(color) {
      this.currentSelectedColor = color
      this.customColorInput = color
      
      // 立即应用颜色
      this.applyColor(color)
    },
    
    // 应用自定义颜色
    applyCustomColor() {
      let color = this.customColorInput.trim()
      if (!color.startsWith('#')) {
        color = '#' + color
      }
      
      if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
        this.applyColor(color)
      } else {
        uni.showToast({ title: '颜色格式错误', icon: 'error' })
      }
    },
    
    // 应用颜色到对应参数
    applyColor(color) {
      switch (this.currentColorType) {
        case 'lip':
          this.lipColor = color
          break
        case 'blush':
          this.blushColor = color
          break
        case 'eye':
          this.eyeColor = color
          break
        case 'hair':
          this.hairColor = color
          break
      }
      
      this.$forceUpdate()
      this.closeColorPicker()
      
      uni.showToast({ 
        title: `${this.currentColorLabel}颜色已更新`, 
        icon: 'success',
        duration: 1000
      })
    },
    
    uploadAndProcess() {
      if (!this.originalImg) {
        uni.showToast({ title: '请先选择照片', icon: 'none' })
        return
      }
      
      this.isLoading = true
      uni.showLoading({ title: 'AI正在上妆...', mask: true })
      
      console.log('📤 开始上传，API地址:', this.apiUrl)
      console.log('📤 图片路径:', this.originalImg)
      
      const formData = {
        'foundation_val': String(this.foundationVal),
        'lip_color': this.lipColor,
        'lip_alpha': String(this.lipAlpha),
        'blush_color': this.blushColor,
        'blush_alpha': String(this.blushAlpha),
        'eye_color': this.eyeColor,
        'eye_alpha': String(this.eyeAlpha),
        'lash_alpha': String(this.lashAlpha),
        'hair_enable': String(this.hairEnable),
        'hair_color': this.hairColor,
        'hair_alpha': String(this.hairAlpha),
        'bokeh_enable': String(this.bokehEnable),
        'bokeh_val': String(this.bokehVal),
        'show_debug': 'false'
      }
      
      console.log('📤 发送参数:', formData)
      
      const uploadTask = uni.uploadFile({
        url: this.apiUrl,
        filePath: this.originalImg,
        name: 'image',
        timeout: 180000,
        formData: formData,
        success: (res) => {
          uni.hideLoading()
          console.log('📥 响应状态:', res.statusCode)
          
          if (res.statusCode === 200) {
            try {
              const data = JSON.parse(res.data)
              console.log('📥 解析后的数据:', JSON.stringify(data).substring(0, 200) + '...')
              
              if (data.status === 'success' && data.image) {
                let base64Data = data.image
                
                if (base64Data.startsWith('data:image')) {
                  this.$set(this, 'resultImg', base64Data)
                } else {
                  this.$set(this, 'resultImg', 'data:image/jpeg;base64,' + base64Data)
                }
                
                this.$forceUpdate()
                console.log('✅ 结果图片已设置，长度:', this.resultImg.length)
                
                setTimeout(() => {
                  uni.showToast({ title: '上妆成功！', icon: 'success' })
                }, 100)
              } else {
                uni.showToast({ title: data.error || '处理失败', icon: 'error' })
                console.error('❌ 后端返回错误:', data)
              }
            } catch (e) {
              console.error('❌ JSON解析失败:', e)
              uni.showToast({ title: '解析响应失败', icon: 'error' })
            }
          } else {
            uni.showToast({ title: `请求失败: ${res.statusCode}`, icon: 'error' })
          }
        },
        fail: (err) => {
          uni.hideLoading()
          console.error('❌ 请求失败:', JSON.stringify(err))
          
          let msg = '网络请求失败'
          if (err.errMsg) {
            if (err.errMsg.includes('timeout')) msg = '请求超时，请重试'
            else if (err.errMsg.includes('fail')) msg = '连接失败，请检查后端服务'
          }
          uni.showToast({ title: msg, icon: 'error' })
        },
        complete: () => {
          this.isLoading = false
        }
      })
      
      uploadTask.onProgressUpdate((res) => {
        console.log(`📊 上传进度: ${res.progress}%`)
      })
    },
    
    previewResult() {
      if (!this.resultImg) {
        uni.showToast({ title: '没有结果图片', icon: 'none' })
        return
      }
      
      uni.previewImage({
        urls: [this.resultImg],
        current: this.resultImg
      })
    },
    
    saveResult() {
      if (!this.resultImg) {
        uni.showToast({ title: '没有可保存的图片', icon: 'none' })
        return
      }
      
      uni.getSetting({
        success: (res) => {
          if (!res.authSetting['scope.writePhotosAlbum']) {
            uni.authorize({
              scope: 'scope.writePhotosAlbum',
              success: () => this.doSaveImage(),
              fail: () => {
                uni.showModal({
                  title: '需要相册权限',
                  content: '请在设置中开启相册权限',
                  confirmText: '去设置',
                  success: (modalRes) => {
                    if (modalRes.confirm) uni.openSetting({})
                  }
                })
              }
            })
          } else {
            this.doSaveImage()
          }
        }
      })
    },
    
    doSaveImage() {
      const fs = uni.getFileSystemManager()
      const fileName = `muse_${Date.now()}.jpg`
      const filePath = `${wx.env.USER_DATA_PATH}/${fileName}`
      
      let base64Data = this.resultImg
      if (base64Data.startsWith('data:image')) {
        base64Data = base64Data.replace(/^data:image\/\w+;base64,/, '')
      }
      
      fs.writeFile({
        filePath,
        data: base64Data,
        encoding: 'base64',
        success: () => {
          uni.saveImageToPhotosAlbum({
            filePath,
            success: () => uni.showToast({ title: '已保存到相册', icon: 'success' }),
            fail: (err) => {
              console.error('保存失败:', err)
              uni.showToast({ title: '保存失败', icon: 'error' })
            }
          })
        },
        fail: (err) => {
          console.error('写入失败:', err)
          uni.showToast({ title: '保存失败', icon: 'error' })
        }
      })
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #fdf4f5 0%, #ffe9ec 100%);
  padding: 20rpx;
  padding-bottom: 40rpx;
}

.header {
  text-align: center;
  padding: 20rpx 0;
}

.title {
  font-size: 44rpx;
  font-weight: 900;
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: block;
}

.subtitle {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
}

.status-tip {
  background: rgba(255, 107, 107, 0.1);
  padding: 16rpx;
  border-radius: 40rpx;
  text-align: center;
  margin-bottom: 20rpx;
}

.status-tip text {
  color: #FF6B6B;
  font-size: 26rpx;
}

.image-area {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20rpx;
  gap: 15rpx;
}

.image-box {
  flex: 1;
  aspect-ratio: 1;
  border-radius: 20rpx;
  background: #fff;
  overflow: hidden;
  box-shadow: 0 6rpx 20rpx rgba(255, 107, 107, 0.12);
  position: relative;
}

.image-box image {
  width: 100%;
  height: 100%;
}

.image-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.5);
  color: #fff;
  text-align: center;
  padding: 8rpx 0;
  font-size: 22rpx;
}

.style-section {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 12rpx;
}

.style-scroll {
  white-space: nowrap;
}

.style-buttons {
  display: inline-flex;
  gap: 12rpx;
  padding: 4rpx 0;
}

.style-btn {
  padding: 14rpx 24rpx;
  background: #fff;
  border-radius: 40rpx;
  font-size: 24rpx;
  color: #666;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  white-space: nowrap;
}

.style-btn.active {
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
  color: #fff;
}

.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: rgba(255,255,255,0.8);
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  backdrop-filter: blur(10rpx);
}

.control-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #333;
}

.control-arrow {
  font-size: 24rpx;
  color: #999;
}

.control-area {
  padding: 0;
  margin-bottom: 20rpx;
}

.param-group {
  background: rgba(255,255,255,0.8);
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  padding: 20rpx;
  backdrop-filter: blur(10rpx);
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 28rpx;
  font-weight: 700;
  color: #333;
}

.slider-box {
  margin: 25rpx 0;
}

.param-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.param-label text {
  font-size: 26rpx;
  color: #555;
}

.param-value {
  color: #FF6B6B;
  font-weight: 600;
}

.color-box {
  margin: 25rpx 0;
}

.color-box > text {
  font-size: 26rpx;
  color: #555;
  display: block;
  margin-bottom: 10rpx;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 15rpx;
  padding: 15rpx 20rpx;
  background: #fff;
  border-radius: 16rpx;
  border: 1rpx solid #eee;
}

.color-display {
  width: 60rpx;
  height: 60rpx;
  border-radius: 12rpx;
  border: 2rpx solid #fff;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.color-text {
  flex: 1;
  font-size: 26rpx;
  color: #333;
}

.color-arrow {
  font-size: 24rpx;
  color: #999;
}

.switch-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25rpx 0;
}

.switch-box text {
  font-size: 26rpx;
  color: #555;
}

.action-section {
  margin-top: 10rpx;
}

.action-section button {
  margin-top: 20rpx;
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 60rpx;
  font-size: 30rpx;
  font-weight: 600;
}

button[type="primary"] {
  background: #fff;
  color: #FF6B6B;
  border: 2rpx solid #FF6B6B;
}

button[type="warn"] {
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
  color: #fff;
  border: none;
  box-shadow: 0 6rpx 16rpx rgba(255, 107, 107, 0.25);
}

.save-buttons {
  display: flex;
  gap: 20rpx;
  margin-top: 20rpx;
}

.save-btn {
  flex: 1;
  background: #fff !important;
  color: #667eea !important;
  border: 2rpx solid #667eea !important;
}

.debug-btn {
  flex: 1;
  background: #fff !important;
  color: #999 !important;
  border: 2rpx solid #ddd !important;
}

/* 🎨 颜色选择器弹窗样式 */
.color-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.color-picker-content {
  width: 100%;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 30rpx;
  max-height: 70vh;
  overflow-y: auto;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.picker-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.picker-close {
  font-size: 40rpx;
  color: #999;
  padding: 10rpx;
}

.color-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.color-item {
  width: 100rpx;
  height: 100rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 3rpx solid transparent;
  transition: all 0.2s;
}

.color-item.active {
  border-color: #FF6B6B;
  transform: scale(1.05);
}

.check-mark {
  color: #fff;
  font-size: 48rpx;
  font-weight: bold;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.3);
}

.custom-color {
  border-top: 1rpx solid #eee;
  padding-top: 30rpx;
}

.custom-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 15rpx;
  display: block;
}

.custom-row {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.custom-row input {
  flex: 1;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 16rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  border: 1rpx solid #eee;
}

.custom-preview {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  border: 2rpx solid #fff;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.apply-btn {
  padding: 0 30rpx;
  height: 80rpx;
  line-height: 80rpx;
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}
</style>
