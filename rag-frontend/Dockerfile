# Stage 1: Build the React application
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./
# If using yarn:
# COPY package.json yarn.lock ./

# Install dependencies
# Use npm ci for cleaner installs in CI/CD environments
RUN npm ci
# If using yarn:
# RUN yarn install --frozen-lockfile

# Copy the rest of the application source code
COPY . .

# Build the application
RUN npm run build
# If using yarn:
# RUN yarn build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine

# Remove default nginx website config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the build output from the builder stage to nginx's webroot
# Adjust '/app/build' if your build output directory is different
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx and serve the content
CMD ["nginx", "-g", "daemon off;"]