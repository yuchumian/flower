import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/router'
import TDesign from 'tdesign-mobile-vue';
const app = createApp(App)
app.use(TDesign);
app.use(createPinia())
app.use(router)
app.mount('#app')
