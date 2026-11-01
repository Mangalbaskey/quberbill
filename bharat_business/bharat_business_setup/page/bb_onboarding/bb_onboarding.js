/**
 * bharat_business/bharat_business_setup/page/bb_onboarding/bb_onboarding.js
 *
 * Onboarding Wizard — 11-step guided setup for Indian business owners.
 *
 * Architecture:
 *   - Pure Frappe Page (no additional framework dependency)
 *   - Each step is rendered by a dedicated renderStep_N() function
 *   - Data is persisted server-side via `save_wizard_step` after each step
 *   - The final step triggers `complete_onboarding` which calls OnboardingService
 *
 * MILESTONE 01: Steps 1 and 2 are fully implemented as proof-of-concept.
 *               Steps 3–11 render a placeholder. Full implementation in Milestone 02.
 */

frappe.pages['bb_onboarding'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Setup Your Business',
        single_column: true,
    });

    new BBOnboardingWizard(page);
};

class BBOnboardingWizard {
    constructor(page) {
        this.page = page;
        this.wizardName = null;
        this.currentStep = 1;
        this.totalSteps = 11;
        this.collectedData = {};

        this.$wrapper = $(this.page.body);
        this.$wrapper.addClass('bb-page');

        this._init();
    }

    async _init() {
        try {
            const state = await frappe.xcall(
                'bharat_business.bharat_business_setup.page.bb_onboarding.bb_onboarding.get_wizard_state'
            );

            if (state.is_complete) {
                this._renderComplete();
                return;
            }

            this.wizardName = state.wizard_name;
            this.currentStep = state.current_step || 1;
            this._render();
        } catch (err) {
            frappe.msgprint({
                title: 'Setup Error',
                message: 'Could not load the setup wizard. Please refresh and try again.',
                indicator: 'red',
            });
        }
    }

    _render() {
        this.$wrapper.html(`
            <div class="bb-container" style="padding-top:32px; padding-bottom:40px;">
                <div class="bb-wizard-step-indicator" id="bb-step-dots"></div>
                <div id="bb-step-content"></div>
            </div>
        `);
        this._renderStepDots();
        this._renderStep(this.currentStep);
    }

    _renderStepDots() {
        const $dots = this.$wrapper.find('#bb-step-dots');
        $dots.empty();
        for (let i = 1; i <= this.totalSteps; i++) {
            const cls = i < this.currentStep ? 'done' : i === this.currentStep ? 'active' : '';
            $dots.append(`<div class="bb-wizard-step-dot ${cls}"></div>`);
        }
    }

    _renderStep(step) {
        this._renderStepDots();
        const $content = this.$wrapper.find('#bb-step-content');
        $content.empty();

        const renderers = {
            1:  () => this._renderStep1($content),
            2:  () => this._renderStep2($content),
            // Steps 3–11: placeholder, completed in Milestone 02
        };

        if (renderers[step]) {
            renderers[step]();
        } else {
            this._renderStepPlaceholder($content, step);
        }
    }

    // -----------------------------------------------------------------------
    // Step 1 — Business Type
    // -----------------------------------------------------------------------
    _renderStep1($content) {
        const types = [
            { key: 'retail',            label: '🏪 Retail Shop',             desc: 'Clothing, electronics, books, gifts' },
            { key: 'grocery',           label: '🛒 Grocery / Kirana',         desc: 'Food, FMCG, daily essentials' },
            { key: 'wholesale',         label: '🏭 Wholesale / Distribution', desc: 'B2B trade, bulk supply' },
            { key: 'restaurant',        label: '🍽️ Restaurant / Café',         desc: 'Dine-in, takeaway, cloud kitchen' },
            { key: 'service_repair',    label: '🔧 Repair / Service',         desc: 'Mobile, AC, plumbing, electrical' },
            { key: 'freelancer_agency', label: '💻 Freelancer / Agency',      desc: 'Design, IT, consulting, CA' },
            { key: 'manufacturing',     label: '⚙️ Manufacturing',             desc: 'Production, assembly, workshop' },
        ];

        const cards = types.map(t => `
            <div class="bb-business-type-card bb-card"
                 data-key="${t.key}"
                 style="cursor:pointer; transition:border 0.15s ease; border:2px solid var(--bb-border);">
                <div style="font-size:18px; font-weight:600; margin-bottom:4px;">${t.label}</div>
                <div style="font-size:14px; color:var(--bb-text-muted);">${t.desc}</div>
            </div>
        `).join('');

        $content.html(`
            <div class="bb-card" style="border:none; box-shadow:none; padding:0;">
                <div style="font-size:13px; color:var(--bb-text-muted); margin-bottom:8px;">
                    Step ${this.currentStep} of ${this.totalSteps}
                </div>
                <h2 style="font-size:22px; font-weight:700; margin-bottom:8px;">
                    What kind of business do you run?
                </h2>
                <p style="color:var(--bb-text-muted); margin-bottom:24px;">
                    We'll set up the right tools for your business automatically.
                </p>
                ${cards}
            </div>
        `);

        $content.find('.bb-business-type-card').on('click', async (e) => {
            const key = $(e.currentTarget).data('key');
            $content.find('.bb-business-type-card').css('border', '2px solid var(--bb-border)');
            $(e.currentTarget).css('border', '2px solid var(--bb-primary)');
            await this._saveStep(1, { business_type: key });
            this.collectedData.business_type = key;
            this.currentStep = 2;
            this._renderStep(2);
        });
    }

