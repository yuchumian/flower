<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  position: relative;
  font-weight: normal;
}


#app {
  margin: 0 auto;
  padding: 0.5rem;
  height: 100vh;
  width: 100%;
}
</style>
