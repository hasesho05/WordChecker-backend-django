# Set the base image to the official Nginx image from Docker Hub
FROM nginx

# Remove default configuration files
# RUN rm /etc/nginx/conf.d/default.conf
# RUN rm /etc/nginx/nginx.conf

# Copy custom configuration files from host into the container
COPY nginx.conf /etc/nginx/
# COPY my-app.conf /etc/nginx/conf.d/

# Expose port 80 to the host machine
EXPOSE 80

# Start Nginx web server
# CMD ["nginx", "-g", "daemon off;"]