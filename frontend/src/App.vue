<template>
  <Dashboard />
</template>

<script setup>
import Dashboard from './views/Dashboard.vue'
</script>

<style>
/* Los estilos que ya tienes en App.vue están perfectos, déjalos abajo */
body, html {
  margin: 0;
  padding: 0;
  background-color: #050505;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #222;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #333;
}

/* Animación de entrada para los nuevos eventos */
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.animate-in {
  animation: fadeIn 0.4s ease-out forwards;
}
</style>