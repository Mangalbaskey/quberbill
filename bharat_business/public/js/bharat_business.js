/**
 * bharat_business/public/js/bharat_business.js
 *
 * Global client-side entry point for bharat_business.
 * Loaded for all users who have a Bharat Business role (via hooks.py app_include_js).
 *
 * MILESTONE 01: Stubs only. Full implementation in Milestones 02–04.
 */

frappe.provide('bharat_business');

/**
 * Core namespace for bharat_business client utilities.
 */
bharat_business = {

    /**
     * The business profile data injected at boot (from boot.py).
     * Available after `frappe.boot` is populated.
     */
    get profile() {
        return (frappe.boot && frappe.boot.bharat_business) || {};
    },

    /**
     * Formats a number using the Indian numbering system (₹1,23,456.78).
     * Uses the server-side format for consistency, but provides a
     * client-side fallback for immediate display.
     *
     * @param {number} amount
     * @param {boolean} showSymbol
     * @returns {string}
     */
    formatINR(amount, showSymbol = true) {
        if (amount === null || amount === undefined) return '';
        const num = parseFloat(amount);
        if (isNaN(num)) return String(amount);

        const [intPart, decPart] = Math.abs(num).toFixed(2).split('.');
        let formatted = '';
        if (intPart.length > 3) {
            const last3 = intPart.slice(-3);
            let rest = intPart.slice(0, -3);
            const parts = [];
            while (rest.length > 2) {
                parts.unshift(rest.slice(-2));
                rest = rest.slice(0, -2);
            }
            if (rest) parts.unshift(rest);
            formatted = parts.join(',') + ',' + last3;
        } else {
            formatted = intPart;
        }

        const sign = num < 0 ? '-' : '';
        const symbol = showSymbol ? '₹' : '';
        return `${sign}${symbol}${formatted}.${decPart}`;
    },

    /**
     * Navigate to the onboarding wizard page if onboarding is not complete.
     */
    checkOnboarding() {
        const profile = this.profile;
        if (profile.enabled && !profile.onboarding_complete) {
            frappe.set_route('bb_onboarding');
        }
    },

    /**
     * Returns true if the current user has any Bharat Business role.
     */
    isBBUser() {
        return (frappe.user_roles || []).some(r => r.startsWith('Bharat Business'));
    },
};

// On every page load, redirect to onboarding if not complete
frappe.after_ajax(function () {
    if (bharat_business.isBBUser()) {
        bharat_business.checkOnboarding();
    }
});
