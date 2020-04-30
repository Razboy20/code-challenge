<template>
  <div>
    <v-dialog v-model="isOpen">
      <v-card
        class="ballot ballot-modal"
        height="600"
        color="white"
        light
        v-if="isOpen"
      >
        <v-row class="main-row" no-gutters>
          <v-col cols="3" sm="12" md="3" class="left">
            <div class="circle mb-2">
              {{ initials }}
            </div>
            <div class="username mb-1">
              {{ username }}
            </div>
            <div class="votes"><span>Votes:</span> {{ votes }}</div>
            <hr />
            <v-form lazy-validation @submit.prevent="submit">
              <v-btn
                block
                tile
                color="cwhqBlue"
                type="submit"
                :disabled="isSubmitting"
                >{{ voteText }}</v-btn
              >
            </v-form>
          </v-col>
          <v-col class="right">
            <pre
              v-highlightjs="sourceCode"
            ><code :class="codeType"></code></pre>
          </v-col>
        </v-row>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showError" max-width="600">
      <v-card color="white" light v-if="isOpen">
        <v-card-title>
          Uh oh something went wrong.
        </v-card-title>
        <v-card-text>
          {{ errorMessage }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="cwhqBlue" tile text @click="showError = false"
            >Okay</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import * as api from "@/api";
import { User } from "@/store";
import "highlight.js/styles/darcula.css";

export default {
  data() {
    return {
      showSuccess: false,
      showError: false,
      errorMessage: "",
      isOpen: this.value,
      isSubmitting: false,
      votes: this.numVotes,
      voted: this.hasVoted
    };
  },
  computed: {
    ...User.mapState(),
    isPython() {
      const re = new RegExp(/print\s*\(/g);
      return re.test(this.text);
    },
    instructionComments() {
      if (this.isPython) {
        return `
# A prime number is a number that is divisible only by itself and 1 (e.g. 2, 3, 5, 7, 11).
# I want you to create a computer program, written in Python that does the following; 
# find all prime numbers < 1000
# add all those prime numbers up and display the result


`;
      } else {
        return `
// A prime number is a number that is divisible only by itself and 1 (e.g. 2, 3, 5, 7, 11).
// I want you to create a computer program, written in Python that does the following; 
// find all prime numbers < 1000
// add all those prime numbers up and display the result


`;
      }
    },
    sourceCode() {
      return this.instructionComments + this.text.replace(";output", ";");
    },
    codeType() {
      return this.isPython ? "python" : "javascript";
    },
    voteText() {
      return this.voted ? "Revoke Vote" : "Vote";
    }
  },
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
    "hasVoted"
  ],
  watch: {
    isOpen() {
      if (this.isOpen != this.value) {
        this.$emit("input", this.isOpen);
      }
    },
    value() {
      if (this.isOpen != this.value) {
        this.isOpen = this.value;
      }
    },
    numVotes() {
      this.votes = this.numVotes;
    },
    hasVoted() {
      this.voted = this.hasVoted;
    }
  },
  methods: {
    async submit() {
      if (this.isSubmitting) {
        return;
      }
      this.isSubmitting = true;

      try {
        if (!this.voted) {
          // await api.voting.vote(this.id);
          this.votes++;
          this.voted = true;
        } else {
          // await api.voting.unvote(this.id);
          this.votes--;
          this.voted = false;
        }
        this.$emit("updateVotes", this.id, this.votes, this.voted);
      } catch (err) {
        this.errorMessage = err.message;
        this.showError = true;
      }
      this.isSubmitting = false;
    }
  }
};
</script>
