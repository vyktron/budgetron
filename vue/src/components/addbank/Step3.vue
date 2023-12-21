<!-- Step3.vue -->
<template>
    <div>
      <h2>Step 3: Enter Account Number</h2>
      <label for="accountNumber">Account Number:</label>
      <input type="text" v-model="accountNumber" />
      <button @click="submitForm">Submit</button>
      <button @click="prevStep">Previous</button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      selectedBrand: String, // The selected brand from Step 1
      selectedWebsite: String, // The selected website from Step 2
    },
    data() {
      return {
        accountNumber: "",
      };
    },
    mounted() {
      // GET THE FORMAT OF THE LOGIN FORMAT FROM THE SERVER
    },
    methods: {
      submitForm() {
        this.$emit("submit", { accountNumber: this.accountNumber });
      },
      prevStep() {
        this.$emit("prev");
      },
    },
  };
  </script>
  