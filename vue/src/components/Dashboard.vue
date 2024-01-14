<template>
    <div class="dashboard">
        <div class="sidebar">
            <div class="profile">
                <h4>{{ userProfile.email.substring(0, userProfile.email.indexOf('@')) }}</h4>
            </div>
            <div @click="logout" class="close-button"><span class="icon"><img src="../assets/logout.svg"/></span><span class="text">&nbsp;Log Out</span></div>
        </div>
        <div class="content">
            <div @click="showUpdateForm = true" class="button-text"><span class="icon"><img src="../assets/refresh_2_line.svg"/></span><span class="text">Last update - yesterday</span></div>
            <div class="tables">
                <table>
                    <tbody>
                        <tr>
                            <th><span class="icon"><img src="../assets/bank_line.svg"/></span><span class="text">Bank</span></th>
                            <th><span class="icon"><img src="../assets/IDcard_line.svg"/></span><span class="text">ID</span></th>
                            <th> </th>
                        </tr>
                        <tr v-for="bank in banks" :key="bank.name">
                            <td>{{ bank.name }}</td>
                            <td>{{ bank.client_number }}</td>
                            <td><img class="close-button" src="../assets/delete_2_line.svg"/></td>
                        </tr>
                    </tbody>
                    <div @click="showBankForm = true" class="open-button"><img class="icon" src="../assets/add_circle_line.svg"/><span class="text">Add Bank</span></div>
                </table>
            </div>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th><span class="icon"><img src="../assets/hashtag_line.svg"/></span><span class="text">Account</span></th>
                            <th><span class="icon"><img src="../assets/currency_euro_line.svg"/></span><span class="text">Balance</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="account in accounts" :key="account.number">
                            <td>{{ account.name }}</td>
                            <td>{{ account.balance }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Use the dynamic form component -->
            <div v-if="showBankForm" class="popup">
                <div class="popup-content">
                    <div class="right-close"><img class="close-button" @click="closeBankForm" src="../assets/close_line.svg"/></div>
                    <component :is="currentBankStepComponent" @next="nextBankStep" @prev="prevBankStep" @submit="submitBankForm" :data="bankFormData"></component>
                </div>
            </div>
            <div v-if="showUpdateForm" class="popup">
                <div class="popup-content">
                    <div class="right-close"><img class="close-button" @click="closeUpdateForm" src="../assets/close_line.svg"/></div>
                    <UpdateForm />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import BankStep1 from './addbank/Step1.vue'; import BankStep2 from './addbank/Step2.vue'; import BankStep3 from './addbank/Step3.vue';
import UpdateForm from './update/Form.vue';
import './Dashboard.css'; // Style
import ls from 'localstorage-slim';
export default {
    components: {
        BankStep1, BankStep2, BankStep3,
        UpdateForm
    },
    data() {
        return {
            userProfile: {email: 'Fetching user data...'},
            banks: [],
            accounts: [],
            transactions: [],
            showBankForm: false, 
            showUpdateForm: false,
            currentBankStep: 1,
            bankFormData: {}, updateFormData: {},
            aes_key: '',
        };
    },
    mounted() {
        this.fetchUserData();
    },
    computed: {
        currentBankStepComponent() {
            return `BankStep${this.currentBankStep}`;
        },
    },
    methods: {
        async fetchUserData() {
            const profile_endpoint = this.apiUrl + 'data';
            await axios.get(profile_endpoint, { withCredentials: true })
            .then((response) => {
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
                        this.max_tries = 10;
                        do {
                            try {
                                bank[key] = this.decrypt(value, aes_key, bank.random_iv);
                                this.max_tries -= 1;
                            } catch (error) {
                                console.log(error);
                            }
                        } while (bank[key] === undefined && this.max_tries > 0);

                        if (this.max_tries === 0) {
                            alert('Error decrypting bank data');
                        }
                    }
                }
            })
            .catch((error) => {
                // Refresh the page if the user is not authenticated
                try {
                    if (error.response) {
                        if (error.response.status === 401) {
                            this.refreshToken().then((response) => {
                                if (response != "Expired") {
                                    this.fetchUserData();
                                }
                            });
                        }
                    }
                    // Handle Network errors
                    if (error.toJSON().message === "Network Error") {
                        alert("Check your connection or the service status")
                        this.$router.push('/login');
                    }
                } catch (error) {
                    alert(error);
                }
            });
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
                    try {
                        if (error.response) {
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
                        }
                        // Handle Network errors
                        if (error.toJSON().message === "Network Error") {
                            alert("Check your connection or the service status")
                            this.$router.push('/login');
                        }
                    }
                    catch (error) {
                        alert(error);
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

        closeUpdateForm() {
            this.showUpdateForm = false;
        },
        submitUpdateForm(data) {
            this.updateFormData = { ...this.updateFormData, ...data };
            
            alert(this.updateFormData);
            // Close the form after submission
            this.closeUpdateForm();
        },
    }
};
</script>
