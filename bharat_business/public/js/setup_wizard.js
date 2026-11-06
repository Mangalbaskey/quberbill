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

// Intercept setup_complete call to ensure country, currency, and timezone are always set
$(document).ajaxSend(function (event, jqXHR, settings) {
	if (settings.url && settings.url.includes("setup_complete")) {
		try {
			if (typeof settings.data === "string") {
				if (settings.data.startsWith("{")) {
					let payload = JSON.parse(settings.data);
					if (payload.args) {
						let inner = typeof payload.args === "string" ? JSON.parse(payload.args) : payload.args;
						inner.country = inner.country || "India";
						inner.currency = inner.currency || "INR";
						inner.timezone = inner.timezone || "Asia/Kolkata";
						payload.args = typeof payload.args === "string" ? JSON.stringify(inner) : inner;
						settings.data = JSON.stringify(payload);
					}
				} else {
					let data = new URLSearchParams(settings.data);
					let argsStr = data.get("args");
					if (argsStr) {
						let argsObj = JSON.parse(argsStr);
						argsObj.country = argsObj.country || "India";
						argsObj.currency = argsObj.currency || "INR";
						argsObj.timezone = argsObj.timezone || "Asia/Kolkata";
						data.set("args", JSON.stringify(argsObj));
						settings.data = data.toString();
					}
				}
			}
		} catch (e) {
			console.error("QuberBill parameter injection notice:", e);
		}
	}
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
