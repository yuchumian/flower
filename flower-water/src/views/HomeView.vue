<script  lang="ts">
import { ref, defineComponent, onMounted, onUnmounted } from 'vue';

export default defineComponent({
  setup() {
    const initConfig = ref({
      run: false,
      prvWateringTime:0,
      waterTime:1.5,
      auto:false,
      lastTime:'',
      status:'',
      humidity: 0 
    })
    const timmer = ref(0);
    onMounted(() => {
      getInitConfig()
      timmer.value = setInterval(()=>{getInitConfig()},5000);
    });
    onUnmounted(() => {
      if(timmer.value>0){
        clearInterval(timmer.value);
      }
      timmer.value = 0;
    });
    const visible = ref(false);
    const checked = ref(true);
    const checkTitle = ref('自动浇花');
    const msg = ref('');
    const showMsg = (data: any) => {
      if (data['msg']) {
        msg.value = data['msg'];
        visible.value = true;
      }
    }
    const getInitConfig = ()=>{
       fetch(`/api/auto/init`).then((res: any) => {
        return res.json()
      }).then((data: any) => {
        initConfig.value = { ...data }
      })
    }
    const onCheckChange = ($event: boolean) => {
      checkTitle.value = $event ? '自动浇花' : '手动浇花'
      const type_mode = $event ? 0 : 1
      fetch(`/api/auto/change/${type_mode}`).then((res: any) => {
        return res.json()
      }).then((data: any) => {
        showMsg(data)
        getInitConfig()
      })
    };
    const waterTimeOnChange = ($event: number) => {
      console.log($event)
      initConfig.value.waterTime = Number($event.toFixed(2))
      fetch(`/api/auto/time/${initConfig.value.waterTime}`).then((res: any) => {
        return res.json()
      }).then((data: any) => {
        showMsg(data)
        getInitConfig()
      })
    }
    const closeWatering = ($event: any) => {
      fetch(`/api/auto/close`).then((res: any) => {
        return res.json()
      }).then((data: any) => {
        showMsg(data)
        getInitConfig()
      })
    }
    return {
      getInitConfig,
      initConfig,
      msg,
      visible,
      checked,
      onCheckChange,
      checkTitle,
      waterTimeOnChange,
      closeWatering
    };
  },
});
</script>

<template>
  <div class="content">
    <div class="content-info">
      <div class="content-info-view" :style="{'background-color': (initConfig.status==='潮湿'?'greenyellow':'#E34D59')}"><div>{{initConfig.status}}</div><div>湿度：{{initConfig.humidity.toFixed(2)+'%'}}</div></div>
      <div class="content-info-text">
        <div>自动状态：{{initConfig?.auto?'开启':'关闭'}}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 上次浇水时长：{{initConfig?.prvWateringTime}}s</div>
        <div>最后浇水时间：{{initConfig.lastTime}}</div>
      </div>
    </div>
    <t-cell :title="checkTitle">
      <t-switch v-model="initConfig.auto" @change="onCheckChange"> </t-switch>
    </t-cell>
    <t-divider></t-divider>
    <div class="slider_cell">
      <div class="slider_item">
        <span style="font-size: small;">浇水时长</span>
        <t-slider v-model="initConfig.waterTime" :min="0" :max="5" :step="0.1" @change="waterTimeOnChange" />
      </div>
      <div class="slider_value">{{ initConfig.waterTime }}s</div>
    </div>
    <t-divider></t-divider>
    <t-button theme="danger" size="medium" @click="closeWatering" round>关闭</t-button>
  </div>
  <t-message v-model="visible" :content="msg" />
</template>
<style  scoped="true">
.slider_cell {
  display: flex;
  flex-wrap: nowrap;
  width: 98%;
}

.slider_item {
  width: 92%;
}

.slider_value {
  width: 8%;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  align-content: center;
  justify-content: center;
  height: 100%;
  overflow: hidden;
}

.content-info {
  height: 20rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  text-align: center;
  align-items: center;
  align-content: center;

}

.content-info-view {
  height: 15rem;
  width: 15rem;
  border-radius: 50%;
  box-shadow: rgba(0, 114, 228, 0.2) 0px 8px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.content-info-text {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  font-size: 12px;
}
</style>
