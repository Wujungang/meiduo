var vm = new Vue({
    el:'#app',
    data:{
        username:'',
        show_name:'False',
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
    },
    mounted: function(){
        if(this.user_id){
            show_name='True'
        }
        else{
            show_name='Fasle'
        }
    },
});