// Some general UI pack related JS
// Extend JS String with repeat method
String.prototype.repeat = function(num) {
    return new Array(num + 1).join(this);
};


(function($) {
	function set_segment(obj, amount, arr, unit){
		return obj.each(function () { 
			var segmentGap = 100 / (amount - 1) + "%";
			var segment = '';
			var temp;
			for(var i=1; i<arr.length - 1; i++){
				temp = arr[i];
				if(temp >= 1024){
					temp = temp/1024;
					unit = 'GB';
				}
				segment += "<div class='ui-slider-segment' style='margin-left: " + segmentGap
							+ ";'><span>" + temp +" "+ unit + "</span></div>";
			}	
			$(this).prepend(segment);
    	});
	}
  // Add segments to a slider
  $.fn.addSliderSegments = function (slider_name, amount) {
	if(slider_name == 'ram_slider'){
		return set_segment(this, amount, rams, 'MB');
    }else if(slider_name == 'disk_slider'){
		return set_segment(this, amount, disks, 'GB');
	}
   
  };

  $(function() {
    // jQuery UI Sliders
    var $slider = $("#ram_slider");
    if ($slider.length) {
      $slider.slider({
        min: 1,
        max: 7,
        value: 2,
        orientation: "horizontal",
        range: "min"
      }).addSliderSegments("ram_slider", $slider.slider("option").max);
    }    
    
  /*/ for quota
  $(function() {
    // jQuery UI Sliders
    var $slider = $("#mem_slider");
    if ($slider.length) {
      $slider.slider({
        min: 1,
        max: 7,
        value: 2,
        orientation: "horizontal",
        range: "min"
      }).addSliderSegments("mem_slider", $slider.slider("option").max);
    }  
   /* var $slider2 = $("#disk_slider");
    if ($slider2.length) {
      $slider2.slider({
        min: 1,
        max: 6,
        value: 1,
        orientation: "horizontal",
        range: "min"
      }).addSliderSegments("disk_slider", $slider2.slider("option").max);
    }    */
    
    
  });


  
})(jQuery);
