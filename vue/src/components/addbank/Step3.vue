<!-- Step3.vue -->
<template>
    <div class="form-content">
      <div class="form-steps">
          <ul>
              <li>
                  <span class="button-text active">1</span>
              </li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li>
                  <span class="button-text active">2</span>
              </li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li>
                  <span class="button-text active">3</span>
              </li>
          </ul>
      </div>
      <div class="horizontal-line"></div>
      <h2>3. Client number</h2>
      <!-- Set a placeholder which is the login format -->
      <div class="dropdown">
        <input type="text" v-model="clientNumber" :placeholder="loginFormat">
      </div>      
      <div class="horizontal-line"></div>
      <div class="wrap">
        <div class="bottom" @click="prevStep"><img class="button-img" src="../../assets/arrow_left_line.svg"/></div>
        <button type="submit" class="button-text" @click="submitForm">SUBMIT</button>
      </div>
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
        .catch((error) => {
          // Refresh the page if the user is not authenticated
          try {
            if (error.response.status === 401) {
              this.refreshToken().then(() => {
                axios.post(login_format_endpoint, data, { withCredentials: true })
                .then((response) => {
                  this.loginFormat = response.data.login_format;
                });
              });
            }
          } catch (error) {
            alert(error);
          }
        });
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
  