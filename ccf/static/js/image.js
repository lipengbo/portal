$(document).ready(function(){
    $('#edit_image').click(function(){
        $('#images_bj').modal();
    });

    $('.submit-edit').click(function(){
        var name = $('#image_name').val();
        var desc = $('#image_desc').val();
        var is_public;
        var post_data; 
        if(!(check('name', name) && check('desc', desc))){
            return;
        } 
        
        post_data = "name="+name+"&desc="+desc+"&uuid="+$('#edit_image').attr('uuid');

        if($('#image_private').attr('checked') == 'checked'){
            post_data = post_data + "&is_public=" + false;
        }else{
            post_data = post_data + "&is_public=" + true;
        }
        
        $.ajax({
            url : '/plugins/images/update/',
		    type : 'POST',
		    dataType: 'json',
            data: post_data,
		    success:function(data){
                $('#images_bj').modal('hide');
                if(data.result == 0){
                    window.location.href = '/plugins/images/list/';
                }
            }
        });
    });
    
    $('.btn-inverse').click(function(){
        window.location.href = '/plugins/images/create/';
    });
    
    $('#create_cancel_btn').click(function(){
        window.location.href = '/plugins/images/list/0/';
    });

    $('#create_submit_btn').click(function(){
        var name = $('#id_name').val();
        var desc = $('#id_description').val();
        var username = $('#id_image_username').val();
        var passwd = $('#id_image_passwd').val();
        if(!(check('name', name) && check('desc', desc) && check('username', username) && check('passwd', passwd))){
            return;
        } 
        if($('#local_file').attr('checked') == "checked"){
            if(!(check('file', $('#textfile').val()))){
                return;
            }
        }else{
            if(!(check('url', $('#id_location').val()))){
                return;
            }
        }    
        $('form').submit();
        $('#alert_info').text('上传中，这个过程可能需要几分钟...');
        $('#alert_modal').modal();
    });
    var image_type = $('#image_type').attr('type');
    if(image_type != 0){
        var type;
        if(image_type == 1){
            type = 'app';
        }else if(image_type == 2){
            type = 'pri';
        }
        $('.action_box_tab').children('li').removeClass('active');
        $('.tab_'+type).addClass('active');
        $('.action_box_tab_block').removeAttr('style');
        $('.action_box_tab_block.'+type).attr('style', 'display: block;');
    }

});

function delete_image(uuid, type){
    
     $('#alertModal').modal();
     $('.delete-confirm').unbind('click');
     $('.delete-confirm').click(function(){
            $.ajax({
                type: 'POST',
                url: '/plugins/images/delete/',
                data: {
                    uuid: uuid
                },
                dataType: 'json',
                success: function(data){
                    location.href='/plugins/images/list/' + type +"/";
                    
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

