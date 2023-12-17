<template>
  <div>
    <h1>Login</h1>
    <form @submit="login">
      <label for="email">Email:</label>
      <input type="text" id="email" v-model="email" required>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" required>
      <button type="submit">Log In</button>
    </form>
    <p>
      Don't have an account? 
      <router-link to="/signup">Create an account</router-link>
    </p>
  </div>
</template>
    

  <script>
  import axios from 'axios';


  export default {
    data() {
        return {
            email: '',
            password: ''
        };
    },
    methods: {
      async login() {
        // Generate the master key from the password and email
        this.master_key = this.hash(this.password, this.email, 10000);

        // Send the email and password hash to your backend for storage
        const data = {
          // Send the email in plaintext
          email: this.email,
          // Generate the password hash with the master key
          authentication_hash: this.hash(this.master_key, this.email, 1)
        };

        const login_endpoint = this.apiUrl + 'login';

        try {
          alert("Attempting to login");
          const response = await axios.post(login_endpoint, data);

          alert(response.data);

        } 
        catch (error) {
          if (error.response.status == 400) {
            alert(error.response.data.message);
          } else {
            alert(error);
          }
        }
      }
    }
  };
  </script>

  <style scoped>
  /* Add your custom styles here */
  </style>
