<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="login">
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
  import ls from 'localstorage-slim';
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
          const response = await axios.post(login_endpoint, data, { withCredentials: true });

          // Clear the password from memory
          this.password = '';
        
          await this.refreshToken();

          const vault_key = await this.getVaultKey(this.master_key);
          this.master_key = '';
          // Store the master key
          ls.set('vault_key', vault_key, {ttl : 60*60*1000, encrypt: true});
          
          this.$router.push('/dashboard');
        } 
        catch (error) {
          if (error.response.status == 400) {
            // Show error details
            const errorDetails = error.request.response;
            // Parse the error details
            const errorDetailsObject = JSON.parse(errorDetails);
            // Show the error message
            alert(errorDetailsObject.detail);
          } else {
            alert(error);
          }
        }
      },
      async getVaultKey(master_key) {
            const vault_key_endpoint = this.apiUrl + 'vault';
            try {
                const response = await axios.get(vault_key_endpoint, { withCredentials: true });
                return this.decrypt(response.data.key, master_key);
            } catch (error) {
                console.log(error);
            }
        },
    }
  };
  </script>

  <style scoped>
  /* Add your custom styles here */
  </style>
