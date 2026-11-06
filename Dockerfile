FROM frappe/erpnext:v16.53.0

USER frappe
WORKDIR /home/frappe/frappe-bench

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
