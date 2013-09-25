//验证slice名称是否是字母数字下划线
function check_slice_name(obj_id,flag){
	//alert("in check_slice_form");
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	//var reg = /^([u4e00-u9fa5]|[ufe30-uffa0]|[a-zA-Z_])*$/;
	var reg = /^[a-zA-Z_]\w*$/;
	//alert(obj.value.length);
	if(obj.value.length > 0){
		if(!reg.test(obj.value))
		{
			//alert("in 输入");
			showInfo(info," * 请输入字母数字下划线的组合（不以数字开头）","red")
			return false;
		}
		else
		{
			//alert("in green");
			//alert(slice_exist);
			isslice_exist(obj.value);
			if(slice_exist)
			{
				//alert(slice_exist);
				showInfo(info," * 该slice已经存在","red")
				return false;
			}
			else
			{
				showInfo(info,"√","green")
				return true;
			}
		}
	
	}
	else
	{
		showInfo(info," * 必填","red")
		return false;
	}	
}

function check_slice_description(obj_id,flag){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	if(obj.value.length > 0){
		showInfo(info,"√","green")
		return true;
	}
	else{
		showInfo(info," * 必填","red")
		return false;
	}
}

function check_island_id(){
	var obj = document.getElementById("island_id");
	var info = document.getElementById("island_idInfo"); 
	if(obj.value.length > 0){
		showInfo(info,"√","green")
		return true;
	}
	else{
		showInfo(info," * 必填","red")
		return false;
	}
}

function check_slice_controller(obj_name){
	var objs = document.getElementsByName(obj_name);
	for(var i=0;i<objs.length;i++){  
		if(objs[i].checked){  
			if(objs[i].value=="default_create"){  
				return true; 
			}  
			if(objs[i].value=="user_defined"){
				ret1 = check_ip("controller_ip",1);
				ret2 = check_port("controller_port",1);
				if (ret1 && ret2){
					return true;
				}
				else{
					return false;
				}
	  		}  
		}   
	}
}

//验证IP地址格式
function check_ip(obj_id,flag){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info");
	var reg=/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;//正则表达式

	if(obj.value.length > 0){
		if(reg.test(obj.value)){
			if( RegExp.$1<256 && RegExp.$2<256 && RegExp.$3<256 && RegExp.$4<256){
				showInfo(info,"√","green")
				return true;
			}
		}
		showInfo(info," * 格式错误","red")		
		return false;
	}
	else{
		if(flag){
			showInfo(info," * 必填","red")
			return false;
		}
		else{
			return true;
		}
	}	
}

//校验端口值
function check_port(obj_id,flag){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info");
	var reg = /^[0-9]*$/;
	if(obj.value.length > 0){
		if(obj.value >= 65535 || obj.value < 0 || !reg.test(obj.value)){
			showInfo(info," * （0-65535）","red")
			return false;
		}
		else{
			showInfo(info,"√","green")
			return true;
		}	
	}
	else{
		if(flag){
			showInfo(info," * 必填","red")
			return false;
		}
		else{
			return true;
		}
	}
}

var slice_exist;
//校验所填的slice是否存在
function isslice_exist(slicename)
{
	//alert (slicename)
	check_url = "http://" + window.location.host + "/slice/check_slice_name/"+slicename+"/";
	//alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	if (data.value == 1)
             {
                //alert("in true")
                slice_exist = true;
             } 
             else
             {
              	//alert("in false");
                slice_exist = false;
             }
        }
    });
}


//显示信息
function showInfo(_info,msg,color){
    var info=_info;
    info.innerHTML = msg;
    info.style.color=color;
}