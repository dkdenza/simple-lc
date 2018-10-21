from multiprocessing import Manager, Process
import time, traceback, os, sys, tempfile, subprocess

try:
	assert sys.version_info >= (3, 0)
except (KeyboardInterrupt, EOFError):
	print()
	os._exit(1)
except AssertionError:
	print("This script only working with Python 3")
	os._exit(1)

try:
	import requests
except (KeyboardInterrupt, EOFError):
	print()
	os._exit(1)
except:
	print("Module named 'requests' is required")
	os._exit(1)

doVerifyToken = True
doPrintBanner = True
token_list = []
examplePost = "100002256748316_1907790582639481"

def printUp(text=None):
	print("\033[1A\033[K%s" % (text))

def verifyToken():
	global token_list

	def reqProcess(token, return_dict):
		try:
			resp = requests.get("https://graph.facebook.com/me", params={"access_token": token})
			if resp.status_code == 200:
				return_dict[resp.json()["id"]] = token
			return_dict["Processing"] += 1
			printUp("Updating token list... %s%%" % (str(int(round((return_dict["Processing"] / lenUnc) * 100)))))
		except KeyError:
			pass
		except:
			traceback.print_exc()

	unchecked_tokens = [token.strip() for token in open("token_list.txt", "r", encoding="utf-8").read().split("\n") if token != ""]
	lenUnc = len(unchecked_tokens)
	print("Loaded %s token(s)" % (lenUnc))

	manager = Manager()
	return_dict = manager.dict()
	return_dict["Processing"] = 0
	print("Updating token list... 0%")
	for token in unchecked_tokens:
		process = Process(target=reqProcess, args=(token, return_dict,))
		process.daemon = True
		process.start()
		time.sleep(0.05)

	try:
		process.join()
		return_dict.pop("Processing", None)
		token_list = return_dict.values()
		tokenData = ""
		for token in token_list:
			tokenData += "%s\n" % (token)
		tokenData = tokenData[:-1]
		open("token_list.txt", "w", encoding="utf-8").write(tokenData)
		printUp("Updating token list... Done")
		if not token_list:
			print("[Warning] Token list is empty")
		print("There's %s valid token(s) in the list" % (len(token_list)))
	except (KeyboardInterrupt, EOFError):
		raise
	except:
		printUp("Updating token list... Done")
		print("[Warning] Token list is empty")

def main_menu():
	global doPrintBanner
	if doPrintBanner:
		print("""simple-lc (Simple Like & Comment) by Noxturnix
Source code available at https://github.com/Noxturnix/simple-lc""")
		print()
		doPrintBanner = False

	print("""Actions:
1. Like
2. Comment
3. Verify token list

0. Exit
""")

	while True:
		try:
			user_option = int(input("Choose an action [0-3]: "))
			if user_option in range(0, 3 + 1):
				break
		except (KeyboardInterrupt, EOFError):
			raise
		except:
			pass

	return user_option

def like_menu():
	print("""Like types:
1. NONE
2. LIKE
3. LOVE
4. WOW
5. HAHA
6. SAD
7. ANGRY

0. Go back to main menu
""")

	while True:
		try:
			like_option = int(input("Choose a like type [0-7]: "))
			if like_option in range(0, 7 + 1):
				break
		except (KeyboardInterrupt, EOFError):
			raise
		except:
			pass

	return like_option

def like(post_id, like_option):
	"""
	Parameters:
	- post_id (str)
	- like_option (int)
	"""

	global token_list

	action_count = 0
	try:
		if like_option == 1:
			like_type = "NONE"
		elif like_option == 2:
			like_type = "LIKE"
		elif like_option == 3:
			like_type = "LOVE"
		elif like_option == 4:
			like_type = "WOW"
		elif like_option == 5:
			like_type = "HAHA"
		elif like_option == 6:
			like_type = "SAD"
		elif like_option == 7:
			like_type = "ANGRY"

		for token in token_list:
			resp = requests.post("https://graph.facebook.com/%s/reactions" % (post_id), headers={"Authorization": "Bearer %s" % (token)}, data={"type": like_type})
			if resp.status_code != 200:
				print("[Error] %s" % (resp.json()["error"]["message"]))
			else:
				action_count += 1
				print("[Count: %s] Action performed" % (action_count))
	except (KeyboardInterrupt, EOFError):
		print()
		print("Cancelled")
	except:
		traceback.print_exc()

	print("[Summery] %s like(s) added" % (action_count))

def comment_input():
	temp_file = tempfile.NamedTemporaryFile("w")
	open(temp_file.name, "a", encoding="utf-8").write("""# Type your comment below.
# When finished, press Ctrl + X, press 'y', and hit enter.

""")
	subprocess.call(["nano", "+4", temp_file.name, "-L"])
	print("Opening nano...")
	comment_message = open(temp_file.name, "r", encoding="utf-8").read()
	temp_file.close()

	comment_message = comment_message.split("\n")
	for _ in range(2):
		if comment_message[0].startswith("#"):
			comment_message = comment_message[1:]
	if comment_message[0] == "":
		comment_message = comment_message[1:]
	if comment_message[-1] == "":
		comment_message = comment_message[:-1]
	comment_message = "\n".join(comment_message)
	
	return comment_message

def comment(post_id, comment_message):
	"""
	Parameters:
	- post_id (str)
	- comment_message (str)
	"""

	global token_list

	action_count = 0
	try:
		for token in token_list:
			resp = requests.post("https://graph.facebook.com/%s/comments" % (post_id), headers={"Authorization": "Bearer %s" % (token)}, data={"message": comment_message})
			if resp.status_code != 200:
				print("[Error] %s" % (resp.json()["error"]["message"]))
			else:
				action_count += 1
				print("[Count: %s] Action performed" % (action_count))
	except (KeyboardInterrupt, EOFError):
		print()
		print("Cancelled")
	except:
		traceback.print_exc()

	print("[Summery] %s comment(s) added" % (action_count))	

try:
	while True:
		if doVerifyToken:
			verifyToken()
			doVerifyToken = False
		print()
		user_option = main_menu()
		print()
		if user_option == 0:
			print("Source code available at https://github.com/Noxturnix/simple-lc")
			os._exit(0)
		elif user_option == 1:
			like_option = like_menu()
			if not like_option:
				continue
			post_id = input("Post ID [%s]: " % (examplePost)) or examplePost
			print()
			like(post_id, like_option)
		elif user_option == 2:
			comment_message = comment_input()
			post_id = input("Post ID [%s]: " % (examplePost)) or examplePost
			print()
			comment(post_id, comment_message)
		elif user_option == 3:
			doVerifyToken = True

except (KeyboardInterrupt, EOFError):
	print()
except:
	traceback.print_exc()
