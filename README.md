Nginx Role
------------

Install and configure nginx

Requirements
------------

 - ansible >= 2.16
 - python >= 3.6

TODO
--------------

Role Variables
--------------

```yaml
# code: language=ansible
---

# 01 # Repositories

# stable / mainline / sys (not implemented yet)
nginx_branch: "stable"

# 03 # Configure

nginx_daemon: "on"

nginx_error_log: "/var/log/nginx/error.log"
nginx_error_log_level: "notice"

nginx_pid: "/var/run/nginx.pid"
nginx_master_process: "on"

nginx_user: "nginx"
nginx_group: "nginx"

nginx_worker_priority: "0"
nginx_worker_processes: "auto"
nginx_worker_rlimit_core: ~
nginx_worker_rlimit_nofile: "1024"
nginx_worker_shutdown_timeout: ~

nginx_events_accept_mutex: "off"
nginx_events_accept_mutex_delay: "500ms"
nginx_events_worker_aio_requests: "32"
nginx_events_worker_connections: "1024"
nginx_working_directory: ~

nginx_http_default_type: "application/octet-stream"

# default: /var/log/nginx/access.log
nginx_http_access_log: "/var/log/nginx/access.json.log"
# default: main
nginx_http_access_log_format: "json"

nginx_http_server_tokens: "off"
nginx_http_charset: "utf-8"
nginx_http_chunked_transfer_encoding: "on"
nginx_http_client_max_body_size: "32M"
nginx_http_client_body_buffer_size: "32M"

nginx_http_sendfile: "on"
nginx_http_keepalive_timeout: "65"

# default: []
# Upload custom certificates to server
# Certificates saved at /etc/nginx/ssl/{{ name }}
nginx_certs:
  - name: "example.com.crt"
    data: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      ...
  - name: "example.com.key"
    data: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      ...

# Stream module configs
# result:
# stream {
#    upstream kube_api_https {
#        server 10.0.0.11:6443;
#        server 10.0.0.12:6443;
#        server 10.0.0.13:6443;
#    }
#    server {
#        listen 6443;
#        proxy_pass kube_api_https;
#    }
#}
nginx_stream:
  upstreams:
    - name: "kube_api_https"
      servers:
        - "10.0.0.11:6443"
        - "10.0.0.12:6443"
        - "10.0.0.13:6443"
  servers:
    - name: "kube_api"
      listen: 6443
      proxy_pass: "kube_api_https"
      proxy_protocol: false

# HTTP module configs
nginx_http:
  # default: []
  maps:
    - name: "enable_http_auth"
      string: "$request_uri"
      variable: "$enable_http_auth"
      rules:
        - get_string: "~^/api/v2/(.*)"
          set_value: "off"
        - get_string: "~^/files/(.*)"
          set_value: "off"
        - get_string: "default"
          set_value: "Restricted"
    - name: "enable_https_redirect"
      string: "$request_uri"
      variable: "$enable_https_redirect"
      rules:
        - get_string: "~^/api/v2/(.*)"
          set_value: "0"
        - get_string: "~^/files/(.*)"
          set_value: "0"
        - get_string: "default"
          set_value: "1"
  upstreams:
    - name: "kube_ingress_http"
      servers:
        - "10.0.0.11:80"
        - "10.0.0.12:80"
        - "10.0.0.13:80"
    - name: "kube_ingress_https"
      servers:
        - "10.0.0.11:443"
        - "10.0.0.12:443"
        - "10.0.0.13:443"
  servers:
    - name: "com.example"
      # Your own template (add extension .conf.j2 to file)
      # Put templates in hidden folder, ansible ignore .folders
      #   when read inventory
      template: "{{ inventory_dir }}/.templates/tpl-prj-example"
      vars: # use {{ item.vars }} in template
        domains:
          - "example.com"
        root: "/home/apps/example.com/current/web"
        index: "index.php"
        client_max_body_size: 0
        access_log: "/var/log/nginx/access.json.log"
        access_log_format: "json"
        error_log: "/var/log/nginx/error.log"
        fastcgi_pass: "127.0.0.1:9001"
        enable_web_auth: true
```

Dependencies
------------

```shell
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
```

License
-------

MIT
