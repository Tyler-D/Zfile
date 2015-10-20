/* disk逻辑 */
$(document).ready(function(){
    // 提交表单
    // 新建文件夹 
    $("#folder-form-submit").click(function(){
        $.ajax({
            type:"POST",
            //TODO 增加修改密码的action
            url:"/disk/add",
            dataType:"json",
            data:$("#folder-form").serialize(),
            async:false,
            success:function(data){
                alert(data.msg);
                if(0 == data.errno) {
                    location.reload();
                }
            }
        })
    });

    // 上传文件
    $("#file-form-submit").click(function(){
        $.ajaxFileUpload ({
            url :'/disk/upload',
            secureuri :false,
            fileElementId :'disk',
            data: {'path': $('#file-form-path').val()},
            dataType : 'json',
            success : function (data, status){
                alert(data.msg);
                if(0 == data.errno)
                    location.reload();
            },
            error: function (data, status, e){
                alert(e);
            }
        })
    });
});
