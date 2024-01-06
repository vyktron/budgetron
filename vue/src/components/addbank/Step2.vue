<!-- Step2.vue -->
<template>
    <div class="form-content">
      <div class="form-steps">
          <ul>
              <li>
                  <span class="step active">1</span>
              </li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li>
                  <span class="step active">2</span>
              </li>
              <li><div class="form-steps-yellow-line"></div></li>
              <li><div class="form-steps-black-line"></div></li>
              <li><div class="form-steps-black-line"></div></li>
              <li><div class="form-steps-black-line"></div></li>
              <li>
                  <div class="form-steps-line"></div>
              </li>
              <li>
                  <span class="step">3</span>
              </li>
          </ul>
      </div>
      <div class="horizontal-line"></div>
      <h2>2. Website</h2>
      <div class="dropdown" ref="dropdown">
        <input v-model="filterText" @input="filterOptions" @click="toggleOptions" placeholder="Type to filter">
        <ul v-if="showOptions" class="options" @click="stopPropagation">
          <li v-for="option in filteredOptions" :key="option" @click="selectOption(option)">{{ option }}</li>
        </ul>
      </div>
      <div class="horizontal-line"></div>
      <div class="wrap">
        <img class="bottom button-img" @click="prevStep" src="../../assets/arrow_left_line.svg"/>
        <img class="bottom button-img" @click="nextStep" src="../../assets/arrow_right_line.svg"/>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  export default {
    data() {
      return {
        selectedWebsite: '',
        filterText: '',
        showOptions: false,
        websites: [],
      };
    },
    mounted() {
      const websites_endpoint = this.apiUrl + "websites";
      const data = {name : this.$parent.bankFormData.name};
      axios
        .post(websites_endpoint, data, { withCredentials: true })
        .then((response) => {
          this.setValues(response);
        })
        .catch((error) => {
          /// Refresh the page if the user is not authenticated
        try {
          if (error.response.status === 401) {
            this.refreshToken().then(() => {
              axios.post(websites_endpoint, data, { withCredentials: true })
                .then((response) => {
                  this.setValues(response);
              });
            });
          }
        } catch (error) {
            alert(error);
        }
        });
        document.addEventListener("click", this.closeDropdown);
    },
    beforeDestroy() {
      document.removeEventListener("click", this.closeDropdown);
    },
    computed: {
      filteredOptions() {
        return this.websites.filter(option => option.toLowerCase().includes(this.filterText.toLowerCase()));
      },
    },
    methods: {
      setValues(response) {
        this.websites = this.websites.concat(response.data.websites);
        // Test if bankFormData is empty
        if (Object.keys(this.$parent.bankFormData).length > 1 && this.websites.includes(this.$parent.bankFormData.website)) {
          
          this.selectedWebsite = this.$parent.bankFormData.website;
          this.filterText = this.selectedWebsite;
        }
      },
      nextStep() {
        if (this.selectedWebsite === "") {
          alert("Please select a website");
          return;
        }
        this.$emit("next", { website: this.selectedWebsite });
      },
      prevStep() {
        this.$emit("prev");
      },

      filterOptions() {
      this.showOptions = true;
      },
      toggleOptions() {
        this.showOptions = !this.showOptions;
        if (this.showOptions) {
          this.filterText = '';
        }
        else {
          this.filterText = this.selectedWebsite;
        }
      },
      selectOption(option) {
        this.filterText = option;
        this.selectedWebsite = option;
        this.showOptions = false;
      },
      closeDropdown(event) {
        if (!this.$refs.dropdown.contains(event.target)) {
          this.showOptions = false;
          this.filterText = this.selectedWebsite;
        }
      },
      stopPropagation(event) {
        event.stopPropagation();
      },
    },
  };
  </script>
  