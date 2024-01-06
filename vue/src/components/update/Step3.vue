<!-- Step3.vue -->
<template>
    <div>
      <h2>Step 3: Enter Your Client Number</h2>
      <label for="ClientNumber">Clien Number:</label>
      <!-- Set a placeholder which is the login format -->
      <input type="text" v-model="clientNumber" :placeholder="loginFormat">
      <button @click="submitForm">Submit</button>
      <button @click="prevStep">Previous</button>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  export default {
    data() {
      return {
        clientNumber: "",
        loginFormat: "", // Added loginFormat data property
      };
    },
    mounted() {
      // GET THE FORMAT OF THE LOGIN FORMAT FROM THE SERVER
      const login_format_endpoint = this.apiUrl + "login_format";
      const data = {
        name: this.$parent.bankFormData.name,
      };
      axios
        .post(login_format_endpoint, data, { withCredentials: true })
        .then((response) => {
          this.loginFormat = response.data.login_format;
        })
    },
    methods: {
      submitForm() {
        this.$emit("submit", { client_number: this.clientNumber });
      },
      prevStep() {
        this.$emit("prev");
      },
    },
  };
  </script>
  