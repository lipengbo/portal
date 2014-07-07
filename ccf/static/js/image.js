$(document).ready(function(){
    $('#edit_image').click(function(){
        $('#images_bj').modal();
    });
    
    $('.submit-edit').click(function(){
        var name = $('#image_name').val();
        var desc = $('#image_desc').val();
        if(!(check('name', name) && check('desc', desc))){
            return;
        } 
        $.ajax({
            url : '/plugins/images/update/',
		    type : 'POST',
		    dataType: 'json',
            data: {
                name: $('#image_name').val(),
                desc: $('#image_desc').val(),
                uuid: $('#edit_image').attr('uuid')
            },
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
        window.location.href = '/plugins/images/list/';
    });

    $('#create_submit_btn').click(function(){
        var name = $('#id_name').val();
        var desc = $('#id_description').val();
        if(!(check('name', name) && check('desc', desc))){
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
        $('#alert_info').text('uploading...');
        $('#alert_modal').modal();
    });
});


function delete_image(uuid){
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
                    window.location.href='/plugins/images/list/';
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
