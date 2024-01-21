<template>
    <div class="container">
      <Welcome></Welcome>
      <div class="right-side">
        <div class="cred-form">
            <h1>Sign Up</h1>
            <div class="horizontal-line"></div>
            <form @submit.prevent="submitForm"> <!-- Use the prevent modifier to avoid page reload -->
                <input type="email" id="email" v-model="email" required placeholder="Email address">
                <input type="password" id="password" v-model="password" required v-on:input="updatePasswordStrength" placeholder="Password">
                <p>{{ passwordScore }}</p>

                <input type="password" id="confirm-password" v-model="confirmPassword" placeholder="Confirm Password" required>
                <div class="horizontal-line"></div>
                <button type="submit" class="button-text">SIGN UP</button>
            </form>
            <p>Already registered? <a href="/login" style="color:#eebe39">Login</a></p>
        </div>
      </div>
    </div>
</template>
<script>
import { passwordStrength } from 'check-password-strength';
import CryptoJS from 'crypto-js';
import axios from 'axios';
import Welcome from "./Welcome.vue";
import "./Welcome.css"; // Style
export default {
    components: {
      Welcome
    },
    data() {
        return {
            email: '',
            password: '',
            confirmPassword: '',
            passwordScore: "Too weak",
            master_key: ''
        };
    },
    methods: {
        // Function to submit the form
        async submitForm() {
            if (!this.validateEmail(this.email)) {
                alert('Please enter a valid email address.');
                return;
            }

            if (!this.validatePasswordStrength()) {
                alert('Please enter a strong password');
                return;
            }

            if (this.password !== this.confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            // Generate the master key from the password and email
            this.master_key = this.hash(this.password, this.email, 10000);

            // Generate the vault key
            const vault_key = this.generateKey();
            
            // Send the email and password hash to your backend for storage
            const data = {
                // Send the email in plaintext
                email: this.email,
                // Generate the password hash with the master key
                authentication_hash: this.hash(this.master_key, this.email, 1),
                // Encrypt the vault key with the master key
                encrypted_vault_key: CryptoJS.AES.encrypt(vault_key, this.master_key).toString()
            };

            const signup_endpoint = this.apiUrl + 'signup';
            
            try {
                const response = await axios.post(signup_endpoint, data);
                
                if (response.status == 200) {
                    alert('Signup successful');
                    // Redirect to the login page
                    this.$router.push('/login');
                }
            } 
            catch (error) {
                try {
                    if (error.response) {
                        if (error.request.status == 409) {
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

        validateEmail(email) {
            // Regular expression for email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },
        validatePasswordStrength() {
            return this.passwordScore == "Strong"; // Adjust the strength threshold as needed
        },
        updatePasswordStrength() {
            this.passwordScore = passwordStrength(this.password).value;
        },
    }
};
</script>

<style scoped>
/* Add your custom styles here */
</style>
