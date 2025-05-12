#!/bin/bash

# Display current timezone
echo "Current timezone: $(timedatectl | grep 'Time zone')"

# Set timezone to Asia/Kolkata (Indian Standard Time)
sudo timedatectl set-timezone Asia/Kolkata

# Verify the change
echo "New timezone: $(timedatectl | grep 'Time zone')"

# Restart your application service if needed
# sudo systemctl restart your-app-service
