<!-- Step1.vue -->
<template>
  <div class="form-content">
    <div class="form-steps">
        <ul>
            <li>
                <span class="button-text active">1</span>
            </li>
            <li><div class="form-steps-yellow-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li>
                <span class="step">2</span>
            </li>
            <li><div class="form-steps-black-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li><div class="form-steps-black-line"></div></li>
            <li>
                <span class="step">3</span>
            </li>
        </ul>
    </div>
    <div class="horizontal-line"></div>
    <h2>1. Bank</h2>
    <div class="dropdown" ref="dropdown">
      <input v-model="filterText" @input="filterOptions" @click="toggleOptions" placeholder="Type to filter">
      <ul v-if="showOptions" class="options" @click="stopPropagation">
        <li v-for="option in filteredOptions" :key="option" @click="selectOption(option)">{{ option }}</li>
      </ul>
    </div>
    <div class="horizontal-line"></div>
    <div class="right">
      <img class="bottom button-img" @click="nextStep" src="../../assets/arrow_right_line.svg"/>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      selectedBrand: '',
      banks: [],
      filterText: '',
      showOptions: false,
    };
  },
  mounted() {
    const banks_endpoint = this.apiUrl + "banks";
    axios
      .get(banks_endpoint, { withCredentials: true })
      .then((response) => {
        this.setValues(response);
      })
      .catch((error) => {
        // Refresh the page if the user is not authenticated
        try {
          if (error.response.status === 401) {
            this.refreshToken().then(() => {
              axios.get(banks_endpoint, { withCredentials: true })
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
      return this.banks.filter(option => option.toLowerCase().includes(this.filterText.toLowerCase()));
    },
  },
  methods: {
    setValues(response) {
      this.banks = this.banks.concat(response.data.banks);
        // Test if bankFormData is empty
        if (Object.keys(this.$parent.bankFormData).length !== 0) {
          this.selectedBrand = this.$parent.bankFormData.name;
          this.filterText = this.selectedBrand;
        }
    },
    nextStep() {
      // If the user has not selected a bank, do not allow them to continue
      if (this.selectedBrand === "") {
        alert("Please select a bank");
        return;
      }
      this.$emit("next", { name: this.selectedBrand });
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
        this.filterText = this.selectedBrand;
      }
    },
    selectOption(option) {
      this.filterText = option;
      this.selectedBrand = option;
      this.showOptions = false;
    },
    closeDropdown(event) {
      if (!this.$refs.dropdown.contains(event.target)) {
        this.showOptions = false;
        this.filterText = this.selectedBrand;
      }
    },
    stopPropagation(event) {
      event.stopPropagation();
    },
  },
};
</script>
