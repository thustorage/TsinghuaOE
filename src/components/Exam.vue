<template>
  <v-container
    fluid
    class="fill-height"
  >
    <v-layout
      align-center
      justify-center
    >
      <v-stepper
        v-model="e1"
        v-if="items.length>0"
        vertical
      >
        <template v-for="item in items">
          <v-stepper-step
            :key="`${item.id}-step`"
            :complete="e1 > item.id"
            :step="item.id"
            editable
          >
            {{ item.id }}
          </v-stepper-step>
          
          <v-stepper-content
            :key="`${item.id}-content`"
            :step="item.id"
          >
            <v-card
              v-if="item.type!=='submit'"
              class="mb-12"
              width="800px"
            >
              <v-card-text>
              <v-img :src="item.path" min-height=300 min-width=500 max-width=700  contain>
              </v-img>
              </v-card-text>
              <v-card-actions>
                <v-select
                  v-if="item.type==='select'"
                  v-model="answers[item.id]"
                  :items="item.options"
                  :label="item.label"
                  :multiple="item.multiple"
                ></v-select>
                <v-textarea
                  v-if="item.type==='text'"
                  v-model="answers[item.id]"
                  clearable="true"
                  filled
                  auto-grow
                  solo
                  label="请在此输入答案"
                ></v-textarea>
              </v-card-actions>
            </v-card>
            <v-btn
              v-if="item.type!=='submit'"
              color="primary"
              class="mx-4"
              @click="lastStep(item.id)"
            >
              上一题
            </v-btn>
            <v-btn
              v-if="item.type!=='submit'"
              color="primary"
              class="mx-4"
              @click="nextStep(item.id)"
            >
              下一题
            </v-btn>
            <v-card
              v-if="item.type==='submit'"
              class="mb-12"
              width="800px"
            >
              <v-card-title>
              {{item.title}}
              </v-card-title>
              <v-card-text>
                {{item.body}}
              </v-card-text>
              <v-card-text>
                {{answers}}
              </v-card-text>
              <v-card-actions>
                <v-btn
                  v-if="item.type==='submit'"
                  color="primary"
                  @click="submit"
                >
                确认提交
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
      </v-stepper>
    </v-layout>
  </v-container>
</template>

<script>
  // import md5 from 'js-md5';
  import axios from 'axios';

  export default {
    name: 'Exam',
    mounted: function () {
      let that = this;
      axios({
        method: 'post',
        url: '/app/exam',
        data: {token: this.$store.state.Authorization}
      }).then(res => {
        if (res.data.code === 0) {
          for (let item in res.data.items) {
            that.items.push(res.data.items[item]);
          }
        } else {
          alert(res.data.message)
          that.$router.replace('/');
        }
      }).catch(error => {
        alert('请等待考试开始');
        that.$router.replace('/');
        console.log(error)
      });
      this._autosubmit();
    },
    data: () => ({
      submitted: false,
      timer: null,
      e1: 1,
      index: 1,
      items: [
      ],
      answers: {}
    }),
    watch: {
      steps (val) {
        if (this.e1 > val) {
          this.e1 = val
        }
      },
    },
    methods: {
      _autosubmit () {
        let that = this;
          this.timer = setInterval( () => {
            if (that.submitted) {return;}
            axios({
              method: 'post',
              url: '/app/submit',
              data: {token: that.$store.state.Authorization, answers: that.answers}
            }).then(res => {
              if (res.data.code === 0) {
                // alert("提交成功");
                console.log(res.data);
              } else {
                alert("自动提交失败，请联系助教");
              }
            }).catch(error => {
              alert('自动提交失败，请联系助教');
              console.log(error);
            });
          }, 5000);
      },
      nextStep (n) {
        if (n === this.items.length) {
          this.e1 = 1
        } else {
          this.e1 = n + 1
        }
      },
      lastStep (n) {
        if (n === 0) {
          this.e1 = this.items.length
        } else {
          this.e1 = n - 1
        }
      },
      submit () {
        let that = this;
        axios({
          method: 'post',
          url: '/app/submit',
          data: {token: this.$store.state.Authorization, answers: this.answers}
        }).then(res => {
          if (res.data.code === 0) {
            alert("提交成功");
            console.log(res.data);
            that.submitted = true;
          } else {
            alert("提交失败");
            that.submitted = false;
          }
        }).catch(error => {
          alert('提交失败');
          that.submitted = false;
          console.log(error);
        });
      }
    },
  }
</script>
