frappe.provide("frappe.setup");

frappe.setup.on("before_load", function () {
	frappe.setup.intro_apps = [
		{
			name: "bharat_business",
			logo: "/assets/bharat_business/images/quberbill-icon.png",
			title: "QuberBill",
			setup_wizard_text: __("Smart Billing & Operating Platform for Indian Businesses."),
		},
	];

	setTimeout(function () {
		$(".setup-intro__logo").attr("src", "/assets/bharat_business/images/quberbill-icon.png");
		$(".setup-intro__tagline").text(__("Smart Billing & Operating Platform for Indian Businesses."));
	}, 50);
});

$(document).ready(function () {
	const observer = new MutationObserver(function () {
		const logos = document.querySelectorAll(".setup-intro__logo");
		logos.forEach(function (logo) {
			if (logo.getAttribute("src") !== "/assets/bharat_business/images/quberbill-icon.png") {
				logo.setAttribute("src", "/assets/bharat_business/images/quberbill-icon.png");
			}
		});
	});
	observer.observe(document.body, { childList: true, subtree: true });
});
