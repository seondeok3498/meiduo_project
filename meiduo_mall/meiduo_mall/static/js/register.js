let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        //v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url: '',
        uuid: '',
        image_code:'',
        sms_code:'',
        sms_code_tip:'获取短信验证码',
        send_flag: false,//默认锁为开，可用

        //v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code:false,

        //[[]]
        error_name_message: '',
        error_mobile_message: '',
        error_image_code_message: '',
        error_sms_code_message: '',

    },
    mounted(){
        this.generate_image_code();
    },
    methods: {
        send_sms_code(){
            //避免恶意用户频繁请求验证码
            if (this.send_flag == true){//判断如果锁已上，则不能发送请求
                return;
            }

            this.send_flag = true;//上锁，不可用

            //校验手机号和图形验证码
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true) {
                //上锁后不能使用，开锁
                this.send_flag = false;
                return;
                }

            //发送ajax请求发送验证码，此时处于上锁状态
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {

                    //发送短信成功
                    if (response.data.code == '0') {
                        //定义60秒计时器
                        let num = 60;
                        let t = setInterval(() => {
                            if (num == 1) {//计时器即将结束
                                clearInterval(t);//停止计时器的执行
                                this.sms_code_tip = '获取短信验证码';//将a标签重新显示获取短信验证码
                                this.generate_image_code();//重新获取图形验证码
                                this.send_flag = false;//重新获取短信验证码时开锁
                            }
                            else {//正在计时
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    }

                    //发送短信失败
                    else {
                        if (response.data.code == '4001') {
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                            this.send_flag = false;//需重新发送短信，开锁
                        }
                        else if (response.data.code == '4002'){
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        else {
                            console.log(response.data)
                        }
                    }
                })
                .catch(error => {
                    console.log(response.data);
                    //ajax请求发送失败，开锁
                    this.send_flag = false;
                })
            },

        generate_image_code(){
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },

        check_username() {
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if (re.test(this.username)) {
                this.error_name = false;
            } else {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }

            if (this.error_name == false) {
                let url = '/usernames/' + this.username + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        } else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },

        check_password() {
            let re = /^[a-zA-Z0-9]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },

        check_password2() {
            if (this.password2 != this.password) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },

        check_mobile() {
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '请输入正确的手机号码';
                this.error_mobile = true;
            }

            if (this.error_mobile == false) {
                let url = '/mobiles/' + this.mobile + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            // 用户名已存在
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        } else {
                            // 用户名不存在
                            this.error_mobile = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },

        check_image_code(){
            if (this.image_code.length != 4){
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            }else {
                this.error_image_code = false;
            }
        },

        check_sms_code(){
            if (this.sms_code.length != 6){
                this.error_sms_code_message = '请输入短信验证码';
                this.error_sms_code = true;
            }else {
                this.error_sms_code = false;
            }
        },

        check_allow(){
            if (!this.allow){
                this.error_allow = true
            }else{
                this.error_allow = false
            }
        },

        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_sms_code();
            this.check_allow();

            if (this.error_name == true || this.error_password == true ||
                this.error_password2 == true || this.error_mobile == true ||
                this.error_sms_code ==true || this.error_allow == true) {
                window.event.returnValue = false;
            }

        },


        },

})
