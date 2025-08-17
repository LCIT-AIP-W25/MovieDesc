# Use the official Nginx image as the base
FROM nginx:alpine

# Copy the frontend files to the Nginx html directory
COPY . /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 8080

# Nginx will automatically start and serve the files