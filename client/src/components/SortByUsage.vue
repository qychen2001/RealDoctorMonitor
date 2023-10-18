<template>
    <div class="container">
        <el-table :data="sortedItems" style="width: 100%" default-expand-all>
            <el-table-column prop="user" label="姓名"></el-table-column>
            <el-table-column prop="gpu_count" label="使用数量" sortable></el-table-column>

            <el-table-column type="expand">
                <template #default="props">
                    <el-table :data="props.row.details" style="width: 100%">
                        <el-table-column prop="server" label="服务器地址"></el-table-column>
                        <el-table-column prop="gpu_name" label="GPU型号"></el-table-column>

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

                        <el-table-column prop="usage_rate" label="使用率"></el-table-column>
                    </el-table>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
    name: 'SortByUsage',
    setup() {
        const sortedItems = ref([]);
        let intervalId = null;

        const fetchData = async () => {
            try {
                const response = await fetch("http://192.168.0.35:8000/sort-by-user");
                if (response.ok) {
                    sortedItems.value = await response.json();
                }
            } catch (error) {
                console.error("Error fetching GPU data:", error);
            }
        };

        onMounted(() => {
            fetchData();
            intervalId = setInterval(fetchData, 30000);
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
            sortedItems,
            fetchData,
            formatMemory
        };
    }
}
</script>

<style scoped>
.container {
    width: 80%;
    margin: 40px auto;
    padding: 20px;
    border: 1px solid #ebeef5;
    box-shadow: 0px 0px 12px #ebeef5;
}
</style>
