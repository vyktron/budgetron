<template>
    <div class="dashboard">
        <div class="sidebar">
            <div class="profile">
                <h3>{{ userProfile.email }}</h3>
            </div>
            <button @click="logout">Logout</button> <!-- Added logout button -->
        </div>
        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>Number</th>
                        <th>Name</th>
                        <th>Balance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="account in accounts">
                        <td>{{ account.number }}</td>
                        <td>{{ account.name }}</td>
                        <td>{{ account.balance }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
export default {
    data() {
        return {
            userProfile: {email: 'test'},
            accounts: [{number: '123', name: 'test', balance: '123'}]
        };
    },
    mounted() {
        this.fetchUserProfile();
        this.fetchAccounts();
    },
    methods: {
        async fetchUserProfile() {
            const profile_endpoint = this.apiUrl + 'profile';
            const response = await axios.get(profile_endpoint, { withCredentials: true });
            this.userProfile = response.data;
        },
        async fetchAccounts() {
            const accounts_endpoint = this.apiUrl + 'accounts';
            const response = await axios.get(accounts_endpoint, { withCredentials: true });
            this.accounts = response.data;           
        },
        async logout() {
            const logout_endpoint = this.apiUrl + 'logout';
            const response = await axios.get(logout_endpoint, { withCredentials: true });
            this.$router.push('/login');
        }
    }
};
</script>

<style>
.dashboard {
    display: flex;
}

.sidebar {
    width: 250px;
    background-color: #f0f0f0;
    padding: 20px;
}

.profile {
    margin-bottom: 20px;
}

.content {
    flex: 1;
    padding: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 10px;
    border: 1px solid #ccc;
}
</style>

