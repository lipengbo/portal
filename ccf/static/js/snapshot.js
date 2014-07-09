$(document).ready(function(){
    $('#edit_snapshot').click(function(){
        $('#snapshot_bj').modal();
    });
    
    $('#create_image').click(function(){
        $('#make_image').modal();
    });

    $('.submit-edit').click(function(){
        var name = $('#snapshot_name').val();
        var desc = $('#snapshot_desc').val();
        var uuid = $('.tr.active').children("td:first").text();
        if(!(check('name', name) && check('desc', desc))){
            return;
        } 
        $.ajax({
            url : '/ghost/edit_snapshot/',
		    type : 'POST',
		    dataType: 'json',
            data: {
                name: $('#snapshot_name').val(),
                desc: $('#snapshot_desc').val(),
                uuid: uuid
            },
		    success:function(data){
                $('#snapshot_bj').modal('hide');
                if(data.result == 0){
                    window.location.href = '/ghost/list_snapshot/';
                }
            }
        });
    });

    $('.submit-create').click(function(){
        var name = $('#image_name').val();
        var desc = $('#image_desc').val();
        var uuid = $('.tr.active').children("td:first").text();
        var is_public;

        if($('#image_public').attr('checked') == 'checked'){
            is_public = true;
        }else{
            is_public = false;
        }

        if(!(check('name', name) && check('desc', desc))){
            return;
        }

        $.ajax({
            url : '/ghost/create_image/',
		    type : 'POST',
		    dataType: 'json',
            data: {
                name: name,
                desc: desc,
                is_public: is_public,
                uuid: uuid
            },
		    success:function(data){
                $('#make_image').modal('hide');
                if(data.result == 0){
                    window.location.href = '#';
                }
            }
        });                
    });
});

var STATIC_URL = $("#STATIC_URL").text();

function snapshot_creation_show(){
    var vm_id = $('#uuid').attr('title');
    alert('')
    if($('#'+vm_id+'_snapshot').attr('style') == 'cursor:not-allowed'){
        return;
    }
    $('#snapshot_ensure').attr("onclick", "create_snapshot(" + vm_id + ", '"+ host_ip + "')");
    //$('#snapshot_creation').modal('show');
}

function create_snapshot(vm_id, host_ip){
    var name = $('#snapshot_name').val();
    var desc = $('#snapshot_desc').val();
    if(!(check('name', name) && check('desc', desc))){
        return;
    }
    $('#snapshot_creation').modal('hide');
    if($('#'+vm_id+'_qt').children('img').attr('title') == '停止'){
        $('#'+vm_id+'_qt').attr('style', 'cursor:not-allowed');
        $('#'+vm_id+'_qt').children('img').attr('src', ''+STATIC_URL+'img/ic-tz-un.png')
        $('#'+vm_id+'_dl').attr('style', 'cursor:not-allowed');
        $('#'+vm_id+'_dl').children('img').attr('src', ''+STATIC_URL+'img/btn_dl_gray.png');
        $('#'+vm_id+'_sc').attr('style', 'cursor:not-allowed');
        $('#'+vm_id+'_sc').children('img').attr('src', ''+STATIC_URL+'img/btn_sc_gray.png');
    }
    $('#icon_state'+vm_id).removeClass().addClass("icon-spinner").addClass("icon-spin").addClass('check_vm');
   // $('#'+vm_id+'_snapshot').html('<img src="'+STATIC_URL+'img/loader.gif" title="创建快照中" />');
    $.ajax({
        type: 'POST',
        url: '/ghost/create_snapshot/',
        data: {
            name: name,
            desc: desc,
            host_ip: host_ip,
            vm_id: vm_id
        },
        dataType: 'json',
        success: function(data){
            //$('#'+vm_id+'_snapshot').html('<i class="icon-camera" id="icon_state{{vm.id}}"></i>');
        }
        
    });
   
    update_vm_status();
}

function delete_snapshot(snapshot_uuid){
     $('#alertModal').modal();
     $('.delete-confirm').unbind('click');
     $('.delete-confirm').click(function(){
            $.ajax({
                type: 'POST',
                url: '/ghost/delete_snapshot/',
                data: {
                    snapshot_uuid: snapshot_uuid,
                },
                dataType: 'json',
                success: function(data){
                    if(data.result == 0){
                        window.location.href='/ghost/list_snapshot/';
                    }else{
                        alert('删除失败')
                    }
                }
        });
    });
}

function delete_from_dropdown(){
    var snapshot_uuid = $('.tr.active').children("td:first").text();
    delete_snapshot(snapshot_uuid);
}

function restore_snapshot(vm_id, snapshot_uuid){
    //alert($("#STATIC_URL").text());
    $('#alertModal').find('p').text('还原将会丢失当前数据，确定要还原吗？');
    $('#alertModal').modal();
    $('.delete-confirm').click(function(){
        var restore_img = $('#do_restore_'+snapshot_uuid).children('img');
        restore_img.attr('src', $("#STATIC_URL").text()+'img/loader.gif');
        $.ajax({
                type: 'POST',
                url: '/ghost/restore_snapshot/',
                data: {
                    vm_id: vm_id,
                    snapshot_uuid: snapshot_uuid,
                },
                dataType: 'json',
                success: function(data){
                    if(data.result == 0){
                        restore_img.attr('src', $("#STATIC_URL").text()+'img/btn_hy.png');
                        $('.'+vm_id+'.pot_state').html('');
                        $('.'+snapshot_uuid+'.pot_state').html('<span title="使用中"></span>');
                    }else{
                        $('#alert_info').text('还原失败！');
                        $('#alert_modal').modal();
                    }
                }
        });
    });
    
}

function check(class_var, obj_var){
    var obj = $('.form-group.'+class_var+"");
    if(obj_var == ""){
        obj.addClass('has-error');
        return false;
    }else{
        if(obj.hasClass('has-error')){
            obj.removeClass('has-error');
        }
        return true;
    }
}
