# /mnt/nvme/Algo/vietnamese-image-captioning/frontend-vue/Dockerfile

FROM node:16-alpine AS build-stage

WORKDIR /app

# Cài đặt dependencies
COPY package*.json ./
RUN npm install

# Copy code và build
COPY . .
RUN npm run build

# Giai đoạn production
FROM nginx:alpine AS production-stage

# Copy built files
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy cấu hình nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]