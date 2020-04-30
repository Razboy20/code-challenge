<template>
  <v-card
    class="ballot ballot-card"
    light
    :class="{ voted }"
    :elevation="voted ? 5 : 0"
    @click="$emit('click')"
  >
    <div class="circle">
      {{ initials }}
    </div>
    <div class="username">
      {{ username }}
    </div>
    <div class="vote-count">
      {{ votes }} {{ votes == 1 ? "vote" : "votes" }}
    </div>

    <v-btn elevation="0" color="cwhqBlue" block>See Code</v-btn>
    <v-btn elevation="0" color="primary" class="votedBtn" block
      >{{ voted ? "Voted" : "Vote"
      }}<v-icon class="ml-2" v-if="voted"
        >mdi-checkbox-marked-circle</v-icon
      ></v-btn
    >
  </v-card>
</template>

<script>
export default {
  props: [
    "display",
    "firstName",
    "id",
    "lastName",
    "numVotes",
    "text",
    "username",
    "value",
    "initials",
    "update",
    "hasVoted"
  ],
  data() {
    return {
      votes: this.numVotes,
      voted: this.hasVoted ? true : false
    };
  },
  watch: {
    update() {
      if (this.update.id !== this.id) return;
      this.votes = this.update.numVotes;
      this.voted = this.update.hasVoted;
    }
  }
};
</script>

<style lang="scss" scoped>
.voted {
  border-color: #a4deb0 !important;
  .votedBtn {
    background-color: #00a822 !important;
  }
  &:hover {
    border-color: #6cee86 !important;
  }
}
</style>
