# WordChecker-backend-django

docker exec -it wordChecker-backend /bin/bash


server {
        listen 80;
        server_name 18.181.223.238;

        location = /favicon.ico {access_log off; log_not_found off;}
        location /static/ {
                root /home/ubuntu/langlink-backend;
        }

        location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/langlink-backend/wordChecker.sock;
        }
}