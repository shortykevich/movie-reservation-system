```shell
mkdir certs && cd certs
openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -out PEM -pubout -out jwt-public.pem
```# movie-reservation-system
