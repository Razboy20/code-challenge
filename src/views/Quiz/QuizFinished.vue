<template>
  <div class="mt-6">
    <v-row justify="center">
      <quiz-scroll>
        <template v-slot:title>Congratulations!</template>
        <template v-slot:default>
          <div style="padding-left:130px; padding-right: 130px;">
            Congratulations young pilgrim!
            <br />
            <br />
            You've qualified for the final round of The Dragon Quest.
            <br /><br />
            To win the grand prize of $100 and a free STEAM access code from
            Endless, come back when the voting period begins, April 26 at 5:00
            PM CT, to gather votes and cast your vote on who you think has the
            best solution for the final answer.
            <br /><br />
            The player with the highest number of votes will be crowned the
            champion on May 1. Will you be the champion …
            <br /><br />Good luck! <br /><br />
            <v-btn :to="{ name: 'voting' }" color="white" light
              >Cast Your Votes Here</v-btn
            ><br />
            <v-btn
              class="mr-3 mt-5"
              :style="{ backgroundColor: 'white !important' }"
              x-large
              color="blue"
              href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fcodewizardshq.com%2Fchallenge%2F&amp;src=sdkpreparse"
              icon
              ><v-icon>mdi-facebook</v-icon></v-btn
            >
            <v-btn
              class="mt-5"
              :style="{ backgroundColor: 'white !important' }"
              x-large
              color="blue"
              href="https://twitter.com/intent/tweet?text=The%20Dragon%20Quest%20%E2%80%93%20Code%20Challenge&url=https%3A%2F%2Fcodewizardshq.com%2Fchallenge%2F&original_referer="
              icon
              ><v-icon>mdi-twitter</v-icon></v-btn
            >
          </div>
        </template>
      </quiz-scroll>
    </v-row>
  </div>
</template>

<script>
import QuizScroll from "@/components/QuizScroll";
export default {
  name: "quiz",
  components: {
    QuizScroll
  },
  mounted() {}
};
</script>
