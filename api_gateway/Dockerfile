FROM nginx:1.25-alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom static reverse proxy configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose standard port 80 for the gateway
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
