import pika, time, thread

#########################################
##                                     ##
##  amqp / rabbitmq channel discovery  ##
##                                     ##
##     brute forces amqp channels      ##
##          for those times            ##
##      you forget your channels ;)    ##
##                                     ##
##      now with exchange support!     ##
##                                     ##
#########################################

host = '192.168.1.102'
wordfile = 'english.txt'
threads = 10
exchangemode = True
forceExQuiet = True

## Set exchangemode to true to brute force exchanges instead of queues
## brute forcing exchanges is noisy for speed by default, it attempts to send a blank message to the exchange
## set forceExQuiet to true to use the quiet mode at a reduced speed
## quiet mode will attempt to bind a queue to the exchange

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
	print " [x] Received msg! : %r" % (body,)

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
		global exchangemode
		global forceExQuiet
		print 'trying: ' + pw
		connection = pika.BlockingConnection(pika.ConnectionParameters(host))
		channel = connection.channel()
		try:
			if exchangemode == True:
				if forceExQuiet == True:
					result = channel.queue_declare(exclusive=True)
					queue_name = result.method.queue
					channel.queue_bind(exchange=pw, queue=queue_name)
					channel.queue_unbind(exchange=pw, queue=queue_name)
				else:
					channel.basic_publish(exchange=pw, routing_key='stat', body='')
                        		result = channel.queue_declare(exclusive=True)
			else:
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
	print 'waiting 15 sec for threads to clear'
	time.sleep(15) ##crude way to give threads a sec / timeout to die, usefull for short wordlists
	global good
	print good

main()
