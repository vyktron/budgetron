<!-- Step1.vue -->
<template>
  <div>
    <h2>Fill in your credentials</h2>
    <div class="horizontal-line"></div>
    <!-- Form with as many input fields that the user has banks -->
    
      <table>
        <tr>
          <th><span class="icon"><img src="../../assets/bank_line.svg"/></span><span class="text">Bank</span></th>
          <th><span class="icon"><img src="../../assets/IDcard_line.svg"/></span><span class="text">ID</span></th>
          <th><span class="icon"><img src="../../assets/safe_lock_line.svg"/></span><span class="text">Secret</span></th>
        </tr>
        <tr v-for="(bank, index) in user_banks" :key="index">
          <td>{{ bank.name }}</td>
          <td>{{ bank.client_number }}</td>
          <td><input type="password" class="credentials" clav-model="form[bank.name]" /></td>
        </tr>
      </table>
    <div class="horizontal-line"></div>
    <button type="submit" class="button-text" @click="submitForm" style="margin-bottom: 10px;">EXTRACT</button>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      user_banks: [],
      form: {},
    };
  },
  mounted() {
    this.user_banks = this.$parent.banks;
  },
  methods: {
    submitForm() {
      this.$emit("submit", this.form);
    },
  },
};
</script>

<style>
.form-row {
  display: flex;
  align-items: center;
}

html, body {
  height: 100%;
}
</style>
