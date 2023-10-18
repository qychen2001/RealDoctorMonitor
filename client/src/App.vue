<template>
  <div>
    <!-- Sticky Header -->
    <el-header class="sticky-header">
      <div class="site-title">
        睿医网信办
      </div>
      <el-menu mode="horizontal">
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
    <el-footer class="site-footer">© 2023 由<a href="https://qiyuan-chen.github.io/">陈启源</a>开发。感谢杜邦支持。</el-footer>
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
  background-color: white;
  height: 80px;
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
  padding-top: 30px;
}
</style>