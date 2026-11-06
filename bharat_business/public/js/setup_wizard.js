frappe.provide("frappe.setup");
frappe.provide("frappe.wizard");

frappe.setup.on("before_load", function () {
	// Set default wizard values so downstream slides have access
	if (!frappe.wizard.values) frappe.wizard.values = {};
	frappe.wizard.values.country = "India";
	frappe.wizard.values.currency = "INR";
	frappe.wizard.values.timezone = "Asia/Kolkata";

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

// Helper to ensure Chart of Accounts options are populated on Step 2
function checkAndPopulateCOA() {
	if (!frappe.wizard.values) frappe.wizard.values = {};
	frappe.wizard.values.country = "India";
	frappe.wizard.values.currency = "INR";

	const coaSelect = $('select[data-fieldname="chart_of_accounts"]');
	if (coaSelect.length) {
		const currentOptions = coaSelect.find("option");
		// If empty or only blank placeholder exists
		if (currentOptions.length <= 1) {
			const options = [
				{ value: "Standard", text: "Standard" },
				{ value: "India - Chart of Accounts", text: "India - Chart of Accounts" },
			];
			coaSelect.empty();
			options.forEach(function (opt) {
				coaSelect.append($("<option>", { value: opt.value, text: opt.text }));
			});
			coaSelect.val("Standard").trigger("change");
		}
	}

	// Auto-populate Financial Year if blank
	const fyInput = $('input[data-fieldname="fy_start_date"]');
	if (fyInput.length && !fyInput.val()) {
		const today = new Date();
		const year = today.getFullYear();
		// Indian FY starts April 1st
		const fyStart = today.getMonth() >= 3 ? `${year}-04-01` : `${year - 1}-04-01`;
		fyInput.val(fyStart).trigger("change");
	}
}

// Intercept setup_complete call to ensure country, currency, and chart of accounts are always set
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
						inner.chart_of_accounts = inner.chart_of_accounts || "Standard";
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
						argsObj.chart_of_accounts = argsObj.chart_of_accounts || "Standard";
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
	// Periodic check for slide 2 elements
	setInterval(checkAndPopulateCOA, 500);

	const observer = new MutationObserver(function () {
		const logos = document.querySelectorAll(".setup-intro__logo");
		logos.forEach(function (logo) {
			if (logo.getAttribute("src") !== "/assets/bharat_business/images/quberbill-icon.png") {
				logo.setAttribute("src", "/assets/bharat_business/images/quberbill-icon.png");
			}
		});
		checkAndPopulateCOA();
	});
	observer.observe(document.body, { childList: true, subtree: true });
});
