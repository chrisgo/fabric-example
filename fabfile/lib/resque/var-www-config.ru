#!/usr/bin/env ruby

# Put this in /var/www/resque-web/config.ru

require 'logger'
require 'resque/server'

$LOAD_PATH.unshift ::File.expand_path(::File.dirname(__FILE__) + '/lib')

# Add some basic authentication
Resque::Server.use Rack::Auth::Basic do |username, password|
	password == '{{password}}' # password
end

# Set the RESQUE_CONFIG env variable if you’ve a `resque.rb` or similar
# config file you want loaded on boot.
if ENV['RESQUE_CONFIG'] && ::File.exists?(::File.expand_path(ENV['RESQUE_CONFIG']))
	load ::File.expand_path(ENV['RESQUE_CONFIG'])
end

Resque.redis = Redis.new(:host => '{{host}}', :port => {{port}}, :password => '{{password}}')

use Rack::ShowExceptions
run Resque::Server.new
