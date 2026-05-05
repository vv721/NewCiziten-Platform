<script setup>
import { ref, watch } from 'vue'
import MapContainer from './MapContainer.vue'
import { uiState } from '@/store/uiState'
import InfoTrace from './InfoTrace.vue'
import ServiceNavigation from './ServiceNavigation.vue'

const carouselRef = ref(null)

const carouselSlide = newIndex => {
    activeCarouselIndex.value = newIndex
}

let isScrolling = false

watch(
  () => uiState.currentCarouselIndex,
  (newIndex) => {
    if (carouselRef.value) {
      carouselRef.value.setActiveItem(newIndex)
    }
  }
)

</script>

<template>
    <div class="carousel-wrapper">
        <el-carousel
         ref="carouselRef"
         :autoplay="false"
         arrow="never"
         indicator-position="none"
         height="100%">
            <el-carousel-item class="feature1">
                <InfoTrace />
            </el-carousel-item>
            <el-carousel-item class="feature2">
                <MapContainer />
            </el-carousel-item>
            <el-carousel-item class="feature3">
                <ServiceNavigation />
            </el-carousel-item>
        </el-carousel>
    </div>
</template>

<style scoped>
.carousel-wrapper {
    height: 100%;
    width: 100%;
}
.el-carousel {
    height: 100%;
}
.el-carousel__item {
    height: 100%;
    display: flex;
    align-items: stretch;
}
.feature2 {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
}
</style>