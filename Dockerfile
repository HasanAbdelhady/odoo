FROM odoo:18.0

# Switch to root to create directories and set permissions
USER root

# Create the custom addons directory
RUN mkdir -p /mnt/extra-addons/custom_addons && \
    chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Expose Odoo port
EXPOSE 8069
