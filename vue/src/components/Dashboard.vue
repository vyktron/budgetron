<template>
    <div class="sidebar">
        <div class="profile">
            <h4>{{ userProfile.email.substring(0, userProfile.email.indexOf('@')) }}</h4>
        </div>
        <div @click="logout" class="close-button"><span class="icon"><img src="../assets/logout.svg"/></span><span class="text">&nbsp;Log Out</span></div>
    </div>
    <div class="dashboard">
        <div class="main">
            <div class="content-middle">
                <Graphs/>
            </div>
            <div class="content-right">
                <div style="display: flex; flex-direction: column; justify-content: center; min-height: 63vh; min-width: 23vw;">
                    <div @click="showUpdateForm = true && allow_update" :class="{'button-disabled': !allow_update, 'button-allowed': allow_update}"><span class="icon"><img src="../assets/refresh_2_line.svg"/></span><span class="text">{{ last_update }}</span></div>
                    <table style="margin-top: 0.5vh;">
                        <thead>
                            <tr>
                                <th style="width: 4%;"></th>
                                <th style="width: 4%;"></th>
                                <th style="width: 40%; font-weight: bolder; font-size: large;"><span class="icon"><img src="../assets/bank_line.svg"/></span><span class="text">Bank</span></th>
                                <th style="width: 40%; font-weight: bolder; font-size: large;"><span class="icon"><img src="../assets/IDcard_line.svg"/></span><span class="text">ID</span></th>
                                <th style="width: 15%;"></th>
                            </tr>
                        </thead>
                        <tbody style="max-height: 50vh;">
                            <div v-for="(bank, index) in banks" :key="bank.name">
                                <tr style="height: 5vh; cursor: pointer;">
                                    <td style="width: 4%;" class="checkbox-wrapper">
                                        <div style="margin-left: 2px;" class="round" :title="'Select ' + bank.name">
                                            <input type="checkbox" :id="'checkbox-' + bank._id" @change="changeCheckColor(bank, index, null)"/>
                                            <label :style="{ borderColor: bank_colors[index] }" :for="'checkbox-' + bank._id" :id="'checkbox-label-' + bank._id"></label>
                                        </div>
                                        <div class="line-bank" :id="'checkbox-line-' + bank._id"></div>
                                    </td>
                                    <td style="width: 4%;"><img src="../assets/right_line.svg" :id="'arrow-' + bank._id" @click="toggleDropdown(bank, index)" :title="'Show ' + bank.name + ' accounts'"/></td>
                                    <td style="width: 40%; font-weight: bold;">{{ bank.name }}</td>
                                    <td style="width: 45%; font-weight: bold;">{{ bank.client_number }}</td>
                                    <td style="width: 10%;"><img class="close-button" src="../assets/delete_2_line.svg" @click="deleteBank(bank)" title="Delete this bank"/></td>
                                </tr>
                                <div v-if="bank.showDropdown && bank.accounts.length !==0" style="width: 100%">
                                    <tr v-for="account in accounts" :key="account._id">
                                        <div v-if="bank.accounts.includes(account._id)">
                                            <td></td>
                                            <td class="checkbox-wrapper" style="width: 14%; height: 3vh; border-left: 2px solid" :style="{ borderLeftColor: bank_colors[index] }">
                                                <div class="round">
                                                    <input type="checkbox" :id="'checkbox-' + account._id" @change="changeCheckColor(account, index, bank)"/>
                                                    <label style="height: 10px; width: 10px;" :style="{ backgroundColor: account.color, borderColor: bank_colors[index], borderWidth: '2px'}" :for="'checkbox-' + account._id" :id="'checkbox-label-' + account._id"></label>
                                                </div>
                                            </td>
                                            <td style="width: 60%;">{{ account.name }}</td>
                                            <td style="width: 30%;">type</td>
                                        </div>
                                    </tr>
                                </div>
                            </div>
                        </tbody>
                    </table>
                    <div @click="showBankForm = true" class="open-button" style="width: fit-content; padding-left: 0.5vw;"><img class="icon" src="../assets/add_circle_line.svg"/><span class="text">Add Bank</span></div>
                </div>
            </div>
        </div>
        <div class="transaction-container">
            <div class="content-middle">
                <div style="background-color: grey; width: 60vw; height: 30vh;">Transactions</div>
            </div>
            <div class="content-right">
                <div style="background-color: grey; width: 23vw; height: 30vh;">Transaction details</div>
            </div>
        </div>
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
            <div class="right-close" v-if="currentUpdateStep==1"><img class="close-button" @click="closeUpdateForm" src="../assets/close_line.svg"/></div>
            <component :is="currentUpdateStepComponent" @submit="submitUpdateForm" @finish="finishUpdate" :data="updateFormData"></component>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import BankStep1 from './addbank/Step1.vue'; import BankStep2 from './addbank/Step2.vue'; import BankStep3 from './addbank/Step3.vue';
