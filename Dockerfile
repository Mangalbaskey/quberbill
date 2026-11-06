FROM frappe/erpnext:v16.53.0

USER frappe
WORKDIR /home/frappe/frappe-bench

# Stub package for india_compliance to prevent ModuleNotFoundError if previously registered in DB
RUN mkdir -p /home/frappe/frappe-bench/apps/india_compliance/india_compliance \
    && echo '{"name": "india_compliance", "version": "0.0.1"}' > /home/frappe/frappe-bench/apps/india_compliance/package.json \
    && printf 'from setuptools import setup, find_packages\nsetup(name="india_compliance", version="0.0.1", packages=find_packages())\n' > /home/frappe/frappe-bench/apps/india_compliance/setup.py \
    && printf '__version__ = "0.0.1"\n' > /home/frappe/frappe-bench/apps/india_compliance/india_compliance/__init__.py \
    && printf 'app_name = "india_compliance"\napp_title = "India Compliance"\napp_publisher = "Stub"\napp_description = "Stub"\napp_icon = "octicon octicon-file-directory"\napp_color = "grey"\napp_email = "stub@example.com"\napp_license = "MIT"\n' > /home/frappe/frappe-bench/apps/india_compliance/india_compliance/hooks.py \
    && /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/india_compliance

# Copy QuberBill (bharat_business) application code
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/bharat_business

# Install the app into the bench python virtual environment
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/bharat_business \
    && echo "bharat_business" >> /home/frappe/frappe-bench/sites/apps.txt

# Bake static assets into the image-layer storage so entrypoint links them to volume
RUN if [ -d "/home/frappe/frappe-bench/apps/bharat_business/bharat_business/public" ]; then \
        mkdir -p /home/frappe/frappe-bench/assets/bharat_business && \
        cp -r /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/* /home/frappe/frappe-bench/assets/bharat_business/ 2>/dev/null || true; \
    fi

# Replace ERPNext and Frappe logos with QuberBill branding in app layers and assets
RUN cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/apps/erpnext/erpnext/public/images/erpnext-logo.svg 2>/dev/null || true \
    && cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/apps/erpnext/erpnext/public/images/erp-icon.svg 2>/dev/null || true \
    && cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/apps/frappe/frappe/public/images/frappe-framework-logo.svg 2>/dev/null || true \
    && cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.png /home/frappe/frappe-bench/apps/erpnext/erpnext/public/images/erpnext-icon.png 2>/dev/null || true \
    && cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.png /home/frappe/frappe-bench/apps/frappe/frappe/public/images/frappe-icon.png 2>/dev/null || true \
    && if [ -d "/home/frappe/frappe-bench/assets/erpnext/images" ]; then \
        cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/assets/erpnext/images/erpnext-logo.svg 2>/dev/null || true; \
        cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/assets/erpnext/images/erp-icon.svg 2>/dev/null || true; \
        cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.png /home/frappe/frappe-bench/assets/erpnext/images/erpnext-icon.png 2>/dev/null || true; \
    fi \
    && if [ -d "/home/frappe/frappe-bench/assets/frappe/images" ]; then \
        cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.svg /home/frappe/frappe-bench/assets/frappe/images/frappe-framework-logo.svg 2>/dev/null || true; \
        cp /home/frappe/frappe-bench/apps/bharat_business/bharat_business/public/images/quberbill-icon.png /home/frappe/frappe-bench/assets/frappe/images/frappe-icon.png 2>/dev/null || true; \
    fi
