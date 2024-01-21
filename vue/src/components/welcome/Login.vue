<template>
  <div class="container">
    <Welcome></Welcome>
    <div class="right-side">
      <div class="cred-form">
        <h1>Login</h1>
        <div class="horizontal-line"></div>
        <form @submit.prevent="login">
          <input type="text" id="email" v-model="email" placeholder="Email address" required>
          <input type="password" id="password" v-model="password" placeholder="Password" required>
          <div class="horizontal-line"></div>
          <button type="submit" class="button-text">LOGIN</button>
        </form>
        <p>
          Don't have any account? 
          <router-link to="/signup" style="color: #eebe39;">Create an account</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
    

  <script>
  import axios from 'axios';
  import ls from 'localstorage-slim';
  import Welcome from './Welcome.vue';
  import "./Welcome.css" // Style
  export default {
    components: {
      Welcome
    },
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
          try {
            if (error.response) {
              if (error.response.status == 400) {
                // Show error details
                const errorDetails = error.request.response;
                // Parse the error details
                const errorDetailsObject = JSON.parse(errorDetails);
                // Show the error message
                alert(errorDetailsObject.detail);
              }
            }
            // Handle 500 errors
            if (error.toJSON().message === "Network Error") {
                alert("Check your connection or the service status")
                this.$router.push('/login');
            }
          } catch (error) {
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
