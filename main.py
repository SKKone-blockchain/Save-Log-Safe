import parser as ps
import schedule
import cryptomodue as ct
import uploadLogs as ul
import threading
import time
import setproctitle
import modi as md
import uuid

loglists= []
index = 0
last_index = 0
check_interval = 0
upload_interval = 0
w = None
upload_lock = threading.Lock()

def my_random_string(string_length=10):
	"""Returns a random string of length string_length."""
	random = str(uuid.uuid4()) # Convert UUID format to a Python string.
	random = random.upper() # Make all characters uppercase.
	random = random.replace("-","") # Remove the UUID '-'.
	return random[0:string_length] # Return the random string.


def inputpassword():
	count = 0
	while True:
		password = input("input password for checking: ")
		if w.comparepassword(password)[0] is False:
			print("Wrong password!")
			# print('DEBUG) password is ', w.password, 'password hash is',w.passwordhash, w.comparepassword(password)[1])
			count += 1
		else:
			return password
		
		if count > 4:
			return False

def check(start=last_index):
	'''
	for i in range(start, index):
		password = input("input password for checking: ")
		time = int(input("how long would you use same password: "))
		for j in range(i, i+time):
			checkValid(password)	
			i += 1
		if last_index < i:
			last_index = i
	'''
	# check all hash in cidlist
	password = inputpassword()
	hashlist = w.gethashlist()
	for h in hashlist:
		if checkValid(password, h) is False:
			return False
	return True


def checkValid(password, ipfshash=None):
	try:
		'''
		# downanddec need ipfs hash from ethereum(w.ipfs.extract()를 호출하면 /etc/savelog/hash에 저장을 하는 기능을 추가할 수 있습니다.). 
		# ipfshash가 None면 이 프로그램 실행중 ipfs에 업로드한 모든 파일을 다운로드 받아 복호화해봅니다.
		# index가 정확히 어떤 역할인지 모르겠는데, ipfshash를 담은 리스트를 만드는게 낫지 않을까 싶습니다.
		# If something wrong during decrypt, it raise NameError.
		'''
		loglist = w.downanddec(password, ipfshash)
		return True
	except NameError:
		return False
	'''
		loglist 의 파일 형식이 유효한지 확인
		We should make a code for the validation of downloaded logs
	'''


def upload(password, interval=1):
	global upload_interval
	upload_interval = interval
	schedule.every(interval).seconds.do(uploading, password)
	while True:
		schedule.run_pending()

def uploading(password):
	global index
	upload_lock.acquire()
	logs = ps.save_log()
	myhash = w.encandup(password, logs)
	if myhash is False:
		while True:
			print('[Warning] IPFS daemon died!')
	t = threading.Thread(target=ul.sendLog,args=(myhash,))
	t.start()
	ul.sendLog(myhash)
	index += 1
	upload_lock.release()


def uploadthis(password, logs):
	st = ''.join(logs)
	upload_lock.acquire()
	t = threading.Thread(target=ul.warning, args=(st,))
	t.start()
	ul.warning(st)
	upload_lock.release()


class terminal():
	'''
	업로드를 daemon 스레드로 두고 이곳에서 유저의 인풋에 따라 작업을 수행한다.
	하는 일
		- 현재까지 업로드한 log 출력(평문/암호문/ipfs 해시)
		- 암호 변경
		- 유효성 검사
		- 기타 등등
	'''
	def __init__(self, t1):
		self.upload_thread = t1
	
	def main(self):
		global loglists
		while True:
			print("If you want to read the commands, type \"man\".")
			command = input(">")
			if command == "man":
				print("Commands\n")
				print("chpw\t:\tchange password from. (Overhead is too large, so using this command is depreceated.)")
				print("printl\t:\tprint all logs uploaded from here.")
				print("ck\t:\ttest validations of logs uploaded from here.")
				print("quit\t:\tquit this program.")
				print("rm\t:\tremove all data in ipfs")
				print("init\t:\tdelete all data from ipfs, contract.")
			
			elif command == "chpw":
				self.chpw()
				

			elif command == "printl":
				self.printl()

			elif command == "tv":
				self.tv()
			
			elif command == "quit" or command == 'halt' or command == 'exit':
				print("program exited")
				w.ipfs.close()
				exit()
			
			elif command == "rm":
				w.ipfs.rm()

			elif command == "ck":
				self.ck()
			elif command == 'init':
				self.init()
			else:
				print("Wrong command!")
	
	def init(self):
		w.ipfs.rm()
		ul.contract.functions.init().call()
		exit()

	def chpw(self): 
		# 업로드 스레드인 t1을 이 과정에서 멈추고 끝나면 resume 시켜야 함
		pw = inputpassword()
		if pw is False:
			return
		new_password = input("new password:")
		w.changepassword(pw, new_password)
	
	def printl(self):
		hashlists=[]
		loglists=[]
		n = ul.getN()
		pw = inputpassword() 
		if pw is False:
			return
		for i in range(0,n):
			hashlists.append(ul.getLogs(i))
		for l in hashlists:
			try:
				print("		DEBUG)try download and decrypt ", l)
				loglists.append(w.downanddec(password=pw, h=l))
			except ct.DecryptionError:
				print('Decryption Fail. It caused by old password, or attacked by malicous user')
				continue

		print(loglists)
	
	def ck(self):
		print('ck start!')
		upload_lock.acquire()
		print('acquire done')
		if check() is False:
			print("Validation Check Fail : Log may be modified")
		else:
			print("Validation Check Sucess")
		upload_lock.release()

def main():
	setproctitle.setproctitle(my_random_string(6))
	'''
	sudo python3 main.py 로 실행하면 안되고 sudo 권한이 있는 쉘에서 바로 python3 main.py 실행시켜야 됨
	ps -ef 명령어로 확인 가능
	'''

	password = input("input password: ")
	interval = int(input("input interval time for uploading logs (0 is default - 1sec): "))
	global w
	overwatcht = threading.Thread(target=md.handler)
	overwatcht.start()
	w = ct.wrapper(password)
	t1 = threading.Thread(target=upload, args=(password, interval))
	t1.daemon = True
	t1.start()	# make and run a thread for uploading files valid on IPFS	
		
	'''
		We need to add 
			1. an operation for changing password
				: w.changepassword(password, new_password). 모든 파일을 다운 받아서 복호화하고 다시 새로운 비밀번호로 키를 만들어서 하나의 암호문으로 암호화해 ipfs에 업로드하고 해시를 반환합니다.
				salt도 새로 발급받습니다.
				이 때 기존의 ipfs에 올라간 모든 파일은 삭제됩니다.
				부하가 굉장히 큰 작업이니 사용자들이 자주 하지 않는다는 시나리오로 진행했으면 좋겠습니다
			2. an operation for checking validation of uploaded files
	'''
	
	shell = terminal(t1)
	shell.main()

if __name__ == "__main__":
    main()
