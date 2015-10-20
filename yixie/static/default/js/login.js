/* login逻辑 */
$(document).ready(function(){
    // 提交表单
    // 登录
    $("#login-form-submit").click(function(){
        $.ajax({
            type:"POST",
            //TODO 增加修改密码的action
            url:"/account/login_auth",
            dataType:"json",
            data:$("#login-form").serialize(),
            async:false,
            success:function(data){
                alert(data.msg);
                if(0 == data.errno) {
                    location.reload();
                }
            }
        });
    });

    // 提交表单
    // 注册账号
    $("#register-form-submit").click(function(){
        $.ajax({
            type:"POST",
            //TODO 增加修改密码的action
            url:"/account/register",
            dataType:"json",
            data:$("#register-form").serialize(),
            async:false,
            success:function(data){
                alert(data.msg);
                if(0 == data.errno) {
                    location.reload();
                }
            }
        });
    });
});
