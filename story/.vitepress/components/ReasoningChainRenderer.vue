<template>
    <div class="reasoning-chain">
        <div @click="toggleShow" class="chain-title">推理模型思维链<div :style="{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }"   class="chain-toggle-icon"><svg width="10" height="6" viewBox="0 0 10 6"
                    fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M5.786 4.167L2.765 1.259c-.416-.4-.985-.482-1.273-.183-.287.298-.183.864.233 1.264l3.021 2.908c.416.4.986.482 1.273.184.287-.299.183-.865-.233-1.265z"
                        fill="currentColor"></path>
                    <path
                        d="M8.197 1.206L5.288 4.208c-.4.413-.484.982-.187 1.27.298.289.864.187 1.265-.227L9.274 2.25c.401-.414.485-.983.187-1.271-.297-.288-.863-.187-1.264.227z"
                        fill="currentColor"></path>
                </svg></div>
        </div>
        <div v-if="isExpanded" class="chain-steps">
            <div class="chain-separator"></div>
            <slot></slot>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

// 定义状态变量
const isExpanded = ref(false);
const toggleShow = () => {
  isExpanded.value =!isExpanded.value;
};
</script>

<style scoped>
/* .reasoning-chain { */
    /* padding: 10px; */
    /* border: 1px solid #ccc; */
    /* border-radius: 4px; */
    /* background-color: #f9f9f9; */
/* } */

.chain-title {
    color: #333;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    width: fit-content;
    width: -moz-fit-content;
    margin-bottom: 12px;
    background-color: #f5f5f5;
    padding: 7px 14px;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    border-radius: 10px;
    justify-content: center;
    align-items: center;
    line-height: 18px;
}
.chain-title:hover{
    background-color: #ededed;
}

.chain-title .chain-toggle-icon{
    cursor: pointer;

    /* font-size: 10px;
    width: 10px;
    height: 10px; */
    /* transform: rotate(180deg); */

    line-height: 0;
    display: inline-flex;

    margin-left: 6px;
}

.chain-steps {
    padding: 10px;
    color: #8b8b8b;
    white-space: pre-wrap;
    margin: 0;
    padding: 0 0 0 13px;
    line-height: 26px;
    position: relative;
    font-size: 14px;

}

.chain-steps .chain-separator {
    border-left: 2px solid #e5e5e5;
    height: calc(100% - 10px);
    margin-top: 5px;
    position: absolute;
    top: 0;
    left: 0;
}
</style>