/* 此文件js依赖于jquery.js */

/**
 * 使用ajax提交数据，直接alrt数据
 */
function ajax_call(the_url,the_param){
	$.ajax({
		type:'POST',
		url:the_url,
		data:the_param,
		dataType: 'json',
		success:function(html){alert(html);},
		error:function(html){
			alert("提交数据失败，代码:" +html.status+ "，请稍候再试");
		}
	});
}

/**
 * 使用ajax提交数据，并重新加载页面
 */
function ajax_call_and_refresh(the_url, the_param){
	$.ajax({
		type:'POST',
		url:the_url,
		data:the_param,
		dataType: 'json',
		success:function(html){location.reload();},
		error:function(html){
			alert("提交数据失败，代码:" +html.status+ "，请稍候再试");
		}
	});
}

/**
 * 使用ajax提交数据，通过回调函数处理返回结果
 */
function ajax_post(the_url,the_param,succ_callback){
	$.ajax({
		type	: 'POST',
		cache	: false,
		url		: the_url,
		data	: the_param,
		dataType: 'json',
		success	: succ_callback,
		error	: function(html){
			alert("提交数据失败，代码:" +html.status+ "，请稍候再试");
		}
	});
}

/**
 * 使用ajax获取数据，通过回调函数处理返回结果
 */
function ajax_get(the_url,error_tip,succ_callback){
	$.ajax({
		type	: 'GET',
		cache	: true,
		url		: the_url,
		dataType: 'json',
		success	: succ_callback,
		error	: function(html){
			if(error_tip)
			alert("获取数据失败，代码:" +html.status+ "，请稍候再试");
		}
	});
}

/**
 * 使用ajax跨域获取数据，通过回调函数处理返回结果
 */
function ajax_cross_get(the_url,error_tip,succ_callback){
	$.ajax({
		type	: 'GET',
		cache	: true,
		url		: the_url,
		dataType: 'jsonp',
        jsonp: 'jsoncallback',
		success	: succ_callback,
		error	: function(html){
			if(error_tip)
			alert("获取数据失败，代码:" +html.status+ "，请稍候再试");
		}
	});
}
