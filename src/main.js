
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex';

import App from './App.vue'
import vuetify from './plugins/vuetify';

Vue.config.productionTip = true

Vue.use(VueRouter)
Vue.use(Vuex);

const store = new Vuex.Store({

  state: {
    Authorization: localStorage.getItem('Authorization') ?
        localStorage.getItem('Authorization') :
        '',
    id: localStorage.getItem('id') ? localStorage.getItem('id') : '',

  },

  mutations: {
    changeLogin(state, user) {
      state.Authorization = user.Authorization;
      state.id = user.id;
      localStorage.setItem('Authorization', user.Authorization);
      localStorage.setItem('id', user.id);
    }
  }
});

import Login from './components/Login';
import Exam from './components/Exam';
const routes = [
  {path: '/', component: Login},
  {path: '/exam', component: Exam},
];
const router = new VueRouter({routes});

router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    next();
  } else {
    let token = localStorage.getItem('Authorization');
    if (token === 'null' || token === '') {
      next('/');
    } else {
      next();
    }
  }
});

new Vue({vuetify, render: h => h(App), store, router}).$mount('#app')
