# Put this in /var/www/resque-web/config/unicorn.rb

worker_processes 2
working_directory "/var/www/resque-web";

# This loads the application in the master process before forking
# worker processes
# Read more about it here:
# http://unicorn.bogomips.org/Unicorn/Configurator.html
preload_app true
timeout 45

# This is where we specify the socket.
# We will point the upstream Nginx module to this socket later on
listen "/var/run/unicorn.sock", :backlog => 64 #directory structure needs to be created.
pid "/var/run/unicorn.resque-web.pid" # make sure this points to a valid directory.
#listen "/tmp/resque.etagwerker.com.sock", :backlog => 64
#listen 9292, :tcp_nopush => true
#user "runner", "runner"

# Set the path of the log files inside the log folder of the testapp
stderr_path "/var/www/resque-web/log/unicorn.stderr.log"
stdout_path "/var/www/resque-web/log/unicorn.stdout.log"

shared_path = "var/www/resque-web/shared"
