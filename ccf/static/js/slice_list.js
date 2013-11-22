$(function() {

    $(".knob").knob({
        change : function (value) {
            //console.log("change : " + value);
        },
        release : function (value) {
            //console.log(this.$.attr('value'));
            console.log("release : " + value);
        },
        cancel : function () {
            console.log("cancel : ", this);
        },
        draw : function () {

            // "tron" case
            if(this.$.data('skin') == 'tron') {

                var a = this.angle(this.cv)  // Angle
                    , sa = this.startAngle          // Previous start angle
                    , sat = this.startAngle         // Start angle
                    , ea                            // Previous end angle
                    , eat = sat + a                 // End angle
                    , r = 1;

                this.g.lineWidth = this.lineWidth;

                this.o.cursor
                    && (sat = eat - 0.3)
                    && (eat = eat + 0.3);

                if (this.o.displayPrevious) {
                    ea = this.startAngle + this.angle(this.v);
                    this.o.cursor
                        && (sa = ea - 0.3)
                        && (ea = ea + 0.3);
                    this.g.beginPath();
                    this.g.strokeStyle = this.pColor;
                    this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sa, ea, false);
                    this.g.stroke();
                }

                this.g.beginPath();
                this.g.strokeStyle = r ? this.o.fgColor : this.fgColor ;
                this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sat, eat, false);
                this.g.stroke();

                this.g.lineWidth = 2;
                this.g.beginPath();
                this.g.strokeStyle = this.o.fgColor;
                this.g.arc( this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
                this.g.stroke();
       
                 
                    this.g.strokeStyle ='hsl(120,50%,50%)';//线条颜色：绿色
                    this.g.lineWidth = 1;//设置线宽
                    this.g.beginPath();
                    this.g.moveTo(0,0);
                    this.g.lineTo(100,200);
                    this.g.closePath();//可以把这句注释掉再运行比较下不同
                    this.g.stroke();//画线框
                    this.g.fill();//填充颜色
                    //this.g.font = “12px Arial”;
                
                return false;
            }
        }
    });

    // Example of infinite knob, iPod click wheel
    var v, up=0,down=0,i=0
        ,$idir = $("div.idir")
        ,$ival = $("div.ival")
        ,incr = function() { i++; $idir.show().html("+").fadeOut(); $ival.html(i); }
        ,decr = function() { i--; $idir.show().html("-").fadeOut(); $ival.html(i); };
    $("input.infinite").knob(
                        {
                        min : 0
                        , max : 20
                        , stopper : false
                        , change : function () {
                                        if(v > this.cv){
                                            if(up){
                                                decr();
                                                up=0;
                                            }else{up=1;down=0;}
                                        } else {
                                            if(v < this.cv){
                                                if(down){
                                                    incr();
                                                    down=0;
                                                }else{down=1;up=0;}
                                            }
                                        }
                                        v = this.cv;
                                    }
                        });
});


    $(".circle_canvas").each(function(){
    alert("cbc");
    alert($(this).attr("id"));
        var canvasTitle = $(this).attr("data-text");
        var canvasId = $(this).attr("id");       
        var ctxCanvas = document.getElementById(canvasId);
        var context = ctxCanvas.getContext("2d");  
        context.strokeStyle = "#d3d3d3"; 
        context.lineWidth = 2;  
        context.beginPath();         
        context.moveTo(0,10);  
        context.lineTo(50,10);  
        context.stroke();  
        context.closePath();
        
        context.beginPath();   
        context.fillStyle="#01b6ef";    
        context.arc(50,10,2,Math.PI/2,false);
        context.closePath();
        context.fill();
        
        context.fillStyle="#000000";    
        context.fillText(canvasTitle,55,13);        
    });

