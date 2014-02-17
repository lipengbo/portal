// Some general UI pack related JS
// Extend JS String with repeat method
String.prototype.repeat = function(num) {
    return new Array(num + 1).join(this);
};

(function($) {

  // Add segments to a slider
  $.fn.addSliderSegments = function (amount) {
    return this.each(function () {             
      var segmentGap = 100 / (amount - 1) + "%"
        , segment = "<div class='ui-slider-segment' style='margin-left: " + segmentGap + ";'></div>";
      $(this).prepend(segment.repeat(amount - 2));
    });
  };

  $(function() {
    // jQuery UI Sliders
    var $slider = $("#cpu_slider");
    if ($slider.length) {
      $slider.slider({
        min: 1,
        max: 7,
        value: 1,
        orientation: "horizontal",
        range: "min"
      }).addSliderSegments($slider.slider("option").max);
    }    
    
    var $slider2 = $("#disk_slider");
    if ($slider2.length) {
      $slider2.slider({
        min: 1,
        max: 5,
        value: 1,
        orientation: "horizontal",
        range: "min"
      }).addSliderSegments($slider2.slider("option").max);
    }    
  });
  
})(jQuery);