$(function(){
    $("ul.action_box_tab li a").click(function(){
        var tabIndex = $(this).parent("li").index();
        if(!$(".action_box_tab_blocks .action_box_tab_block").is(":animated")) {
            if($(".action_box_tab_blocks .action_box_tab_block").eq(tabIndex).is(":hidden")) {
                $("ul.action_box_tab li").removeClass("active");
                $(this).parent("li").addClass("active");
                $(".action_box_tab_blocks .action_box_tab_block").hide().eq(tabIndex).fadeIn();
            }           
        }      
    });
});
