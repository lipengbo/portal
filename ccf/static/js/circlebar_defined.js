// JavaScript Document
$(function () {		
	//circle bar
	$(".knob").knob();
	// Example of infinite knob, iPod click wheel
	var val,up=0,down=0,i=0
		,$idir = $("div.idir")
		,$ival = $("div.ival")
		,incr = function() { i++; $idir.show().html("+").fadeOut(); $ival.html(i); }
		,decr = function() { i--; $idir.show().html("-").fadeOut(); $ival.html(i); };
		$("input.infinite").knob(
			{
			'min':0
			,'max':20
			,'stopper':false
			,'change':function(v){
						if(val>v){
							if(up){
								decr();
								up=0;
							}else{up=1;down=0;}
						}else{
							if(down){
								incr();
								down=0;
							}else{down=1;up=0;}
						}
						val=v;
					}
			}
		);
});
$(".circle_canvas").each(function(){
//alert("cbc");
//alert($(this).attr("id"));
	var canvasTitle = $(this).attr("data-text");
	var canvasId = $(this).attr("id");       
	var ctxCanvas = document.getElementById(canvasId);
	var context = ctxCanvas.getContext("2d");  
	context.strokeStyle = "#d3d3d3"; 
	context.lineWidth = 2;  
	context.beginPath();         
	context.moveTo(0,10);  
	context.lineTo(40,10);  
	context.stroke();  
	context.closePath();
	
	context.beginPath();   
	context.fillStyle="#01b6ef";    
	context.arc(40,10,2,Math.PI/2,false);
	context.closePath();
	context.fill();
	
	context.fillStyle="#000000";    
	context.fillText(canvasTitle,45,13);        
});
