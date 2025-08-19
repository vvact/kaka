# Base image
FROM nginx:1.25.3-alpine

LABEL maintainer="api.vbm7752@gmail.com"
LABEL project="ecommerce"
LABEL description="Nginx setup for Django Ecommerce project"

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom nginx config
COPY default.conf /etc/nginx/conf.d/

# Create directory for static files
RUN mkdir -p /staticfiles /mediafiles

# Expose port 80
EXPOSE 80

# Command to start nginx (optional, default CMD in nginx image already does this)
# CMD ["nginx", "-g", "daemon off;"]