<template>
  <v-form @submit.prevent="validate" ref="form" v-model="isValid">
    <v-card-text>
      <v-card max-height="500" style="overflow-y:scroll;">
        <v-card-text class="tos-text">
          <terms-of-service-content />
        </v-card-text>
      </v-card>
    </v-card-text>

    <v-row>
      <v-col cols="7"></v-col>
      <v-col>
        <v-switch
          color="button"
          v-model="fields.tos.value"
          v-bind="fields.tos"
        ></v-switch>
        <v-switch
          color="button"
          v-model="fields.tos2.value"
          v-bind="fields.tos2"
        ></v-switch>
      </v-col>
    </v-row>

    <v-card-actions>
      <v-btn
        color="button"
        @click="() => $emit('back')"
        :disabled="isSubmitting"
        >Back</v-btn
      >
      <v-spacer />
      <v-btn
        color="button"
        type="submit"
        :disabled="
          isSubmitting ||
            !isValid ||
            fields.password.value != fields.passwordConfirm.value
        "
      >
        Create Account
        <v-progress-circular
          size="14"
          class="ml-3"
          indeterminate
          v-if="isSubmitting"
        />
      </v-btn>
    </v-card-actions>
  </v-form>
</template>

<script>
import TermsOfServiceContent from "@/components/TermsOfServiceContent";

export default {
  name: "register-step-4",
  props: ["fields"],
  components: { TermsOfServiceContent },
  methods: {
    async submit() {
      if (this.isSubmitting) {
        return;
      }
      this.isSubmitting = true;
      const cb = () => {
        this.isSubmitting = false;
      };
      this.$emit("submit", cb);
    },
    validate() {
      if (this.$refs.form.validate()) {
        this.submit();
      }
    }
  },
  data() {
    return {
      isValid: false,
      isSubmitting: false
    };
  }
};
</script>

<style lang="scss" scoped>
.tos-text {
  background-color: rgba(255, 255, 255, 0.9);
  font-family: "Barlow", sans-serif;
  color: #333 !important;
}
</style>
