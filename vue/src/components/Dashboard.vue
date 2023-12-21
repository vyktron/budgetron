<template>
    <div class="dashboard">
        <div class="sidebar">
            <div class="profile">
                <h3>{{ userProfile.email }}</h3>
            </div>
            <button @click="logout">Logout</button>
        </div>
        <div class="content">
            <div class="account">
                <h2>Accounts</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Number</th>
                            <th>Name</th>
                            <th>Balance</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="account in accounts" :key="account.number">
                            <td>{{ account.number }}</td>
                            <td>{{ account.name }}</td>
                            <td>{{ account.balance }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="banks">
                <h2>Banks</h2>
                <table>
                    <tbody>
                        <tr v-for="bank in banks" :key="bank.name">
                            <td>{{ bank.name }}</td>
                            <td>{{ bank.website }}</td>
                            <td>{{ bank.client_number }}</td>
                        </tr>
                    </tbody>
                </table>
                <button @click="showBankForm = true">Add Bank</button>
            </div>
            
            <!-- Use the dynamic form component -->
            <div v-if="showBankForm" class="popup">
                <div class="popup-content">
                    <img class="close-button" @click="closeBankForm" src="../assets/close_line.svg"/>
                    <component :is="currentBankStepComponent" @next="nextBankStep" @prev="prevBankStep" @submit="submitBankForm" :data="bankFormData"></component>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import Step1 from './addbank/Step1.vue';
import Step2 from './addbank/Step2.vue';
import Step3 from './addbank/Step3.vue';
import './Dashboard.css'; // Import Dashboard.css file
import ls from 'localstorage-slim';
export default {
    components: {
        Step1,
        Step2,
        Step3,
    },
    data() {
        return {
            userProfile: {email: 'Fetching user data...'},
            banks: [],
            accounts: [],
            transactions: [],
            showBankForm: false,
            currentBankStep: 1,
            bankFormData: {},
            aes_key: '',
        };
    },
    mounted() {
        this.fetchUserData();
    },
    computed: {
        currentBankStepComponent() {
            return `Step${this.currentBankStep}`;
        },
    },
    methods: {
        async fetchUserData() {
            const profile_endpoint = this.apiUrl + 'data';

            try {
                const response = await axios.get(profile_endpoint, { withCredentials: true });
                this.userProfile = response.data.user;
                this.banks = response.data.banks;
                this.accounts = response.data.accounts;
                this.transactions = response.data.transactions;

                // Decrypt all the data
                const vault_key = ls.get('vault_key', {decrypt: true});
                for (const bank of this.banks) {
                    // Get the AES key and random IV
                    const aes_key = this.decryptRandomIV(bank.enc_aes_key, vault_key, bank.random_iv);
                    // Decrypt the bank data
                    for (const [key, value] of Object.entries(bank)) {
                        if (key === 'enc_aes_key' || key === 'random_iv' || key === 'accounts') {
                            continue;
                        }
                        bank[key] = this.decrypt(value, aes_key, bank.random_iv);
                    }
                }
                
            } catch (error) {
                // Refresh the page if the user is not authenticated
                try {
                    if (error.response.status === 401) {
                        const refresh_status = await this.refreshToken();
                        if (refresh_status === 200) {
                            this.fetchUserData();
                        }
                        else {
                            this.$router.push('/login');
                            alert("Session expired. Please login again.")
                        }
                    }
                } catch (error) {
                    this.$router.push('/login');
                    alert("Please login.")
                }
            }
        },
        async logout() {
            const logout_endpoint = this.apiUrl + 'log/out';
            const response = await axios.get(logout_endpoint, { withCredentials: true });

            // Clear the local storage
            localStorage.clear();

            this.$router.push('/login');
        },
        closeBankForm() {
            this.currentBankStep = 1;
            this.bankFormData = {};
            this.showBankForm = false;
        },
        submitBankForm(data) {
            this.bankFormData = { ...this.bankFormData, ...data };
            // Send the bank form data to the server7
            const add_bank_endpoint = this.apiUrl + 'add_bank';

            // Encrypt all fields of the bank form data
            this.aes_key = this.generateKey();
            const random_iv = this.generateKey(16);
            
            // Encrypt the bank form data
            for (const [key, value] of Object.entries(this.bankFormData)) {
                this.bankFormData[key] = this.encrypt(value, this.aes_key, random_iv);
            }
            
            const vault_key = ls.get('vault_key', {decrypt: true});
            // Encrypt the AES key with the vault key
            this.aes_key = this.encryptRandomIV(this.aes_key, vault_key, random_iv);
            alert(this.aes_key);
            const enc_data = {
                ...this.bankFormData,
                enc_aes_key: this.aes_key,
                random_iv: random_iv,
            };

            axios.post(add_bank_endpoint, enc_data, { withCredentials: true })
                .then((response) => {
                    // Refresh the user data
                    this.fetchUserData();
                })
                .catch((error) => {
                    // Refresh the access token if it has expired
                    if (error.response.status === 401) {
                        const refresh_status = this.refreshAccessToken();
                        if (refresh_status == 200) {
                            axios.post(add_bank_endpoint, this.bankFormData, { withCredentials: true })
                                .then((response) => {
                                    // Refresh the user data
                                    this.fetchUserData();
                                });
                        }
                    }
                });
            // Close the form after submission
            this.closeBankForm();
        },
        nextBankStep(data) {
            this.bankFormData = { ...this.bankFormData, ...data };
            this.currentBankStep += 1;
        },
        prevBankStep() {
            this.currentBankStep -= 1;
        },
    }
};
</script>
