<template>
    <div class="container">
        <div v-for="(gpus, ip) in gpuData" :key="ip">
            <h3>{{ ip }}</h3>
            <el-table :data="gpus" style="width: 100%">
                <el-table-column prop="name" label="GPU型号"></el-table-column>

                <el-table-column label="总显存">
                    <template #default="scope">
                        {{ formatMemory(scope.row.memory_total) }}
                    </template>
                </el-table-column>

                <el-table-column label="已用显存">
                    <template #default="scope">
                        {{ formatMemory(scope.row.memory_used) }}
                    </template>
                </el-table-column>

                <el-table-column prop="Usage_rate" label="使用率"></el-table-column>
                <el-table-column prop="user_display" label=""></el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
    name: 'GpuMonitor',
    setup() {
        const gpuData = ref({});
        let intervalId = null;

        const fetchData = async () => {
            try {
                const response = await fetch("http://192.168.0.35:8000/gpu-monitor");
                if (response.ok) {
                    gpuData.value = await response.json();
                }
            } catch (error) {
                console.error("Error fetching GPU data:", error);
            }
        };

        onMounted(() => {
            fetchData();
            intervalId = setInterval(fetchData, 1000);
        });

        onBeforeUnmount(() => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });

        const formatMemory = (memory) => {
            return (memory / 1024).toFixed(2) + ' GB';
        };

        return {
            gpuData,
            fetchData,
            formatMemory
        };
    }
}
</script>



<style scoped>
.container {
    width: 90%;
    margin: 40px auto;
    padding: 20px;
    border: 1px solid #ebeef5;
    box-shadow: 0px 0px 12px #ebeef5;
}
</style>
