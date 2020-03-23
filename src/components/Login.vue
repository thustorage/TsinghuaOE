<template>
  <v-container
    fluid
    class="fill-height"
  >
    <v-layout
      align-center
      justify-center
    >
      <v-flex
        xs12
        sm8
        md4
      >
        <v-card class="elevation-12">
          <v-toolbar
            color="primary"
            dark
            flat
          >
            <v-toolbar-title>登入</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field
                v-model="login_id"
                label="学号"
                name="id"
                type="text"
              ></v-text-field>

              <v-text-field
                v-model="login_password"
                label="密码"
                name="password"
                type="password"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn v-on:click="login" color="primary">登入</v-btn>
          </v-card-actions>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import md5 from 'js-md5';
  import axios from 'axios';
  import { mapMutations } from 'vuex';
  export default {
    name: 'Login',
    data: () => ({
     login_id:"",
     login_password:"",
     login_id_rules: [],
    }),
    methods: {
      ...mapMutations(['changeLogin']),
      login: function () {
        var l_id = md5(this.login_id)
        var l_password = md5(this.login_password)
        let that = this 
        axios({
          method: 'post',
          url: '/app/login',
          data: {id: l_id, password:l_password}
        }).then(res => {
          if (res.data.code === 0) {
            that.changeLogin({ Authorization: res.data.path, id: that.login_id });
            that.$router.replace('/Exam');
          } else {
            alert('账号或密码错误');
          }
        }).catch(error => {
          alert('账号或密码错误');
          console.log(error)
        });
      }
    },
  }
</script>
