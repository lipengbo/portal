$(function(){
    $(".pop_chose_block .cpu_chose").find("a").click(function(){
        $(this).addClass("vm_active").siblings().removeClass("vm_active");
    });
});
