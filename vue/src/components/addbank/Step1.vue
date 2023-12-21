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
        this.setValues(response);
      })
      .catch((error) => {
        // Refresh the access token if it has expired
        if (error.response.status === 401) {
          const refresh_status = this.refreshAccessToken();
          if (refresh_status == 200) {
            axios
              .get(banks_endpoint, { withCredentials: true })
              .then((response) => {
                this.setValues(response);
            });
          }
        }
      });
  },
  methods: {
    setValues(response) {
      this.banks = this.banks.concat(response.data.banks);
        // Test if bankFormData is empty
        if (Object.keys(this.$parent.bankFormData).length !== 0) {
          this.selectedBrand = this.$parent.bankFormData.name;
        }
        else {this.selectedBrand = this.banks[0];}
    },
    nextStep() {
      // If the user has not selected a bank, do not allow them to continue
      if (this.selectedBrand === this.banks[0]) {
        alert("Please select a bank");
        return;
      }
      this.$emit("next", { name: this.selectedBrand });
    },
  },
};
</script>
