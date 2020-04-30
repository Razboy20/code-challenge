<template>
  <div
    id="loadScreen"
    :class="{ hide: isLoaded, 'display-none': isHidden }"
  ></div>
</template>

<script>
export default {
  props: {
    loaded: Boolean
  },
  data() {
    return {
      isLoaded: false,
      isHidden: false
    };
  },
  watch: {
    loaded() {
      if (this.loaded && !this.isHidden) this.hide();
    }
  },
  methods: {
    hide() {
      if (this.isHidden) return;
      this.isLoaded = true;
      setTimeout(() => {
        this.isHidden = true;
      }, 200);
    }
  },
  mounted() {
    setTimeout(this.hide, 1000);
  }
};
</script>

<style lang="scss" scoped>
#loadScreen {
  background-color: white;
  width: 100vw;
  height: 100vh;
  position: fixed;
  left: 0px;
  top: 0px;
  z-index: 100;
  opacity: 1;
  transition: opacity 0.2s ease-in-out;
}
.display-none {
  display: none;
}
.hide {
  opacity: 0 !important;
}
</style>
