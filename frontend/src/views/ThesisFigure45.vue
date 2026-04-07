<template>
  <main class="thesis-figure-page">
    <div class="figure-scroll">
      <figure class="figure-sheet">
        <div class="figure-stage">
          <svg class="edge-layer" viewBox="0 0 1560 1040" aria-hidden="true">
            <defs>
              <marker id="arrow-solid" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#5c778d" />
              </marker>
              <marker id="arrow-open" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
                <path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="#7a8da0" stroke-width="1.4" />
              </marker>
            </defs>

            <path
              v-for="line in lifelines"
              :key="`life-${line.x}`"
              class="lifeline"
              :d="`M ${line.x} 92 V 960`"
            />

            <path
              v-for="message in messages"
              :key="message.label"
              class="message-line"
              :class="{ dashed: message.dashed }"
              :d="messagePath(message)"
              :marker-end="message.dashed ? 'url(#arrow-open)' : 'url(#arrow-solid)'"
            />
          </svg>

          <section
            v-for="participant in participants"
            :key="participant.title"
            class="participant-head"
            :style="participantStyle(participant)"
          >
            {{ participant.title }}
          </section>

          <div
            v-for="stage in stages"
            :key="stage.label"
            class="stage-chip"
            :style="boxStyle(stage)"
          >
            {{ stage.label }}
          </div>

          <div
            v-for="fragment in fragments"
            :key="fragment.title"
            class="fragment-box"
            :class="fragment.kind"
            :style="boxStyle(fragment)"
          >
            <span class="fragment-title">{{ fragment.title }}</span>
          </div>

          <div
            v-for="activation in activations"
            :key="`${activation.x}-${activation.y}`"
            class="activation-bar"
            :style="boxStyle(activation)"
          />

          <div
            v-for="message in messages"
            :key="`label-${message.label}`"
            class="message-label"
            :class="{ dashed: message.dashed }"
            :style="messageLabelStyle(message)"
          >
            {{ message.label }}
          </div>

          <div class="stop-note" :style="boxStyle(stopNote)">
            停止轮询
          </div>

          <aside class="legend-panel" :style="boxStyle(legendPanel)">
            <section class="legend-card">
              <h2>真实对应说明</h2>
              <ul>
                <li>发起调度 = POST /dispatch/plans</li>
                <li>轮询状态 = GET /dispatch/plans/{id}</li>
                <li>写中间进度 = 更新 route.geo_json</li>
                <li>写最终结果 = 更新 route / package / plan</li>
              </ul>
            </section>

            <section class="legend-card">
              <h2>状态</h2>
              <ul>
                <li>plan: OPTIMIZING -&gt; READY / COMPLETED</li>
                <li>route: calculating -&gt; optimizing -&gt; optimized</li>
              </ul>
            </section>
          </aside>
        </div>

        <figcaption class="figure-caption">图4.5 调度时序图</figcaption>
      </figure>
    </div>
  </main>
</template>

<script setup lang="ts">
interface Box {
  x: number
  y: number
  width: number
  height: number
}

interface Participant {
  title: string
  centerX: number
}

interface Message {
  label: string
  from: number
  to: number
  y: number
  width: number
  dashed?: boolean
}

interface Fragment extends Box {
  title: string
  kind: 'loop' | 'alt'
}

interface Stage extends Box {
  label: string
}

const participants: Participant[] = [
  { title: '调度页面 SmartDispatch', centerX: 160 },
  { title: 'Dispatch API', centerX: 380 },
  { title: '后台调度任务', centerX: 600 },
  { title: '路径优化模块', centerX: 820 },
  { title: 'SQLite', centerX: 1040 }
]

const lifelines = participants.map((participant) => ({ x: participant.centerX }))

const stages: Stage[] = [
  { x: 28, y: 132, width: 92, height: 36, label: '创建计划' },
  { x: 28, y: 370, width: 92, height: 36, label: '后台准备' },
  { x: 28, y: 496, width: 92, height: 36, label: '路径求解' },
  { x: 28, y: 748, width: 92, height: 36, label: '前端轮询' },
  { x: 28, y: 902, width: 92, height: 36, label: '完成收尾' }
]

const messages: Message[] = [
  { label: '发起调度', from: 0, to: 1, y: 160, width: 76 },
  { label: '创建 plan', from: 1, to: 4, y: 214, width: 76 },
  { label: '返回 plan_id', from: 1, to: 0, y: 268, width: 84, dashed: true },
  { label: '启动后台任务', from: 1, to: 2, y: 322, width: 94 },
  { label: '读取待调度数据', from: 2, to: 4, y: 404, width: 104 },
  { label: '资源不足则结束', from: 2, to: 4, y: 466, width: 104 },
  { label: '执行聚类', from: 2, to: 3, y: 540, width: 72 },
  { label: '预建路线', from: 2, to: 4, y: 602, width: 72 },
  { label: '执行路径优化', from: 2, to: 3, y: 680, width: 94 },
  { label: '写中间进度', from: 2, to: 4, y: 742, width: 84 },
  { label: '轮询状态', from: 0, to: 1, y: 790, width: 72 },
  { label: '查询 plan/routes', from: 1, to: 4, y: 846, width: 116 },
  { label: '写最终结果', from: 2, to: 4, y: 902, width: 82 },
  { label: '返回状态与路线', from: 1, to: 0, y: 958, width: 116, dashed: true }
]

