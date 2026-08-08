# Multi-Stage Nginx Production Dockerfile for Planetary Command Surface
FROM node:20-alpine AS build

WORKDIR /app

# Copy root monorepo files
COPY package*.json ./
COPY frontend/packages ./frontend/packages
COPY frontend/apps/command/package*.json ./frontend/apps/command/

# Install and build
RUN npm install
COPY frontend/apps/command ./frontend/apps/command
WORKDIR /app/frontend/apps/command
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine

COPY --from=build /app/frontend/apps/command/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
