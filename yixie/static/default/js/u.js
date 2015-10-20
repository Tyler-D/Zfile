/* u逻辑 */
$(document).ready(function(){
    // 提交表单
    // 修改存储容量
    $("#quota-form-submit").click(function(){
        $.ajax({
            type:"POST",
            //TODO 增加修改密码的action
            url:"/quota/add",
            dataType:"json",
            data:$("#quota-form").serialize(),
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
