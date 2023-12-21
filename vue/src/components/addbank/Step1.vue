<!-- Step1.vue -->
<template>
  <div>
    <h2>Step 1: Choose Bank Brand</h2>
    <select v-model="selectedBrand" name="Choose Bank Brand">
      <option v-for="bank in banks" :value="bank">{{ bank }}</option>
    </select>
    <button @click="nextStep">Next</button>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      selectedBrand: "",
      banks: ["--Please Select Your Bank--"],
    };
  },
  mounted() {
    const banks_endpoint = this.apiUrl + "banks";
    axios
      .get(banks_endpoint, { withCredentials: true })
      .then((response) => {
        this.banks = this.banks.concat(response.data.banks);
        this.selectedBrand = this.banks[0];
      })
      .catch((error) => {
        // Refresh the access token if it has expired
        if (error.response.status === 401) {
          this.refreshAccessToken();
          axios
            .get(banks_endpoint, { withCredentials: true })
            .then((response) => {
              this.banks = this.banks.concat(response.data.banks);
              this.selectedBrand = this.banks[0];
            });
        }
      });
  },
  methods: {
    nextStep() {
      // If the user has not selected a bank, do not allow them to continue
      if (this.selectedBrand === this.banks[0]) {
        alert("Please select a bank");
        return;
      }
      this.$emit("next", { brand: this.selectedBrand });
    },
  },
};
</script>
