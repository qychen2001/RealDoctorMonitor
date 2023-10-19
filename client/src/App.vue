<template>
  <div>
    <!-- Sticky Header -->
    <el-header class="sticky-header">
      <div class="site-title">
        睿医网信办
      </div>
      <p class="site-p">这个项目由<a href="https://qiyuan-chen.github.io/">陈启源</a>开发。感谢杜邦的支持。受限于后端实现与资源部署限制，现在版本的更新较慢（大概五秒更新一次）。代码已经在<a
          href="https://github.com/qiyuan-chen/RealDoctorMonitor">Github</a>开源，欢迎大家提出建议和改进！</p>
      <el-menu mode="horizontal" :default-active="'1'">
        <el-menu-item index="1" @click="activeComponent = 'gpu-monitor'">各服务器GPU占用情况</el-menu-item>
        <el-menu-item index="2" @click="activeComponent = 'sort-by-usage'">按使用量排序</el-menu-item>
      </el-menu>
    </el-header>

    <!-- Main Content -->
    <el-main class="content-with-padding">
      <keep-alive>
        <component :is="activeComponent" />
      </keep-alive>
    </el-main>

    <!-- Footer -->
    <el-footer class="site-footer">© 2023 浙大睿医</el-footer>
  </div>
</template>

<script>
import GpuMonitor from './components/GpuMonitor.vue';
import SortByUsage from './components/SortByUsage.vue';

import { ref } from 'vue';

export default {
  name: 'App',
  components: {
    GpuMonitor,
    SortByUsage
  },
  setup() {
    const activeComponent = ref('gpu-monitor'); // 默认显示 GPU Monitor

    return {
      activeComponent,
    };
  },
};
</script>

<style scoped>
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: white; /* 确保背景颜色为不透明的白色 */
  height: 120px;
}


.site-title {
  font-size: 30px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
  color: dodgerblue;
}

.site-footer {
  font-size: 15px;
  margin-bottom: 20px;
  text-align: center;
}

.content-with-padding {
  padding-top: 40px;
}

.site-p {
  background-color: white;
}
</style>