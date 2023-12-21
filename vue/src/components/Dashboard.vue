<template>
    <div class="dashboard">
        <div class="sidebar">
            <div class="profile">
                <h3>{{ userProfile.email }}</h3>
            </div>
            <button @click="logout">Logout</button>
        </div>
        <div class="content">
            <table>
                <!-- table content -->
            </table>
            <button @click="showBankForm = true">Add Bank</button>
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

export default {
    components: {
        Step1,
        Step2,
        Step3,
    },
    data() {
        return {
            userProfile: {email: 'test'},
            banks: ['test'],
            accounts: [{number: '123', name: 'test', balance: '123'}],
            transactions: [],
            showBankForm: false,
            currentBankStep: 1,
            bankFormData: {},
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
            } catch (error) {
                // Refresh the page if the user is not authenticated
                if (error.response.status === 401) {
                    const refresh_status = this.refreshToken();
                    if (refresh_status === 200) {
                        this.fetchUserData();
                    } else {
                        this.$router.push('/login');
                    }
                }
            }
        },
        async logout() {
            const logout_endpoint = this.apiUrl + 'log/out';
            const response = await axios.get(logout_endpoint, { withCredentials: true });
            this.$router.push('/login');
        },
        closeBankForm() {
            this.currentBankStep = 1;
            this.bankFormData = {};
            this.showBankForm = false;
        },
        submitBankForm(data) {
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
