<template>
  <v-app>
    <v-content>
      <router-view></router-view>
    </v-content>
    <v-footer app color="primary">
      <span class="white--text">&copy; Tsinghua Storage 2020</span>
      <v-spacer />
      <span class="white--text"> 如遇问题请及时联系助教</span>
    </v-footer>
  </v-app>
</template>

<script>

export default {
  name: 'App',

  data: () => ({
    //
  }),
};
</script>
