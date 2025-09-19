FROM odoo:18.0

# Copy your custom Tasks app
COPY addons/tasks_app /mnt/extra-addons/tasks_app

# Set the addons path to include your custom module
ENV ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

# Expose Odoo port
EXPOSE 8069

# Use the default Odoo entrypoint
USER odoo
