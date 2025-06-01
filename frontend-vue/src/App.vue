<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f9fafb;
  color: #1f2937;
  margin: 0;
  padding: 0;
}

h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
  margin: 0;
}

h1 {
  color: #2f80ed;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5em;
}

h2 {
  color: #4f4f4f;
  font-size: 1.5rem;
  margin-bottom: 0.5em;
}

:root {
  --darkGrey: #4f4f4f;
  --midGrey: #a9a9a9;
  --lightGrey: #bdbdbd;
  --deepBlue: #2f80ed;
  --lightBlue: #f6f8fb;
  --white: #ffffff;
  --borderBlue: #97bef4;
}
</style>
