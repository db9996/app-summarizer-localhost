# Build step
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build  # or yarn build

# Production nginx image to serve SPA
FROM nginx:alpine

# Copy build output to nginx
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose React static site port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


