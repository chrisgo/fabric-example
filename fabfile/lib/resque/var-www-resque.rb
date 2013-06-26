# Put this in /var/www/resque-web/config/resque.rb

require 'resque'

Resque.redis = Redis.new(:password => '{{password}}')
