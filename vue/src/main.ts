import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import Login from './components/welcome/Login.vue';
import Signup from './components/welcome/Signup.vue';
import Dashboard from './components/Dashboard.vue';
import CryptoJs from 'crypto-js';
import axios from 'axios';


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/signup', component: Signup },
  { path: '/dashboard', component: Dashboard },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);

// Global variables
// Set the API URL globally
app.config.globalProperties.apiUrl = 'https://127.0.0.1:8089/';
// Set the websocket URL globally
app.config.globalProperties.wsUrl = 'wss://127.0.0.1:8089/';

// Global functions
// Function to generate AES key of size 512 bits
app.config.globalProperties.generateKey = function (size : number = 64) {
  return CryptoJs.enc.Hex.stringify(CryptoJs.lib.WordArray.random(size));
};

// Function to encrypt with random IV and AES algorithm
app.config.globalProperties.encryptRandomIV = function (data : string, key : string, randomIV : string) {
  return CryptoJs.AES.encrypt(data, key, { iv: randomIV }).toString();
};

// Function to decrypt with random IV and AES algorithm
app.config.globalProperties.decryptRandomIV = function (data : string, key : string, randomIV : string) {
  return CryptoJs.AES.decrypt(data, key, { iv: randomIV }).toString(CryptoJs.enc.Utf8);
};

// Function to generate SHA256 hash of size 512 bits with SHA256
app.config.globalProperties.hash = function (data : string, salt : string, iterations : number) {
  return CryptoJs.PBKDF2(data, salt, { keySize: 512/32, iterations: iterations, hasher: CryptoJs.algo.SHA256 }).toString();
};

// Function to refresh the access token if it is expired
app.config.globalProperties.refreshToken = function () {
  return axios.get(app.config.globalProperties.apiUrl + 'log/refresh', { withCredentials: true })
  .catch(_ => {
    this.$router.push('/login');
    alert("Session expired. Please login again.");
    return "Expired";
  })
};

app.use(router);
app.mount('#app');



