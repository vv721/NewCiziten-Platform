<script setup>
import ChatArea from '@/modules/ChatArea/ChatArea.vue';
import LeftSidebar from '@/modules/LeftSidebar/LeftSidebar.vue';
import RightSidebar from '@/modules/RightSidebar/RightSidebar.vue';
</script>

<template>
    <div class="layout-container">
        <div class="left-sidebar">
            <LeftSidebar />
        </div>
        <div class="center-chat">
            <ChatArea />
        </div>
        <div class="right-sidebar">
            <RightSidebar />
        </div>
    </div>
</template>

<style scoped>
    .layout-container {
        display: flex;
        height: 100vh;
        flex-direction: row;
    }
    .center-chat {
        flex: 1;
    }
    .left-sidebar {
        width: 15%;
        background-color: #f8fafc;
    }
    .right-sidebar {
        width: 20%;
        background-color: #bccaf0;
    }
</style>
