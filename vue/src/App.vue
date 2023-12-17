<template>
  <div id="app">
    <router-view />
    <router-link to="/signup"></router-link>
    <router-link to="/login"></router-link>
    <router-link to="/dashboard"></router-link>
  </div>
</template>

<script setup>
import './App.css';
</script>
