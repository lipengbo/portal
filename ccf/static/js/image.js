$(document).ready(function(){
    $('#edit_image').click(function(){
        $('#images_bj').modal();
    });
    
    $('.submit-edit').click(function(){
        
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
        window.location.href = '/plugins/images/create/'
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