import UpdateForm from './update/Form.vue'; import UpdateProgress from './update/Progress.vue';
import Graphs from './Graphs.vue';
import './Dashboard.css'; // Style
import ls from 'localstorage-slim';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
export default {
    components: {
        BankStep1, BankStep2, BankStep3,
        UpdateForm, UpdateProgress,
        Graphs,
    },
    data() {
        return {
            userProfile: {email: 'Fetching user data...'},
            banks: [],
            accounts: [],
            transactions: [],
            showBankForm: false, showUpdateForm: false,
            currentBankStep: 1, currentUpdateStep: 1,
            bankFormData: {}, updateFormData: {},
            updateFormData: {},
            allow_update: false,
            last_update: ' Loading...',
            bank_colors: ["#FF6633", "#FFB399", "#FF33FF", "#FFFF99", "#00B3E6", 
                "#E6B333", "#3366E6", "#999966", "#99FF99", "#B34D4D"]
        };
    },
    async mounted() {
        await this.fetchUserData();
    },
    computed: {
        currentBankStepComponent() {
            return `BankStep${this.currentBankStep}`;
        },
        currentUpdateStepComponent() {
            if (this.currentUpdateStep === 1) {
                return 'UpdateForm';
            }
            return 'UpdateProgress';
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
                    var aes_key = this.decryptRandomIV(bank.enc_aes_key, vault_key, bank.random_iv);
                    // Decrypt the bank data
                    for (const [key, value] of Object.entries(bank)) {
                        if (key === 'enc_aes_key' || key === 'random_iv' || key === 'accounts' || key === '_id') {
                            continue;
                        }
                        this.max_tries = 10;
                        do {
                            try {
                                bank[key] = this.decryptRandomIV(value, aes_key, bank.random_iv);
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

                // Get the last update date (the last update date of each bank)
                this.last_update = dayjs(0);
                for (const bank of this.banks) {
                    if (bank.last_update === "None") {
                        this.bank_last_update = dayjs(0);
                    } else {
                        this.bank_last_update = dayjs(bank.last_update);
                    }
                    if (this.bank_last_update.isAfter(this.last_update)) {
                        this.last_update = this.bank_last_update;
                    }
                }
                // Get the time difference between now and the last update
                dayjs.extend(relativeTime);
                this.last_update = "Last update - " + this.last_update.fromNow()
                if (this.last_update.includes('hour') || this.last_update.includes('minute') || this.last_update.includes('second')) {
                    this.allow_update = false;
                }
                else {
                    this.allow_update = true;
                }

                for (const account of this.accounts) {
                    // Get the AES key and random IV
                    aes_key = this.decryptRandomIV(account.enc_aes_key, vault_key, account.random_iv);
                    // Decrypt the bank data
                    for (const [key, value] of Object.entries(account)) {
                        if (key === 'enc_aes_key' || key === 'random_iv' || key === 'transactions' || key === '_id') {
                            continue;
                        }
                        this.max_tries = 10;
                        if (key === "balances" || key === "dates") {
                            for (let j = 0; j < value.length; j++) {
                                do {
                                    try {
                                        account[key][j] = this.decryptRandomIV(value[j], aes_key, account.random_iv);
                                        this.max_tries -= 1;
                                    } catch (error) {
                                        console.log(error);
                                    }
                                } while (account[key][j] === undefined && this.max_tries > 0);

                                if (this.max_tries === 0) {
                                    alert('Error decrypting data');
                                }
                            }
                        }
                        else {
                            do {
                                try {
                                    account[key] = this.decryptRandomIV(value, aes_key, account.random_iv);
                                    this.max_tries -= 1;
                                } catch (error) {
                                    console.log(error);
                                }
                            } while (account[key] === undefined && this.max_tries > 0);
                            if (key === "currency") {
                                switch (account[key]) {
                                    case "EUR":
                                        account[key] = "€";
                                        break;
                                    default:
                                        account[key] = account[key];
                                        break;
                                }
                            }
                            if (this.max_tries === 0) {
                                alert('Error decrypting data');
                            }
                        }
                    }
                }
                for (const transactions_per_account of this.transactions) {
                    // Get the AES key and random IV from the corresponding account
                    aes_key = this.decryptRandomIV(transactions_per_account[1], vault_key, transactions_per_account[2]);
                    // Enumerate the transactions
                    for (const transaction of transactions_per_account[0]) {
                        // Decrypt the bank data
                        for (const [key, value] of Object.entries(transaction)) {
                            if (key === 'enc_aes_key' || key === 'random_iv' || key === 'id') {
                                continue;
                            }
                            this.max_tries = 10;
                            do {
                                try {
                                    transaction[key] = this.decryptRandomIV(value, aes_key, transaction.random_iv);
                                    this.max_tries -= 1;
                                } catch (error) {
                                    console.log(error);
                                }
                            } while (transaction[key] === undefined && this.max_tries > 0);

                            if (this.max_tries === 0) {
                                alert('Error decrypting data');
                            }
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
                    if (error.toJSON.message === "Network Error") {
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
        changeCheckColor(object, index, bank) {
            const checkboxElement = document.getElementById('checkbox-' + object._id);
            const checkboxLabelElement = document.getElementById("checkbox-label-" + object._id)
        
            if (checkboxElement.checked) {
                checkboxLabelElement.style.backgroundColor = this.bank_colors[index];
                object.color = this.bank_colors[index];
                if (bank === null) {
                    object.color = this.bank_colors[index];
                    // Check all the checkboxes linked to the accounts of this bank 
                    for (const account_id of object.accounts) {
                        //Get the account object
                        const account = this.accounts.find(account => account._id === account_id);
                        account.color = this.bank_colors[index];
                    }
                }
                else {
                    // If it is the only account checked, check the bank checkbox
                    const bankCheckbox = document.getElementById('checkbox-' + bank._id);
                    const bankCheckboxLabel = document.getElementById('checkbox-label-' + bank._id);
                    const checkedAccounts = bank.accounts.filter(account_id => {
                        const accountCheckbox = document.getElementById('checkbox-' + account_id);
                        return accountCheckbox.checked;
                    });
                    if (checkedAccounts.length === 1) {
                        bankCheckboxLabel.style.backgroundColor = this.bank_colors[index] + "60";
                        bankCheckbox.checked = true;
                    }
                    if (checkedAccounts.length === bank.accounts.length) {
                        bankCheckboxLabel.style.backgroundColor = this.bank_colors[index];
                    }
                }
            } else {
                object.color = '';
                checkboxLabelElement.style.backgroundColor = '';
                if (bank === null) {
                    // Uncheck all the checkboxes linked to the accounts of this bank 
                    for (const account_id of object.accounts) {
                        // Get the account object
                        const account = this.accounts.find(account => account._id === account_id);
                        account.color = '';
                    }
                }
                else {
                    // If it is the only account checked, uncheck the bank checkbox
                    const bankCheckbox = document.getElementById('checkbox-' + bank._id);
                    const bankCheckboxLabel = document.getElementById('checkbox-label-' + bank._id);
                    const checkedAccounts = bank.accounts.filter(account_id => {
                        const accountCheckbox = document.getElementById('checkbox-' + account_id);
                        return accountCheckbox.checked;
                    });
                    if (checkedAccounts.length < bank.accounts.length) {
                        bankCheckboxLabel.style.backgroundColor = this.bank_colors[index] + "80";
                    }
                    if (checkedAccounts.length === 0) {
                        bankCheckboxLabel.style.backgroundColor = '';
                        bankCheckbox.checked = false;
                    }
                }
            }
        },
        closeBankForm() {
            this.currentBankStep = 1;
            this.bankFormData = {};
            this.showBankForm = false;
        },
        async submitBankForm(data) {
            this.bankFormData = { ...this.bankFormData, ...data };
            // Send the bank form data to the server
            const add_bank_endpoint = this.apiUrl + 'add_bank';

            // Encrypt all fields of the bank form data
            var aes_key = this.generateKey();
            const random_iv = this.generateKey(16);

            this.bankFormData['last_update'] = "None";
            
            // Encrypt the bank form data
            for (const [key, value] of Object.entries(this.bankFormData)) {
                // Do not encrypt the accounts (which is the list of ids of the accounts of the bank)
                if (key !== 'accounts') {
                    this.bankFormData[key] = this.encryptRandomIV(value, aes_key, random_iv);
                }
            }
            
            const vault_key = ls.get('vault_key', {decrypt: true});
            // Encrypt the AES key with the vault key
            aes_key = this.encryptRandomIV(aes_key, vault_key, random_iv);
            const enc_data = {
                ...this.bankFormData,
                enc_aes_key: aes_key,
                random_iv: random_iv,
            };

            try {
                const response = await axios.post(add_bank_endpoint, enc_data, { withCredentials: true });
                // Refresh the page
                await this.fetchUserData();
                this.defineBankColor();
            } catch (error) {
                // Refresh the access token if it has expired
                alert(error);
                try {
                    if (error.response) {
                        if (error.response.status === 401) {
                            const refresh_status = this.refreshAccessToken();
                            if (refresh_status == 200) {
                                const response = await axios.post(add_bank_endpoint, this.bankFormData, { withCredentials: true });
                                // Refresh the user data
                                await this.fetchUserData();
                            }
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
            }
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
        finishUpdate() {
            this.showUpdateForm = false;
            this.currentUpdateStep = 1;
            this.fetchUserData();
            this.defineBankColor();
        },
        submitUpdateForm(data) {
            this.updateFormData = { ...data };
            this.currentUpdateStep += 1;
        },
        deleteBank(bank) {
            const delete_bank_endpoint = this.apiUrl + 'delete_bank';
            // Send the bank data to the server
            axios.post(delete_bank_endpoint, bank, { withCredentials: true })
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
                                    axios.post(delete_bank_endpoint, bank, { withCredentials: true })
                                        .then((response) => {
                                            // Refresh the user data
                                            this.fetchUserData();
                                        });
                                }
                            }
                            if (error.response.status === 400) {
                                // Show error details
                                const errorDetails = error.request.response;
                                // Parse the error details
                                const errorDetailsObject = JSON.parse(errorDetails);
                                // Show the error message
                                alert(errorDetailsObject.detail);
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
        },
        toggleDropdown(bank, index) {
            if (bank.accounts.length === 0) {
                return;
            }
            bank.showDropdown = !bank.showDropdown;
            const arrowElement = document.getElementById('arrow-' + bank._id);
            const lineElement = document.getElementById("checkbox-line-" + bank._id);
            if (bank.showDropdown) {
                arrowElement.style.transition = "transform 0.2s";
                arrowElement.style.transform = "rotate(90deg)";
                lineElement.style.backgroundColor = this.bank_colors[index];
            } else {
                arrowElement.style.transform = "rotate(0deg)";
                lineElement.style.backgroundColor = "transparent";
            }
        },
    }
};
</script>