    // -----------------------------------------------------------------------
    // Step 2 — Business Name
    // -----------------------------------------------------------------------
    _renderStep2($content) {
        $content.html(`
            <div class="bb-card" style="border:none; box-shadow:none; padding:0;">
                <div style="font-size:13px; color:var(--bb-text-muted); margin-bottom:8px;">
                    Step ${this.currentStep} of ${this.totalSteps}
                </div>
                <h2 style="font-size:22px; font-weight:700; margin-bottom:8px;">
                    What is your business name?
                </h2>
                <p style="color:var(--bb-text-muted); margin-bottom:24px;">
                    Use the name as it appears on your bills or GST certificate.
                </p>
                <label class="bb-label">Business Name *</label>
                <input type="text" id="bb-business-name" class="bb-input"
                       placeholder="e.g. Sharma General Store" autocomplete="organization">
                <div id="bb-name-error" style="color:#DC2626; font-size:13px; margin-top:6px; display:none;"></div>
                <button class="bb-btn bb-btn-primary bb-btn-full" id="bb-step2-next" style="margin-top:24px;">
                    Continue →
                </button>
                <button class="bb-btn bb-btn-secondary bb-btn-full" id="bb-step2-back" style="margin-top:8px;">
                    ← Back
                </button>
            </div>
        `);

        $content.find('#bb-step2-back').on('click', () => {
            this.currentStep = 1;
            this._renderStep(1);
        });

        $content.find('#bb-step2-next').on('click', async () => {
            const name = $content.find('#bb-business-name').val().trim();
            if (!name || name.length < 2) {
                $content.find('#bb-name-error').text('Please enter a valid business name.').show();
                return;
            }
            $content.find('#bb-name-error').hide();
            await this._saveStep(2, { business_name: name });
            this.collectedData.business_name = name;
            this.currentStep = 3;
            this._renderStep(3);
        });

        // Allow Enter key to proceed
        $content.find('#bb-business-name').on('keydown', (e) => {
            if (e.key === 'Enter') $content.find('#bb-step2-next').trigger('click');
        });
    }

    // -----------------------------------------------------------------------
    // Steps 3–11 Placeholder (Milestone 02)
    // -----------------------------------------------------------------------
    _renderStepPlaceholder($content, step) {
        $content.html(`
            <div class="bb-card" style="text-align:center; padding:48px 24px;">
                <div style="font-size:48px; margin-bottom:16px;">🚧</div>
                <h3 style="font-size:20px; font-weight:700; margin-bottom:8px;">
                    Step ${step} — Coming in Milestone 02
                </h3>
                <p style="color:var(--bb-text-muted); margin-bottom:32px;">
                    The full wizard is being built milestone by milestone.<br>
                    This step (${step}/${this.totalSteps}) will be ready soon.
                </p>
                <button class="bb-btn bb-btn-secondary" id="bb-placeholder-back">
                    ← Back
                </button>
            </div>
        `);
        $content.find('#bb-placeholder-back').on('click', () => {
            this.currentStep = Math.max(1, step - 1);
            this._renderStep(this.currentStep);
        });
    }

    // -----------------------------------------------------------------------
    // Complete screen
    // -----------------------------------------------------------------------
    _renderComplete() {
        this.$wrapper.html(`
            <div class="bb-container" style="padding-top:64px; text-align:center;">
                <div style="font-size:64px; margin-bottom:16px;">✅</div>
                <h2 style="font-size:26px; font-weight:700; margin-bottom:8px;">
                    You're all set!
                </h2>
                <p style="color:var(--bb-text-muted); font-size:16px; margin-bottom:32px;">
                    Your business has been set up. Let's start billing.
                </p>
                <a href="/bb_dashboard" class="bb-btn bb-btn-primary bb-btn-full"
                   style="max-width:320px; margin:0 auto; display:flex;">
                    Go to Dashboard →
                </a>
            </div>
        `);
    }

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------
    async _saveStep(step, data) {
        if (!this.wizardName) return;
        try {
            await frappe.xcall(
                'bharat_business.bharat_business_setup.page.bb_onboarding.bb_onboarding.save_wizard_step',
                {
                    wizard_name: this.wizardName,
                    step: step,
                    data: JSON.stringify(data),
                }
            );
        } catch (err) {
            frappe.log_error('BBOnboardingWizard._saveStep', err);
        }
    }
}
