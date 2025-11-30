FROM nginx:stable-alpine-slim

# Set working directory to Nginx's default html folder
WORKDIR /usr/share/nginx/html

# Remove default Nginx page
RUN rm -rf ./*

# Copy your static files (index.html, CSS, JS, images, etc.)
COPY . .

# Expose HTTP port
EXPOSE 80

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
