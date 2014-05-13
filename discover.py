import pika, time, thread

#########################################
##                                     ##
##  amqp / rabbitmq channel discovery  ##
##                                     ##
##     brute forces amqp channels      ##
##          for those times            ##
##      you forget your channels ;)    ##
##                                     ##
#########################################

host = '192.168.1.102'
wordfile = 'english.txt'
threads = 10



## This code was written quickly out of neccesity for a single server
## It is messy, and its not guarenteed to work on all setups 
## Enjoy!

def setup():
	global tc
	global wordlist
	global good
	wordlist = []
	good = []
	tc = 0
	f = open(wordfile, 'r')
	for line in f:
	    wordlist.append(line.replace('\r\n','').strip())
	f.close()

def callback(ch, method, properties, body):
	print " [x] Received %r" % (body,)

def loop():
	global tc
        global wordlist
	global threads
	trying = True
	on = 0
	while trying and on < len(wordlist):
		try:
			pw = wordlist[on]
			thread.start_new_thread(trial, (pw,))
			tc += 1
			while tc > threads:
				time.sleep(0.1)
		except:
			trying = False
		on += 1
	print good

def trial(pw):
	try:
		global tc
		global host
		print 'trying: ' + pw
		connection = pika.BlockingConnection(pika.ConnectionParameters(host))
		channel = connection.channel()
		try:
			channel.basic_consume(callback, queue=pw, no_ack=True)
			print 'YES! ' + pw
			try:
				f = open('discovered.' + str(time.time()) + '.txt', 'w')
				f.write(host + ':' + pw)
				f.close()
			except:
				pass
			global good
			good.append(pw)
		except:
			pass
	except:
		pass
	tc -= 1

def main():
	setup()
	loop()

main()
