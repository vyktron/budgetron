import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import Login from './components/Login.vue';
import Signup from './components/Signup.vue';
import Dashboard from './components/Dashboard.vue';
import CryptoJs from 'crypto-js';


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

// Global functions
// Function to generate AES key of size 512 bits
app.config.globalProperties.generateKey = function () {
  return CryptoJs.enc.Hex.stringify(CryptoJs.lib.WordArray.random(64));
};
// Function to encrypt data using AES
app.config.globalProperties.encrypt = function (data : string, key : string) {
  return CryptoJs.AES.encrypt(data, key).toString();
};
// Function to decrypt data using AES
app.config.globalProperties.decrypt = function (data : string, key : string) {
  return CryptoJs.AES.decrypt(data, key).toString(CryptoJs.enc.Utf8);
};
// Function to generate SHA256 hash of size 512 bits with SHA256
app.config.globalProperties.hash = function (data : string, salt : string, iterations : number) {
  return CryptoJs.PBKDF2(data, salt, { keySize: 512/32, iterations: iterations, hasher: CryptoJs.algo.SHA256 }).toString();
}

app.use(router);
app.mount('#app');



