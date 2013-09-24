//验证vm名称是否是字母数字下划线
function check_vm_name(obj_id){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	var reg = /^[a-zA-Z_]\w*$/;
	//alert(obj.value.length);
	if(obj.value.length > 0){
		if(!reg.test(obj.value))
		{
			showInfo(info," * 请输入字母数字下划线的组合（不以数字开头）","red")
			return false;
		}
		else
		{
                        showInfo(info,"√","green")
                        return true;
		}
	
	}
	else
	{
		showInfo(info," * 该项为必填项","red")
		return false;
	}	
}

//验证vm的flavor,image,server等以select形式提供的选项不能为空
function check_vm_select(obj_id){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	if(obj.selectedIndex == 0){
		showInfo(info," * 该项为必填项","red")
		return false;
	}
	else
	{
                showInfo(info,"√","green")
		return true;
	}	
}


//获取vm form的内容并填入slice清单中
function fetch_vminfo()
{
        name_value = get_value_from_obj('id_name')
        //alert('name_value')
        flavor_text = get_text_from_select('id_flavor')
        //alert(flavor_text)
        image_text = get_text_from_select('id_image')
        //alert(image_text)
        server_text = get_text_from_select('id_server')
        //alert(server_text)
        enable_dhcp_value = get_checked_from_checkbox('id_enable_dhcp')
        //alert(enable_dhcp_value)
        content = "<tr>"
        content = content + "<td>" + name_value + "</td>"
        content = content + "<td>" + flavor_text + "</td>"
        content = content + "<td>" + image_text + "</td>"
        content = content + "<td>" + server_text + "</td>"
        content = content + "<td>" + enable_dhcp_value + "</td>"
        content = content + "</tr>"
        //alert(content)
        insert_content_to_obj('id_vm_tbody',content)
}

function get_text_from_select(obj_id)
{
        var obj = document.getElementById(obj_id);
        //alert(obj.selectedIndex)
        text = obj.options[obj.selectedIndex].text
        return text
}

function get_checked_from_checkbox(obj_id)
{
        var obj = document.getElementById(obj_id);
        if(obj.checked)
        {
                return "是"
        }
        return "否"
}

function get_value_from_obj(obj_id)
{
        var obj = document.getElementById(obj_id);
        return obj.value
}

function insert_content_to_obj(obj_id, content)
{
        var obj = document.getElementById(obj_id);
        obj.innerHTML = obj.innerHTML + content;
}
