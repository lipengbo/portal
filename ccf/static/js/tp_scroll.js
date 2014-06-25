$(function(){
    var picLength = $(".wrap_pic .pic").length;
    var lastSecIndex = $(".wrap_pic .pic").last().index() - 1;
    
    $(".wrap_pic .pic").first().css({
        "top":"55px",
        "z-index":"4",
        "opacity":"1"
    });
    $(".wrap_pic .pic").eq(1).css({
        "top":"230px",
        "z-index":"1",
        "opacity":"0.4",
        "height":"100px"
    });
    $(".wrap_pic .pic").last().css({
        "top":"0",
        "z-index":"1",
        "opacity":"0.4",
        "height":"100px"
    });
    $(".wrap_pic .pic:gt(1):not(:last)").css({
        "top":"100px",
        "z-index":"1",
        "opacity":"0",
        "height":"100px"
    });
    $(".btn_next").click(function(){
        if(!$(".wrap_pic .pic").is(":animated")) {
            $(".wrap_pic .pic").first().animate({
                "height":"100px",           
                "top":"0",
                "opacity":"0.4"
            },function(){
                $(this).appendTo(".wrap_pic");
                $(this).css({
                    "z-index":"1"
                });
            });
            $(".wrap_pic .pic").eq(1).animate({
                "top":"55px",          
                "height":"200",
                "opacity":"1"
            }).css({
                "z-index":"4"
            });
            if (picLength <= 3) {
                $(".wrap_pic .pic").last().animate({
                    "top":"230px",
                });
            } else {
                $(".wrap_pic .pic").eq(2).animate({
                    "top":"230px",
                    "opacity":"0.4"
                });
                $(".wrap_pic .pic").last().animate({
                    "top":"55px",
                    "opacity":"0"
                });
            }
         }
    });
    $(".btn_pre").click(function(){
        if(!$(".wrap_pic .pic").is(":animated")) {
            $(".wrap_pic .pic").first().animate({
                "height":"100px",
                "opacity":"0.4",
                "top":"230px"
            },function(){
                $(".wrap_pic .pic").last().prependTo(".wrap_pic");
            }).css({
                "z-index":"1"
            });
            if (picLength <= 3) {
                $(".wrap_pic .pic").eq(1).animate({
                    "top":"0",
                    "opacity":"0.4"
                });
            } else {
                $(".wrap_pic .pic").eq(1).animate({
                    "top":"55px",
                    "opacity":"0"
                });
                $(".wrap_pic .pic").eq(lastSecIndex).animate({
                    "opacity":"0.4",
                    "top":"0"
                });             
            }
            $(".wrap_pic .pic").last().animate({
                "height":"200px",
                "opacity":"1",
                "top":"55px"
            }).css({
                "z-index":"4"
            });
        }       
    });
});