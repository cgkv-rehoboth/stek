server {
  listen 80 default_server;
  server_name _;
  root /srv/http/rehobothkerkwoerden.nl;

  location / {
	include         uwsgi_params;
      uwsgi_pass      unix:/srv/http/rehobothkerkwoerden.nl/cgkv.sock;    
  }

  location /static/ {
      autoindex on;
      gzip_static on;
      alias /srv/http/rehobothkerkwoerden.nl/static/;
  }

  location /media/ {
      autoindex on;
      gzip_static on;
      alias /srv/http/rehobothkerkwoerden.nl/media/;
  }
}
