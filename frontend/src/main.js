import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css' 
// Si instalaste primeicons, añade esta línea:
// import 'primeicons/primeicons.css'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')