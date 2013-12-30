$(function(){
    mainHeightCount();
    $(window).resize(function(){
        mainHeightCount();
    });
});

function mainHeightCount() {
    var winHeight = $(window).height();
    var topHeight = $(".error_top").height();
    var mainHeight = winHeight - topHeight +"px";
    $(".error_main").css("height",mainHeight);
}
