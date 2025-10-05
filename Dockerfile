FROM odoo:18.0

# Switch to root to create directories and set permissions
USER root

# Create the custom addons directory
RUN mkdir -p /mnt/extra-addons/custom_addons

# Set proper ownership
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Set the addons path to include your custom modules
# ENV ADDONS_PATH=/mnt/extra-addons/custom_addons,/usr/lib/python3/dist-packages/odoo/addons

# Expose Odoo port
EXPOSE 8069
