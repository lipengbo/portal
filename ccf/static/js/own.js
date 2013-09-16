$(document).ready(function() {
	$(".bs-docs-sidenav li a").click(function() {
		var navHeight = $(".navbar").height();
		$("html, body").animate({
			scrollTop: $($(this).attr("href")).offset().top - navHeight + "px"
			}, {
			duration: 500,
			easing: "swing"
		});
		$(".bs-docs-sidenav li").removeClass();
		$(this).parent("li").addClass("active");
		return false;
	});
});