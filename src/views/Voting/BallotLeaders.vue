<template>
  <v-container>
    <v-row>
      <v-col>
        <h2 class="ballot-header">
          Today's Leaders
        </h2>
      </v-col>
    </v-row>
    <v-row justify="center" v-if="isLoading">
      <v-col class="text-center">
        <v-progress-circular
          class="mt-6"
          color="cwhqBlue"
          size="100"
          width="10"
          indeterminate
        />
      </v-col>
    </v-row>
    <v-row justify="center" v-else>
      <ballot-card
        v-for="(item, i) in pageData.items"
        :key="i"
        v-bind="item"
        v-bind:update="updateModal"
        @click="showCode(item)"
      />
    </v-row>
    <code-modal
      v-bind="this.item"
      v-model="showModal"
      @updateVotes="updateVotes"
    />
  </v-container>
</template>

<script>
import Vue from "vue";
import { voting } from "@/api";
import BallotCard from "./BallotCard";
import CodeModal from "./CodeModal";

export default {
  components: {
    BallotCard,
    CodeModal
  },
  props: ["update"],
  data() {
    return {
      updateModal: {
        id: 0,
        numVotes: 0
      },
      requestIndex: 0,
      requestCount: 0,
      showModal: false,
      item: null,
      per: 1000,
      pageData: {
        hasNext: false,
        hasPrev: false,
        nextNum: false,
        page: 1,
        items: [],
        prevNum: null,
        totalItems: 0,
        totalPages: 0
      }
    };
  },
  mounted() {
    this.loadPage();
  },
  watch: {
    update() {
      this.updateModal = this.update;
      const index = this.pageData.items.findIndex(
        item => item.id == this.update.id
      );
      if (index == -1) return;
      this.pageData.items[index].numVotes = this.update.numVotes;
    }
  },
  methods: {
    updateVotes(id, numVotes, voteStatus) {
      this.updateModal = { id: id, numVotes: numVotes, hasVoted: voteStatus };
      const index = this.pageData.items.findIndex(item => item.id == id);
      if (index == -1) return;
      this.pageData.items[index].numVotes = numVotes;
      this.pageData.items[index].hasVoted = voteStatus;
      this.$emit("updateVotes", id, numVotes, voteStatus);
    },
    showCode(item) {
      this.item = item;
      this.showModal = true;
    },
    async setResult(result) {
      for (const [key, value] of Object.entries(result)) {
        if (key !== "items") {
          Vue.set(this.pageData, key, value);
        }
      }
      const items = result.items
        .filter(i => i.disqualified === null)
        .sort((a, b) => {
          return a.numVotes < b.numVotes ? 1 : -1;
        });
      this.$emit("input", items.length);
      items.splice(3, items.length - 3);
      Vue.set(this.pageData, "items", items);
    },
    async loadPage() {
      this.requestCount++;

      const results = await voting.getBallot(this.pageData.page, this.per);
      await this.setResult(results);

      this.requestCount--;
    }
  },
  computed: {
    isLoading() {
      return this.requestCount > 0;
    }
  }
};
</script>

<style lang="scss" scoped>
h2 {
  text-align: center;
  color: #0d1d41;
  font-family: "Barlow", sans-serif;
  font-weight: bold;
  margin-bottom: 12px;
}
</style>
