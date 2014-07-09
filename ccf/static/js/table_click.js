$(function(){
    
    $(".row_chose tbody tr").hover(function(){
        if(!$(this).hasClass("active")) {
            $(this).addClass("row_hover");
        }
    },function(){
        $(this).removeClass("row_hover");
    });
    
    $(".row_chose tbody tr td").click(function(){     
        var tableId = $(this).parent("tr").parent("tbody").parent(".row_chose").attr("id");      
        var $tableId = $("#" + tableId);   
        var activeLength = $tableId.children("tbody").children("tr.active").length;
 
     
            if($(this).parent("tr").hasClass("active")) {
                $(this).parent("tr").removeClass("active");
            } else {
                $(this).parent("tr").siblings().removeClass("active");
                $(this).parent("tr").addClass("active");
            }
          
         
        play(tableId);     
    });
    
});

function play(id) {
    var $id = $("#" + id);
    var activeLength = $id.children("tbody").find("tr.active").length;   
    if (activeLength == 0) {
        $id.children("thead").find(".oper_menu").children("li").children("a").addClass("disabled");
    } else {
        $id.children("thead").find(".oper_menu").children("li").children("a").removeClass("disabled");
    }      
}
