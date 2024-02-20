<!-- Form.vue : Update form -->
<template>
  <div>
    <h2 style="margin-top: 10px;">Fill in your credentials</h2>
    <div class="horizontal-line"></div>
    <!-- Form with as many input fields that the user has banks -->
    
      <table style="padding-inline: 10px;">
        <tr>
          <th><span class="icon"><img src="../../assets/bank_line.svg"/></span><span class="text">Bank</span></th>
          <th><span class="icon"><img src="../../assets/IDcard_line.svg"/></span><span class="text">ID</span></th>
          <th><span class="icon"><img src="../../assets/safe_lock_line.svg"/></span><span class="text">Secret</span></th>
        </tr>
        <tr v-for="(bank, index) in user_banks" :key="index">
          <td>{{ bank.name }}</td>
          <td>{{ bank.client_number }}</td>
          <td><input type="password" class="credentials" v-model="form[bank.client_number]" :placeholder="password_formats[index]" /></td>
        </tr>
      </table>
    <div class="horizontal-line" style="margin-top: 15px"></div>
    <button type="submit" class="button-text" @click="submitForm" style="margin-bottom: 15px;">EXTRACT</button>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      user_banks: [],
      form: {},
      password_formats: [],
    };
  },
  mounted() {
    this.user_banks = this.$parent.banks;
    // GET THE FORMAT OF THE LOGIN FORMAT FROM THE SERVER
    const password_format_endpoint = this.apiUrl + "password_format";
    const data = {
      banks: this.user_banks,
    };
    axios
      .post(password_format_endpoint, data, { withCredentials: true })
      .then((response) => {
        this.password_formats = response.data.password_formats;
      })
      .catch((error) => {
        // Refresh the page if the user is not authenticated
        try {
          if (error.response.status === 401) {
            this.refreshToken().then(() => {
              axios.post(password_format_endpoint, data, { withCredentials: true })
              .then((response) => {
                this.password_formats = response.data.password_formats;
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
      this.$emit("submit", this.form);
    },
  },
};
</script>
