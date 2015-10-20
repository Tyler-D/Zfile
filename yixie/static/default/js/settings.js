/* settings逻辑 */
$(document).ready(function(){
    // 提交表单
    // 修改账号
    $("#account-form-submit").click(function(){
        $.ajax({
            type:"POST",
            url:"/settings/account",
            dataType:"json",
            data:$("#account-form").serialize(),
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
    // 修改密码
    $("#password-form-submit").click(function(){
        $.ajax({
            type:"POST",
            url:"/settings/password",
            dataType:"json",
            data:$("#password-form").serialize(),
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
