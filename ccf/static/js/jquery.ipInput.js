/*
 * jQuery Plugin: ip input box
 * Version 0.1
 *
 * Copyright (c) 2010 hjzheng 
 * Licensed jointly under the GPL and MIT licenses,
 * choose which one suits your project best!
 *
 * altered by ChenyangGe Jul/03/2012
 */


(function($){  
     
	 $.fn.ipInput = function(){   
        
	 return this.each(function(){
		     
        //将元素集合赋给变量 本例中是div对象 
        var $div = $(this);
		$div.addClass("ipInput-border");
		//初始化input元素			
		
		for(var i=0;i<4;i++){
			var input = $("<input type='text' id='cip"+i+"' maxlength='3' disabled />")
				.addClass("ipInput-cell")
				.blur(function(event){
					var $input = $(this);
					var text = $input.val();
					if(text.length==0){
						$input.val("");
					}
					
					
				})
				.focus(function(event){
				if($.browser.msie) 
					this.createTextRange().select();
				else {
					this.selectionStart = 0;
					this.selectionEnd = this.value.length;
				}

			})
				.keyup(function(event){
					//获取keyCode值
					var keyCode = event.which;
					//input框
					var $input = $(this);
					//获取input框中的value
					var text = $input.val();

					
					//处理text中非数字字符
					$input.val(text.replace(/[^\d]/g,''));

					
					//防止左右键和Tab键自动跳
					//if(keyCode == 39 || keyCode == 37)  return false;	
					if(keyCode == 9){
						$input.focus();
						return false;
					}
					if(text.length==0&&keyCode==8){
						$input.prevAll("input").first().focus();
						return false;
					}
						if(text.length >= 3){
							if(parseInt(text)>=256 || parseInt(text)<=0){ 
								//alert("请输入0~255之间的数");
								//$("div#slice_alert_info").empty();
                                //var str = "" + "<p class=\"text-center\">" + "请输入0~255之间的数" + "</p>";
                                //$("div#slice_alert_info").append(str);
                                //$('#slicealertModal').modal('show');
								$input.val(0);
								$input[0].focus(); 
								return false; 
							}else{  
								$input.nextAll("input")[0].focus();
								$input[0].blur(); 
							}					
						}
						//输入点时 自动跳到下一个
						if(text.length > 0 && (keyCode == 110 || keyCode == 190)){
								$input.nextAll("input")[0].focus();
								$input[0].blur(); 
						}
						
				});

			//输入IP的分割点
			$div.append(input).append($("<span>.</span>"));
		}
		//清空最后一个 .
		$div.children(":last").empty();
		
	  }); 
    };  
})(jQuery); 

function init_ipinput(){
    var slice_id = $("#slice_id").text();
    if(slice_id>=0){
        
        controller_ip = $("#controller_ip_old").text();
        controller_port = $("#controller_port_old").text();
        if(controller_ip && controller_port){
            ips = controller_ip.split(".");
            cip0_obj = document.getElementById("cip0");
            cip1_obj = document.getElementById("cip1");
            cip2_obj = document.getElementById("cip2");
            cip3_obj = document.getElementById("cip3");
            controller_port_obj = document.getElementById("controller_port");
            cip0_obj.value = ips[0];
            cip1_obj.value = ips[1];
            cip2_obj.value = ips[2];
            cip3_obj.value = ips[3];
            controller_port_obj.value = controller_port;
            $(".tab_radio2").parent("td").siblings("td").children("#ipInput").css({"background":"#fff"}).removeClass("disabled");        
            $(".tab_radio2").parent("td").siblings("td").children("#ipInput").children("input").removeAttr("disabled");
            $(".tab_radio2").parent("td").siblings("td").children("input").removeAttr("disabled");
        }   
    }
}
               
