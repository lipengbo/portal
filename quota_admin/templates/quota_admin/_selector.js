{% load quota_admin_tags %}

    {% quotas %}
	$(".cpu_chose a").click(function(){
        $(this).parent().find("a.vm_active").removeClass("vm_active");
        $(this).addClass("vm_active");
        $('input[name="' + $(this).attr('name') + '"]').val($(this).attr('value'));
    });
    var $slider = $("#mem_slider");
    var mem_range = {{quotas.mem}};
    var disk_range = {{quotas.disk}};
    var range_dict = {'disk': disk_range, 'mem': mem_range}
    if ($slider.length) {
      $slider.slider({
        min: 1,
        max: mem_range.length,
        value: mem_range.indexOf(current_mem) + 1,
        orientation: "horizontal",
        stop: function(event, ui) {
            var value = range_dict[$(this).attr('name')][ui.value - 1];
            $('input[name="' + $(this).attr('name') + '"]').val(value);
        },
        range: "min"
      }).addSliderSegments("quota_mem_slider", $slider.slider("option").max);
    }    
    var $slider = $("#disk_slider");
    if ($slider.length) {
      $slider.slider({
        min: 1,
        max: disk_range.length,
        value: disk_range.indexOf(current_disk) + 1,
        orientation: "horizontal",
        stop: function(event, ui) {
            var value = range_dict[$(this).attr('name')][ui.value - 1];
            $('input[name="' + $(this).attr('name') + '"]').val(value);
        },
        range: "min"
      }).addSliderSegments("quota_disk_slider", $slider.slider("option").max);
    }
