SSL certificates 
====

I usually put my SSL certificates and key in here.  It's probably not the more secure thing in the world but it's convenient.  So the files here should be:

domain.com.key
domain.com.crt

----

### Notes:

For Apache:
Use: gd_bundle.crt and domain.com.crt

For Nginx:
Use: domain.com.bundle.crt

+ GoDaddy: http://blog.robodomain.com/post/3698910833/godaddy-ssl-certificates-and-nginx
+ Comodo: http://notes.rioastamal.net/2012/04/nginx-install-comodo-positivessl.html