# FixForesight Frontend Dockerfile - Multi-stage

# Stage 1: Build React bundles
FROM node:18-alpine AS builder
WORKDIR /app

# Install packages
COPY package.json .
RUN npm install

# Copy source and config files
COPY . .

# Build for production
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose default HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
