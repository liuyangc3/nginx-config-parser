# nginx_config_parser
config 内容
```
server {
    listen 443;
    server_name  jr.p.nxin.com jr.t.nxin.com;

    location ~ / {
        proxy_pass http://dbn_nfd;
    }


    location ~ /.*\.(|html|ico|png|jpg|js|css|gif)$ {
       expires    1d;
    }

    location ~ /(web|app)/(wallet|orgwallet|callback)/.*\.shtml$ {
        proxy_pass http://jr-web;
    }

#    location ~ /(newnfb|member) {
#        proxy_set_header SSL_CERT $ssl_client_cert;
#        proxy_set_header X-Real-IP $remote_addr;
#        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#        proxy_pass http://fundCenter;
#    }


    location ~ /*\.(|action|shtml|jsp)$ {
        proxy_pass http://nongxin2-0;
    }
}

server
{
    listen 80;
    server_name jr.p.nxin.com;

    location ~ / {
        proxy_pass http://fuck80;
    }
}

```

测试输出结果
[]
