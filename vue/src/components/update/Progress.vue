<!-- Progress.vue : Update progress bar and errors handling -->
<template>
  <div>
    <h2 style="margin-top: 35px;">Bank data extraction</h2>
    <div class="horizontal-line"></div>
    <!-- Form with as many input fields that the user has banks -->
    
      <table style="padding-inline: 10px;">
        <tr>
          <th><span class="icon"><img src="../../assets/bank_line.svg"/></span><span class="text">Bank</span></th>
          <th><span class="icon"><img src="../../assets/IDcard_line.svg"/></span><span class="text">ID</span></th>
          <th><span class="icon"><img src="../../assets/update.svg"/></span><span class="text">Status</span></th>
        </tr>
        <tr v-for="(bank, index) in user_banks" :key="index">
          <td>{{ bank.name }}</td>
          <td>{{ bank.client_number }}</td>
          <td style="padding-block: 15px;">{{ status[index] }}</td>
        </tr>
      </table>
    <div class="horizontal-line" style="margin-top: 15px"></div>
    <button type="submit" class="button-text" @click="finishUpdate" style="margin-bottom: 15px;">FINISH</button>
  </div>
</template>

<script>
import axios from "axios";
import ls from 'localstorage-slim';
export default {
  data() {
    return {
      user_banks: [],
      status: [],
    };
  },
  mounted() {
    this.user_banks = this.$parent.banks;
    // Add a variable for the status of the extraction for each bank
    this.user_banks.forEach((bank) => {
      this.status.push("Pending");
    });
    this.update_form = this.$parent.updateFormData;
    
    // Get the vault key from the local storage
    const vault_key = ls.get('vault_key', {decrypt: true});

    // Set the websocket connection
    const socket = new WebSocket(this.wsUrl + "extract");
    socket.onopen = () => {
      // Send the banks and the passwords to the server
      const data = {
        banks: this.user_banks,
        passwords: this.update_form,
      };
      socket.send(JSON.stringify(data));
    };
    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.type === "status") {
        this.status[response.message] = response.status;
      }
      if (response.type === "encrypt") {
        // Normally, the data to encrypt is a list of transactions or accounts to encrypt
        for (let i = 0; i < response.message.length; i++) {
          // Create the aes key and the iv
          this.aes_key = this.generateKey();
          const random_iv = this.generateKey(16);
          // Check if the data to encrypt is a list of transactions or accounts
          
          const is_account = Object.keys(response.message[i]).includes("transactions");
          // Encrypt the data
          for (const [key, value] of Object.entries(response.message[i])) {
            // Do not encrypt the id and the transactions (list of transactions ids for an account)
            if (key !== "id" && key !== "transactions") {
              if (key === "balances" || key === "dates") {
                for (let j = 0; j < value.length; j++) {
                  response.message[i][key][j] = this.encryptRandomIV(String(value[j]), this.aes_key, random_iv);
                }
              }
              else if (key === "enc_aes_key") {
                response.message[i][key] = this.encryptRandomIV(this.aes_key, vault_key, random_iv);
              }
              else if (key === "random_iv") {
                response.message[i][key] = random_iv;
              } else {
                response.message[i][key] = this.encryptRandomIV(value, this.aes_key, random_iv);
              }
            }
          }
        }
        // Send the encrypted data to the server
        socket.send(JSON.stringify(response.message));
      }
    };
  },
  methods: {
    finishUpdate() {
      this.$emit("finish");
    },
  },
};
</script>