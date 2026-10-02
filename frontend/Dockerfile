FROM nginxinc/nginx-unprivileged:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY screenshots-week6 /usr/share/nginx/html/screenshots-week6

EXPOSE 8080