const fragments: Fragment[] = [
  {
    title: 'alt 资源不足',
    kind: 'alt',
    x: 508,
    y: 366,
    width: 602,
    height: 126
  },
  {
    title: 'loop 优化迭代',
    kind: 'loop',
    x: 508,
    y: 488,
    width: 602,
    height: 270
  },
  {
    title: 'loop 轮询',
    kind: 'loop',
    x: 136,
    y: 764,
    width: 984,
    height: 222
  }
]

const activations: Box[] = [
  { x: 372, y: 146, width: 16, height: 840 },
  { x: 592, y: 314, width: 16, height: 614 },
  { x: 1032, y: 204, width: 16, height: 720 }
]

const stopNote: Box = {
  x: 150,
  y: 986,
  width: 100,
  height: 38
}

const legendPanel: Box = {
  x: 1230,
  y: 132,
  width: 290,
  height: 620
}

const boxStyle = ({ x, y, width, height }: Box) => ({
  left: `${x}px`,
  top: `${y}px`,
  width: `${width}px`,
  height: `${height}px`
})

const participantStyle = (participant: Participant) => ({
  left: `${participant.centerX - 88}px`,
  top: '34px',
  width: '176px',
  height: '40px'
})

const messagePath = (message: Message) => {
  const fromX = participants[message.from]?.centerX ?? 0
  const toX = participants[message.to]?.centerX ?? 0

  return `M ${fromX} ${message.y} H ${toX}`
}

const messageLabelStyle = (message: Message) => {
  const fromX = participants[message.from]?.centerX ?? 0
  const toX = participants[message.to]?.centerX ?? 0
  const center = (fromX + toX) / 2

  return {
    left: `${center - message.width / 2}px`,
    top: `${message.y - 22}px`,
    width: `${message.width}px`
  }
}
</script>

<style scoped>
.thesis-figure-page {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(180deg, #eef2f5 0%, #e7ecef 100%);
  color: #233645;
}

.figure-scroll {
  overflow-x: auto;
}

.figure-sheet {
  width: 1560px;
  margin: 0 auto;
}

.figure-stage {
  position: relative;
  width: 1560px;
  height: 1040px;
  border: 1px solid #c9d1d9;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 249, 251, 0.98)),
    repeating-linear-gradient(
      90deg,
      rgba(201, 209, 217, 0.05) 0,
      rgba(201, 209, 217, 0.05) 1px,
      transparent 1px,
      transparent 40px
    );
  box-shadow: 0 18px 40px rgba(35, 54, 69, 0.08);
  font-family: 'STSong', 'SimSun', 'Songti SC', serif;
}

.edge-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.lifeline {
  fill: none;
  stroke: #a5b3be;
  stroke-width: 1.5;
  stroke-dasharray: 6 8;
}

.message-line {
  fill: none;
  stroke: #5c778d;
  stroke-width: 2;
}

.message-line.dashed {
  stroke: #7a8da0;
  stroke-dasharray: 8 7;
}

.participant-head {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  border: 1.5px solid #90a2b1;
  border-radius: 12px;
  background: linear-gradient(180deg, #fbfcfd, #f1f5f7);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.25;
  text-align: center;
  box-shadow: 0 6px 16px rgba(35, 54, 69, 0.05);
}

.stage-chip {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(122, 141, 166, 0.65);
  border-radius: 12px;
  background: rgba(243, 246, 248, 0.98);
  color: #516577;
  font-size: 12px;
  font-weight: 700;
}

.fragment-box {
  position: absolute;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.42);
}

.fragment-box.loop {
  border: 1.5px solid rgba(122, 141, 166, 0.86);
}

.fragment-box.alt {
  border: 1.5px dashed rgba(122, 141, 166, 0.92);
  background: rgba(248, 249, 251, 0.8);
}

.fragment-title {
  position: absolute;
  left: 14px;
  top: -12px;
  padding: 0 8px;
  background: #f6f8fa;
  color: #4b657b;
  font-size: 12px;
  font-family: 'Times New Roman', Times, serif;
}

.activation-bar {
  position: absolute;
  border: 1px solid rgba(76, 120, 168, 0.35);
  border-radius: 8px;
  background: rgba(76, 120, 168, 0.12);
}

.message-label {
  position: absolute;
  padding: 3px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.97);
  color: #38546b;
  font-size: 12px;
  line-height: 1.25;
  text-align: center;
  box-shadow: 0 4px 10px rgba(35, 54, 69, 0.04);
}

.message-label.dashed {
  color: #647889;
}

.stop-note {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #c96a28;
  border-radius: 12px;
  background: rgba(255, 248, 241, 0.96);
  color: #8c4e24;
  font-size: 12px;
}

.legend-panel {
  position: absolute;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legend-card {
  border: 1px solid #c9d1d9;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px 18px;
  box-shadow: 0 8px 18px rgba(35, 54, 69, 0.05);
}

.legend-card h2 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #35516a;
}

.legend-card ul {
  margin: 0;
  padding-left: 18px;
  color: #486073;
  font-size: 11px;
  line-height: 1.75;
}

.figure-caption {
  margin: 28px 0 0;
  text-align: center;
  font-size: 20px;
  color: #1e2f3c;
  font-family: 'STSong', 'SimSun', 'Songti SC', serif;
}

@media (max-width: 720px) {
  .thesis-figure-page {
    padding: 12px;
  }
}
</style>
