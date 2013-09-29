$(function(){
    judgeProject();
    $(".close").click(function(){
        judgeProject();
    });
});
//项目管理页面，项目展示部分切换
function judgeProject(){
    if($(".example-sites").length==0){
        $(".nothing_tip").show();
    } else {
        $(".nothing_tip").hide();
    }
}