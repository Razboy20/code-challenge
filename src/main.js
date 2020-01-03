import Vue from "vue";
import App from "./App.vue";
import router from "./plugins/router";
import vuetify from "./plugins/vuetify";
import store from "./store";
import "@/styles/styles.scss";
import { auth } from "@/api";

Vue.config.productionTip = false;

(async function() {
  auth.onAuthStateChange(function() {
    store.dispatch("User/refresh");
  });

  await auth.autoLogin();

  new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
  }).$mount("#app");
})();