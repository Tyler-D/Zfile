/* user逻辑 */
$(document).ready(function(){
    // 提交表单
    // 添加用户 
    $("#user-form-submit").click(function(){
        $.ajax({
            type:"POST",
            //TODO 增加修改密码的action
            url:"/user/add",
            dataType:"json",
            data:$("#user-form").serialize(),
            async:false,
            success:function(data){
                alert(data.msg);
                if(0 == data.errno) {
                    location.reload();
                }
            }
        })
    });
});
