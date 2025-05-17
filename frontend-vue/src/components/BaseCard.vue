<template>
  <div class="dashboard-card">
    <div v-if="$slots.header" class="flex justify-between items-center mb-4">
      <div>
        <slot name="header"></slot>
      </div>
      <div v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div>
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="mt-4">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseCard'
}
</script> 