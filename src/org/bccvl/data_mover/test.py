from xmlrpclib import ServerProxy
s = ServerProxy('http://localhost:8080/RPC2', verbose = 1)
print s.say_hello('Khanh')
print s.say_goobye()
