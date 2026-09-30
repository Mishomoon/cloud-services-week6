FROM nginxinc/nginx-unprivileged:alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/screenshots-week5 /usr/share/nginx/html/screenshots-week5

EXPOSE 8080
