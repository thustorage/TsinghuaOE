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
            :complete="submitteds[item.id]"
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
                <v-container fluid>
                  <v-row dense>
                    <v-col
                     v-if="item.type==='select' || item.type==='judge'"
                     cols="12"
                    >
                      <v-select
                        v-if="item.type==='select' || item.type==='judge'"
                        v-model="answers[item.id]"
                        :items="item.options"
                        :label="item.label"
                        :multiple="item.multiple"
                      ></v-select>
                    </v-col>
                    <v-col
                      v-for="blank in item.blanks"
                      :key="blank"
                      :cols="12"
                    >
                      <v-textarea
                        :key="blank"
                        v-model="answers[item.id][blank]"
                        clearable="true"
                        filled
                        rows=1
                        auto-grow
                        outlined
                        :label="blank"
                      ></v-textarea>
                    </v-col>
                    <v-col
                     v-if="item.type==='text'"
                     cols="12"
                    >
                      <v-textarea
                        v-if="item.type==='text'"
                        v-model="answers[item.id]['text']"
                        clearable="true"
                        filled
                        auto-grow
                        outlined
                        :label="item.label"
                      ></v-textarea>
                    </v-col>
                  </v-row>
                </v-container>
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
            <v-btn
              v-if="item.type!=='submit'"
              color="primary"
              class="mx-4"
              @click="submit_one(item.id)"
            >
              提交
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
                  :disabled="enable_submit"
                  @click="submit"
                >
                提交所有答案
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
        </template>
      </v-stepper>
    </v-layout>
  </v-container>
</template>

<script>
  import md5 from 'js-md5';
  import axios from 'axios';
  import { mapMutations } from 'vuex';
  function isEmpty(dic) {
    for (let key in dic) {
      return false;
    }
    return true;
  }
  export default {
    name: 'Exam',
    mounted: function () {
      this.submitted = this.$store.state.submitted;
      let that = this;
      axios({
        method: 'post',
        url: '/app/exam',
        data: {
          id: md5(this.$store.state.id),
          token: this.$store.state.Authorization
        }
      }).then(res => {
        if (res.data.code === 0) {
          for (let item in res.data.items) {
            that.items.push(res.data.items[item]);
            if(res.data.items[item].type==='text') {
              that.answers[res.data.items[item].id] = {};
            }
          }
          for (let item in res.data.answers) {
            that.answers[item] = res.data.answers[item];
            if (res.data.answers[item].length == 0 || isEmpty(res.data.answers[item]) ) {
              continue;
            }
            else {
              that.submitteds[item] = true;
            }
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
      // this._autosubmit();
    },
    beforeDestroy: function() {
      clearInterval(this.timer);
    },
    data: () => ({
      enable_submit: false,
      submitted: false,
      timer: null,
      e1: 1,
      index: 1,
      items: [
      ],
      answers: {},
      submitteds: {}
    }),
    watch: {
      steps (val) {
        if (this.e1 > val) {
          this.e1 = val
        }
      },
    },
    methods: {
      ...mapMutations(['update_submit']),
      _autosubmit () {
        let that = this;
          this.timer = setInterval( () => {
            if (that.submitted) {return;}
            axios({
              method: 'post',
              url: '/app/submit',
              data: {
                id: md5(that.$store.state.id),
                token: that.$store.state.Authorization,
                answers: that.answers
              }
            }).then(res => {
              if (res.data.code !== 0) {
                alert(res.data.message);
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
      submit_one (id) {
        let ans_package = {};
        ans_package[id] = this.answers[id];
        if (ans_package[id] === null || ans_package[id] === undefined || isEmpty(ans_package[id])) {
          alert("未填写答案");
          return;
        }
        let that = this;
        axios({
          method: 'post',
          url: '/app/submit',
          data: {
            id: md5(that.$store.state.id),
            token: this.$store.state.Authorization,
            answers: ans_package
          }
        }).then(res => {
          if (res.data.code === 0) {
            // alert("提交成功！请注意：以最后一次提交的内容为准。");
            that.submitteds[id] = true;
            that.nextStep(id);
          } else {
            alert(res.data.message);
            that.submitteds[id] = false;
          }
        }).catch(error => {
          alert('提交失败');
          that.submitteds[id] = false;
          console.log(error);
        })
      },
      submit () {
        this.enable_submit = true;
        let that = this;
        axios({
          method: 'post',
          url: '/app/submit',
          data: {
            id: md5(that.$store.state.id),
            token: this.$store.state.Authorization,
            answers: this.answers
          }
        }).then(res => {
          if (res.data.code === 0) {
            alert("提交成功！请注意：以最后一次提交的内容为准。");
            for(let key in that.answers) {
              if (that.answers[key] === null || that.answers[key] === undefined || isEmpty(that.answers[key])) {
               continue;
              }
              that.submitteds[key] = true;
            }
          } else {
            alert(res.data.message);
            for(let key in that.answers) {
              that.submitteds[key] = false;
            }
          }
        }).catch(error => {
          alert('提交失败');
          console.log(error);
        }).then(
          ()=>{
            this.enable_submit = false;
          }
        );
      }
    },
  }
</script>
