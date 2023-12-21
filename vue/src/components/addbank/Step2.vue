<!-- Step2.vue -->
<template>
    <div>
      <h2>Step 2: Choose Website</h2>
      <select v-model="selectedWebsite">
        <option v-for="website in websites" :value="website">{{ website }}</option>
      </select>
      <button @click="nextStep">Next</button>
      <button @click="prevStep">Previous</button>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  export default {
    data() {
      return {
        selectedWebsite: "",
        websites: ["--Please Select The Website--"],
      };
    },
    mounted() {
      
      const websitess_endpoint = this.apiUrl + "websites";
      const data = {name : this.$parent.bankFormData.brand};
      axios
        .post(websitess_endpoint, data, { withCredentials: true })
        .then((response) => {
          this.websites = this.websites.concat(response.data.websites);
          this.selectedWebsite = this.websites[0];
        });
    },
    methods: {
      nextStep() {
        this.$emit("next");
      },
      prevStep() {
        this.$emit("prev");
      },
    },
  };
  </script>
  