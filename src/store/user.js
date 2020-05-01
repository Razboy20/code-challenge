import { mapState } from "vuex";
import * as api from "@/api";
import Vue from "vue";

const moduleName = "User";

function getDefaultState() {
  return {
    username: "",
    firstName: "",
    lastName: "",
    email: "",
    displayName: "",
    rank: 0,
    isAuthorized: false,
    voteCount: 0
  };
}

const state = {
  ...getDefaultState()
};

const actions = {
  async refresh({ commit }) {
    const user = api.auth.currentUser();
    user.rank = user.rank + 1;
    if (user.auth) {
      commit("set", user);
    } else {
      commit("clear", user);
    }
  },
  vote({ commit }) {
    commit("vote");
  },
  unvote({ commit }) {
    commit("unvote");
  },
  setnumvotes({ commit }, numVotes) {
    commit("setnumvotes", numVotes);
  }
};

const mutations = {
  vote(state) {
    state.voteCount++;
  },
  unvote(state) {
    state.voteCount--;
  },
  setnumvotes(state, numVotes) {
    state.voteCount = numVotes;
  },
  setvotes(state, user) {
    for (const [key, value] of Object.entries(user)) {
      Vue.set(state, key, value);
    }
    state.isAuthorized = true;
  },
  clear(state) {
    for (const [key, value] of Object.entries(getDefaultState())) {
      Vue.set(state, key, value);
    }
  }
};

export default {
  namespaced: true,
  name: moduleName,
  state,
  actions,
  mutations,
  mapState: () => mapState([moduleName])
};
