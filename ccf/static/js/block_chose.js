$(function(){    
    $(".block_chose a").live("click",function(){
        $(".block_chose a").removeClass("active");
        $(this).addClass("active");
    });
});
