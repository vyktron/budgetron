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
      crypted_update_dates: [],
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

    // Get the today's date with the format YYYY-MM-DD
    const today = new Date().toISOString().slice(0, 10);
    // Encrypt the date for each bank
    for (let i = 0; i < this.user_banks.length; i++) {
      this.aes_key  = this.decryptRandomIV(this.user_banks[i].enc_aes_key, vault_key, this.user_banks[i].random_iv);
      this.encrypted_date = this.encryptRandomIV(this.today, this.aes_key, this.user_banks[i].random_iv);
      this.crypted_update_dates.push(this.encrypted_date);
    }
    // Set the websocket connection
    const socket = new WebSocket(this.wsUrl + "extract");
    socket.onopen = () => {
      // Send the banks and the passwords to the server
      const data = {
        banks: this.user_banks,
        passwords: this.update_form,
        crypted_update_dates: this.crypted_update_dates,
      };
      socket.send(JSON.stringify(data));
    };
    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);

      if (response.type === "status") {
        this.status[response.message] = response.status;
      }
      if (response.type === "decrypt") {

        this.first_transaction = true;
        for (const data of response.message) {
          // Test if the message contains a list of accounts or a list of transactions (transactions have enc_aes_key and random_iv in the response)
          if (response.enc_aes_key === undefined) {
            // Get the AES key and random IV
            this.aes_key = this.decryptRandomIV(data.enc_aes_key, vault_key, data.random_iv);
          }
          else if (this.first_transaction) {
            // Get the AES key and random IV
            this.aes_key = this.decryptRandomIV(response.enc_aes_key, vault_key, response.random_iv);
            this.first_transaction = false;
          }
          
          // Decrypt the data data
          for (const [key, value] of Object.entries(data)) {
            if (key === 'enc_aes_key' || key === 'random_iv' || key === 'transactions' || key === 'id') {
                continue;
            }
            this.max_tries = 10;
            if (key === "balances" || key === "dates") {
              for (let j = 0; j < value.length; j++) {
                do {
                    try {
                        data[key][j] = this.decryptRandomIV(value[j], this.aes_key, data.random_iv);
                        this.max_tries -= 1;
                    } catch (error) {
                        console.log(error);
                    }
                } while (data[key][j] === undefined && this.max_tries > 0);

                if (this.max_tries === 0) {
                    alert('Error decrypting data');
                }
              }
            }
            else {
              do {
                  try {
                    if (this.first_transaction || key === "date") {
                      data[key] = this.decryptRandomIV(value, this.aes_key, data.random_iv);
                      this.max_tries -= 1;
                    }
                    else {
                      this.max_tries = -1;
                    }
                  } catch (error) {
                      console.log(error);
                  }
              } while (data[key] === undefined && this.max_tries > 0);

              if (this.max_tries === 0) {
                  alert('Error decrypting data');
              }
            }    
          }
        }
        // Send the decrypted data to the server
        socket.send(JSON.stringify(response.message));
      }
      if (response.type === "encrypt") {
        // Normally, the data to encrypt is a list of transactions or accounts to encrypt
        // It can also be a list of strings (balance or date for an account)
        if (response.message.length === 0) {
          return;
        }
        else if (typeof response.message[0] === 'string') {
          // Get it from the response (because it is the same for all the transactions of an account)
          this.aes_key = response.enc_aes_key;
          this.random_iv = response.random_iv;
          // Decrypt the aes key
          this.aes_key = this.decryptRandomIV(this.aes_key, vault_key, this.random_iv);
          // Encrypt the list of strings
          for (let i = 0; i < response.message.length; i++) {
            response.message[i] = this.encryptRandomIV(response.message[i], vault_key, response.random_iv);
          }
        }
        else {
          // Encrypt the data
          for (let i = 0; i < response.message.length; i++) {
            // Check if the data to encrypt is a list of transactions or accounts
            const is_account = Object.keys(response.message[i]).includes("transactions");
            
            if (is_account) {
              // Create the aes key and the iv
              this.aes_key = this.generateKey();
              this.random_iv = this.generateKey(16);
            }
            else {
              // Get it from the response (because it is the same for all the transactions of an account)
              this.aes_key = response.enc_aes_key;
              this.random_iv = response.random_iv;
              // Decrypt the aes key
              this.aes_key = this.decryptRandomIV(this.aes_key, vault_key, this.random_iv);
            }
            // Encrypt the data
            for (const [key, value] of Object.entries(response.message[i])) {
              // Do not encrypt the id and the transactions (list of transactions ids for an account)
              if (key !== "id" && key !== "transactions") {
                if (key === "balances" || key === "dates") {
                  for (let j = 0; j < value.length; j++) {
                    response.message[i][key][j] = this.encryptRandomIV(String(value[j]), this.aes_key, this.random_iv);
                  }
                }
                else if (key === "enc_aes_key") {
                  response.message[i][key] = this.encryptRandomIV(this.aes_key, vault_key, this.random_iv);
                }
                else if (key === "random_iv") {
                  response.message[i][key] = this.random_iv;
                } else {
                  response.message[i][key] = this.encryptRandomIV(value, this.aes_key, this.random_iv);
                }
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