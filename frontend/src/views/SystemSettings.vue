<template>
  <div class="settings-container glass-card">
    <el-tabs tab-position="left" class="settings-tabs">
      <el-tab-pane label="🏢 配送站设置">
        <div class="pane-wrap">
          <div class="pane-header">
            <h2>配送站信息管理</h2>
            <p>管理您的物理配送中心坐标及服务半径</p>
          </div>
          
          <div class="glass-form-box">
            <el-form :model="stationForm" label-position="top">
              <el-form-item label="站点名称">
                <el-input v-model="stationForm.name" />
              </el-form-item>
              <el-form-item label="详细地址">
                <el-input v-model="stationForm.address" type="textarea" :rows="3" />
              </el-form-item>
              <div class="form-row">
                <el-form-item label="纬度 (Latitude)" class="flex-1">
                  <el-input v-model="stationForm.lat" />
                </el-form-item>
                <el-form-item label="经度 (Longitude)" class="flex-1">
                  <el-input v-model="stationForm.lng" />
                </el-form-item>
              </div>
              <el-form-item label="服务半径 (km)">
                <el-slider v-model="stationForm.radius" :min="1" :max="100" />
              </el-form-item>
              <el-button type="primary" round class="save-btn">更新站点信息</el-button>
            </el-form>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="🤖 算法精细调优">
        <div class="pane-wrap">
          <div class="pane-header">
            <h2>核心算法引擎配置</h2>
            <p>调整 K-Means 与 遗传算法 (GA) 的计算深度</p>
          </div>

          <div class="settings-grid">
            <div class="settings-group glass-card">
              <div class="group-title">K-Means 参数</div>
              <div class="g-item">
                <span>最大迭代次数</span>
                <el-input-number v-model="algo.kmeansMax" size="small" />
              </div>
              <div class="g-item">
                <span>收敛阈值 (Tolerance)</span>
                <el-input v-model="algo.kmeansTol" size="small" style="width: 100px" />
              </div>
            </div>

            <div class="settings-group glass-card">
              <div class="group-title">遗传算法 (GA) 参数</div>
              <div class="g-item">
                <span>种群规模 (Population)</span>
                <el-input-number v-model="algo.gaPop" size="small" />
              </div>
              <div class="g-item">
                <span>变异概率 (Mutation)</span>
                <el-slider v-model="algo.gaMutation" :max="0.5" :step="0.01" style="width: 150px" />
              </div>
            </div>
          </div>
          <el-button type="primary" round class="save-btn mt-4">同步算法配置</el-button>
        </div>
      </el-tab-pane>

      <el-tab-pane label="🎨 视觉与偏好">
        <div class="pane-wrap">
          <div class="pane-header">
            <h2>视觉外观定制</h2>
            <p>调整系统的配色方案与视觉呈现</p>
          </div>
          
          <div class="glass-form-box">
             <el-form label-position="left" label-width="120px">
                <el-form-item label="全局主题模式">
                  <el-segmented v-model="theme" :options="['Light', 'Dark', 'Auto']" />
                </el-form-item>
                <el-form-item label="强调色 (Primary)">
                   <el-color-picker v-model="primaryColor" />
                </el-form-item>
                <el-form-item label="玻璃模糊度 (Blur)">
                   <el-slider v-model="blurValue" :max="40" />
                </el-form-item>
             </el-form>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const stationForm = reactive({
  name: '上海浦东配送中心',
  address: '上海市浦东新区张江高科园区...',
  lat: '31.2304',
  lng: '121.4737',
  radius: 50
})

const algo = reactive({
  kmeansMax: 100,
  kmeansTol: '0.0001',
  gaPop: 100,
  gaMutation: 0.1
})

const theme = ref('Light')
const primaryColor = ref('#667eea')
const blurValue = ref(20)
</script>

<style scoped>
.settings-container { height: 100%; border-radius: 24px; overflow: hidden; }
.settings-tabs { height: 100%; }
.settings-tabs :deep(.el-tabs__header) { margin-right: 0; background: rgba(0,0,0,0.02); padding-top: 20px; }
.settings-tabs :deep(.el-tabs__item) { height: 50px; border-radius: 0 12px 12px 0; margin-bottom: 5px; }
.settings-tabs :deep(.el-tabs__item.is-active) { background: rgba(102, 126, 234, 0.1); }

.pane-wrap { padding: 40px; max-width: 800px; }
.pane-header { margin-bottom: 40px; }
.pane-header h2 { margin: 0 0 8px 0; font-size: 24px; color: #2d3748; }
.pane-header p { margin: 0; color: #718096; font-size: 14px; }

.glass-form-box { background: rgba(0,0,0,0.02); padding: 30px; border-radius: 20px; border: 1px solid rgba(0,0,0,0.03); }

.form-row { display: flex; gap: 20px; }
.flex-1 { flex: 1; }

.save-btn { padding: 0 30px; height: 44px; font-weight: 700; margin-top: 20px; }

.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.settings-group { padding: 24px; }
.group-title { font-weight: 700; margin-bottom: 20px; color: #4a5568; }
.g-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-size: 14px; }

.mt-4 { margin-top: 40px; }
</style>