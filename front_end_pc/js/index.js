var vm = new Vue({
    el: "#app",
    data:{
        show_name:false,
        show_reg:true,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
    },
    mounted: function(){
       this.change()
    },
    methods:{
        change:function () {
            if(this.user_id){
            this.show_name= true;
            this.show_reg=false
            }
            else{
                this.show_name= false;
                this.show_reg = true
            }
        }
    }
});