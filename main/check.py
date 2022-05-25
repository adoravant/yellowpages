import sys, time
from datetime import date, datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from io import BytesIO
import win32clipboard
from PIL import Image
import os

today = date.today().strftime('%d/%m/%Y')
current_time = datetime.now().strftime("%H:%M:%S")

msgDate = 'TIME'
msgTime = 'DATE'
filepath = 'perro.jpg'
image = Image.open(filepath)
output = BytesIO()
image.convert("RGB").save(output, "BMP")
data = output.getvalue()[14:]
output.close()
check = True


def send_to_clipboard(clip_type, data):
	win32clipboard.OpenClipboard()
	win32clipboard.EmptyClipboard()
	win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
	win32clipboard.CloseClipboard()
msg = "chequea asjkdhasjkdhjka shjkdahsjkdhjk hasdhk jashd kjhasjkdhjaksdhajkhdkjsjkhkjah kjhkahdskjahdkjhaskj hakjshdjkashdkjahkjashdkj hakhdkjh https://google.com"
send_to_clipboard(win32clipboard.CF_DIB, data)

def new_chat(user):
	new_chat = chrome_browser.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')
	
	new_chat.send_keys(user.name)
	time.sleep(2)
	
	try:
		username = chrome_browser.find_element(By.XPATH, '//span[@title="{}"]'.format(user.name))
		if check == True:
			user.phone_type = "WHATSAPP"
			user.save()
		username.click()
		
	except NoSuchElementException as se:
		print('Username not in contact list')
		close_search = chrome_browser.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/span/button')
		close_search.click()

	# except Exception as e:
	#     chrome_browser.close()
	#     print(e)
	#     sys.exit()

	
	
if __name__ == '__main__':
	
	while True:
		# if msgDate == today:
		#     current_time = datetime.now().strftime("%H:%M:%S")
		#     if current_time >= msgTime:
		options = webdriver.ChromeOptions()
		options.add_argument(r'--user-data-dir=C:\\Users\\pc\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
		options.add_argument('--profile-directory=Default')
		chrome_browser = webdriver.Chrome('C:\\Users\\pc\\Desktop\\chromedriver.exe', options=options)
		chrome_browser.get('https://web.whatsapp.com/')
		#SCAN QR CODE
		time.sleep(10)
		
		user_list = Dato.objects.all()

		for user in user_list:
			try:
				user = chrome_browser.find_element(By.XPATH, '//span[@title="{}"]'.format(user.name))
				user.click()
			except NoSuchElementException as se:
				new_chat(user)
				time.sleep(1)
			if check == False:
				try:        
					time.sleep(2)
					message_box = chrome_browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]')
					time.sleep(2)
					#PEGAR FOTO SI ES CON FOTO
					message_box.send_keys(Keys.CONTROL, 'v')
					time.sleep(1)
					message_box = chrome_browser.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[2]')
					message_box.send_keys(msg)
					send_button = chrome_browser.find_element(By.XPATH,  '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div')
					send_button.click()
					time.sleep(0.5)
					#ELIMINAR CONVERSACION
					more_button = chrome_browser.find_element(By.XPATH, '//*[@id="main"]/header/div[3]/div/div[2]/div/div')
					more_button.click()
					delete_chat_button = chrome_browser.find_element(By.XPATH, '//*[@id="app"]/div/span[4]/div/ul/div/div/li[6]/div[1]')
					time.sleep(0.7)
					delete_chat_button.click()
					time.sleep(0.7)
					confirm_delete_button = chrome_browser.find_element(By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[3]/div/div[2]')
					confirm_delete_button.click()
					confirm_delete_button.click()   
					time.sleep(2)
				except:
					continue
		break
	
   