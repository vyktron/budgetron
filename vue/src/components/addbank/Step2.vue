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
      
      const websites_endpoint = this.apiUrl + "websites";
      const data = {name : this.$parent.bankFormData.name};
      axios
        .post(websites_endpoint, data, { withCredentials: true })
        .then((response) => {
          this.setValues(response);
        })
        .catch((error) => {
          // Refresh the access token if it has expired
          if (error.response.status === 401) {
            const refresh_status = this.refreshAccessToken();
            if (refresh_status == 200) {
              axios
                .post(websites_endpoint, data, { withCredentials: true })
                .then((response) => {
                  this.setValues(response);
              });
            }
          }
        });
    },
    methods: {
      setValues(response) {
        this.websites = this.websites.concat(response.data.websites);
        // Test if bankFormData is empty
        if (Object.keys(this.$parent.bankFormData).length > 1 && this.websites.includes(this.$parent.bankFormData.website)) {
          
          this.selectedWebsite = this.$parent.bankFormData.website;
        }
        else {this.selectedWebsite = this.websites[0];}
      },
      nextStep() {
        if (this.selectedWebsite=== this.websites[0]) {
          alert("Please select a website");
          return;
        }
        this.$emit("next", { website: this.selectedWebsite });
      },
      prevStep() {
        this.$emit("prev");
      },
    },
  };
  </script>
  