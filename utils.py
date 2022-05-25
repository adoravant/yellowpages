import os
import django
import sys
sys.path.append("C:\\Users\\pc\\Desktop\\PYTHON")
print("syspath", sys.path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soup.settings')
django.setup()

from django.conf import settings
from django.db import IntegrityError
import time
from datetime import date, datetime
from main.models import Lead, Dato

#AUTOMATION
import requests
requests.adapters.DEFAULT_RETRIES = 2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#CLIPBOARD
from io import BytesIO
import win32clipboard
from PIL import Image


today = date.today().strftime('%d/%m/%Y')
current_time = datetime.now().strftime("%H:%M:%S")

msgDate = 'TIME'
msgTime = 'DATE'
filepath = 'main/perro.jpg'
image = Image.open(filepath)
output = BytesIO()
image.convert("RGB").save(output, "BMP")
data = output.getvalue()[14:]
output.close()


def send_to_clipboard(clip_type, data):
	win32clipboard.OpenClipboard()
	win32clipboard.EmptyClipboard()
	win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
	win32clipboard.CloseClipboard()
msg = "chequea asjkdhasjkdhjka shjkdahsjkdhjk hasdhk jashd kjhasjkdhjaksdhajkhdkjsjkhkjah kjhkahdskjahdkjhaskj hakjshdjkashdkjahkjashdkj hakhdkjh https://google.com"
send_to_clipboard(win32clipboard.CF_DIB, data)



Ontario = {"ON" :["Toronto", "Ottawa", "Mississauga", "Brampton", 
				 "Hamilton", "London", "Markham", 
				 "Vaughan", "Kitchener", "Windsor"]}

Quebec = {"QC" :["Bas-Saint-Laurent", "Saguenay–Lac-Saint-Jean", 
			"Capitale-Nationale", "Mauricie", "Estrie", 
			"Montréal", "Outaouais", "Abitibi-Témiscamingue", "Côte-Nord", "Nord-du-Québec", "Gaspésie–Îles-de-la-Madeleine",
			"Chaudire-Appalaches", "Laval", "Lanaudière", "Laurentides", "Montérégie", "Centre-du-Québec"]}

Nova_Scotia =  {"NS" :["Halifax", "Sydney", "Kentville", "Truro", "Liverpool", "Shelburne", "Yarmouth"]}

New_Brunswick = {"NB" :["Albert County", "Carleton County", "Charlotte County", "Gloucester County", 
				"Kent County", "Kings County", "Madawaska County", "Northumberland County", "Queens County", "Restigouche County", 
				"Saint John County", "Sunbury County", "Victoria County", "Westmorland County", "Westmorland County"]}

Manitoba = {"MB" :["Pembina Valley", "Winnipeg", "Westman Region", "Parkland", "Eastman", "Central Plains", "Westman", "Northern"]}

British_Columbia = {"BC" :["Prince Rupert", "Tofino", "Nanaimo", "Victoria", "Vancouver", "Chilliwack", 
					"Penticton", "Kamloops", "Osoyoos", "Princeton", "Cranbrook", "Prince George", "Fort Nelson"]}
Princ_Edward_Island = {"PE" :["Charlottetown", "Summerside", "Stratford", 
						"Cornwall", "Montague", "Kensington", "Souris", "Alberton",
						"Tignish", "Georgetown"]}
Saskatchewan = {"SK" :["Maple Creek", "Estevan", "Weyburn", "Moose Jaw", "Regina", "Saskatoon", "Melville", 
				"Swift Current", "Humboldt", "Melfort", "North Battleford", "Yorkton", "Lloydminster", "Prince Albert"]}
Alberta = {"AB" :["Calgary", "Edmonton", "Red Deer", "Lethbridge", "St. Albert ", "Medicine Hat", "Grande Prairie", "Airdrie", "Spruce Grove", 
				  "Leduc", "Strathcona County", "Regional Municipality of Wood Buffalo", "Rocky View County", "Parkland County", "Municipal District of Foothills No. 31"
			]}
Newfoundland_and_Labrador = {"NL" :["St. John's", "Conception Bay South", "Mount Pearl", "Paradise", "Corner Brook", 
							"Grand Falls-Windsor", "Gander", "Portugal Cove-St. Philip's", "Happy Valley-Goose Bay", 
	
]}




def get_citylist():
	citylist = [Ontario, Quebec, Nova_Scotia, New_Brunswick, Manitoba, 
				British_Columbia, Princ_Edward_Island, Saskatchewan, Alberta, Newfoundland_and_Labrador]
	
	return citylist


#START WHATSAPP
def new_chat(user, chrome_browser, check):
	new_chat = chrome_browser.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')
	
	new_chat.send_keys(user.phone)
	time.sleep(2)
	
	try:
		username = chrome_browser.find_element(By.XPATH, '//span[@title="{}"]'.format(user.phone))
		if check == True:
			user.phone_type = "WHATSAPP"
			user.save()
		else:
			username.click()
		
	except NoSuchElementException as se:
		user.phone_type = "REGULAR"
		user.save()
		print(f'{user.phone} not in whatsapp')
	close_search = chrome_browser.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/span/button')
	close_search.click()

	# except Exception as e:
	#     chrome_browser.close()
	#     print(e)
	#     sys.exit()


def run_whatsapp(check=True):   
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
		time.sleep(40)
		
		if check == True:
			user_list = Dato.objects.all().filter(phone_type="WHATSAPP")
			# user_list = Dato.objects.all().exclude(phone_type="WHATSAPP").exclude(phone_type="REGULAR")
		else:
			user_list = Dato.objects.filter(name__in=["Oscar Oso", "Ivet"])
			#user_list = Dato.objects.filter(phone_type="WHATSAPP") 
		
		for user in user_list:
			try:
				user = chrome_browser.find_element(By.XPATH, '//span[@title="{}"]'.format(user.name))
				user.click()
			except NoSuchElementException as se:
				new_chat(user, chrome_browser, check)
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
					more_button = chrome_browser.find_element(By.XPATH, '//*[@id="main"]/header/div[3]/div/div[2]/div/div')
					more_button.click()
					delete_chat_button = chrome_browser.find_element(By.XPATH, '//*[@id="app"]/div/span[4]/div/ul/div/div/li[6]/div[1]')
					time.sleep(1)                                             
					delete_chat_button.click()
					time.sleep(1)
					confirm_delete_button = chrome_browser.find_element(By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[3]/div/div[2]')
					confirm_delete_button.click()
					confirm_delete_button.click()   
					time.sleep(2)
					time.sleep(2)
				except:
					continue
		break
#END WHATSAPP

#START .CA SCRAPPER
def run_soup(term):
	#itera dict y genera serchlinks
	citylist = get_citylist()
	for city in citylist:
		suffix = ""
		for k in city.keys():
			suffix = k
		
		for value in city.values():
			for v in value:
				city_link = f"{v}+{suffix}" 
				print(city_link)
				x = get_page_info(city_link, term)
				get_results(x)



def website_info(obj=None):
	if obj != None:
		if type(obj) != str:
			website = obj.website
		else:
			website = obj
		try:
			r = requests.get(website)
			x = str(r.status_code)
			if r.url.startswith("https") == False:
				x += "NOSSL"
		except:
			x = "DOWNSSL"
		
		try:
			if (x == "503") and ("Your access to this" in r.text):
				x = "BLOCKED"
		except:
			pass
		return x       
	else:
		websites = Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status__startswith="DOWNSSL")
		#Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status=None)
		#Lead.objects.filter(country="CANADA").filter(search_tag="Lawyer").exclude(website="NOWEB").exclude(website_status=None).exclude(website_type="FACEBOOK").filter(website_status="DOWNSSL")
		for website in websites:
			try:
				r = requests.get(website)
				x = str(r.status_code)
				if r.url.startswith("https") == False:
					x += "NOSSL"
			except:
				x = "DOWNSSL"
			if x == "503":
				try:
					if "Your access to this" in r.text:
						x = "BLOCKED"
				except:
					print("last except what?")

			a.website_status = x
			a.save()
 
def get_page_info(city_link, term):
	#returns total de páginas para una búsqueda"
	phonelist = []
	namelist = []
	

	r = requests.get(f"https://www.yellowpages.ca/search/si/1/{term}/{city_link}")
	html = r.content
	sup = BeautifulSoup(html)
	
	#CANTIDAD DE PAGINAS
	span = sup.find_all('span', {"class" : "pageCount"})
	try: 
		page_total = int(span[0].find_all('span')[1].text)
	except:
		page_total = 1
	
	page_info = page_total, city_link, term
	return page_info



def get_results(page_info, check_website=True):
	#scrapea cada uno de los páginas para un searchlink
	linksplit = page_info[1].split("+")
	city = linksplit[0]
	state = linksplit[1]
	
	
	for a in range(1, (page_info[0] +1)):
		#REDEFINIR URL SI TOTAL DE PAGINAS ES MAYOR A 1
		next_url = f"https://www.yellowpages.ca/search/si/{a}/{page_info[2]}/{page_info[1]}"
		# page_to_scrape = f"https://www.yellowpages.ca/search/si/{a}/Marketing+Consultants+%26+Services/Toronto+ON"
		r = requests.get(next_url)
		html = r.content
		sup = BeautifulSoup(html)
		

		div_listing = sup.find_all('div', {"class" : "listing listing--bottomcta"})
		
		for a in div_listing:
			if check_website == True:
				try:
					website = a.find('li', {"class" : "mlr__item--website"})
					website = [x['href'] for x in website.find_all('a', href=True)]
					website = "https://www.yellowpages.ca" + website[0]
					if "facebook" in website:
						website_type = "FACEBOOK"
						website_status = None
					else:
						website_type = "REGULAR"
						website_status = website_info(website)        
				except:
					website = "NOWEB"
					website_type = None
					website_status = None 
					

			name = a.select_one('h3:first-child').text.replace("\n", "")
			try:
				phone = a.select_one('h4:first-child').text 
				phone = phone.replace("\n", "").replace(" ", "").replace("-", "")
				if phone.startswith("1") == False and phone.startswith("+1") == False:
					phone = "+1" + phone
				elif phone.startswith("1") == True:
					phone = "+" + phone    
			except:
				phone = "undefined"
				print("phone does not exist")
			
			
			try:
				obj, created = Lead.objects.update_or_create(
					phone=phone,
					name=name,
					city=city,
					state=state,
					country="CANADA",
					website = website,
					search_tag = page_info[2],
					website_type=website_type,
					website_status = website_status)

			except IntegrityError:
				print("objeto duplicado", phone)
		print("scrapped", next_url) 
#END .CA SCRAPPER        
		



# START FACEBOOK
def send_message(chrome_browser):
	try:
		msg_button_1 = chrome_browser.find_element_by_css_selector('span.a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7.ltmttdrg.g0qnabr5.ojkyduve')
		print(msg_button_1.text)

		if msg_button_1.text == "Enviar mensaje":
			msg_button_1.click()
			time.sleep(4)
			text_box = chrome_browser.find_element_by_css_selector('div.oo9gr5id.lzcic4wl.l9j0dhe7.gsox5hk5.buofh1pr.tw4czcav.cehpxlet.hpfvmrgz.eg9m0zos.notranslate')
			text_box.send_keys("?asdasdas")
		else:
			print("no tiene boton de enviar mensaje")
	except:
		print("entre except")


def visit_facebook():
	pages = Lead.objects.filter(website_type="FACEBOOK").values_list("website", flat=True)
	options = webdriver.ChromeOptions()
	options.add_argument(r'--user-data-dir=C:\\Users\\pc\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
	options.add_argument('--profile-directory=Default')
	chrome_browser = webdriver.Chrome('C:\\Users\\pc\\Desktop\\chromedriver.exe', options=options)
	for page in pages:
		time.sleep(3)
		chrome_browser.get(page)
		if pages[0] == page:
			try:
				time.sleep(3)
				chrome_browser.find_element(By.XPATH, '//span[text()="Abrahan"]')
			except NoSuchElementException:
				user = chrome_browser.find_element(By.XPATH, '//*[@id="email"]')
				user.send_keys("adoravant@gmail.com")
				password = chrome_browser.find_element(By.XPATH, '//*[@id="pass"]')
				password.send_keys("Dereversa15389!")
				
				time.sleep(1.5)
				login_button = chrome_browser.find_element(By.ID, 'loginbutton')
				login_button.click()
				logged = True
				time.sleep(3)   
		
		send_message(chrome_browser)
#END FACEBOOK


#START GUIA CORES
def guia_cores():
	busquedas = ["INMOBILIARIA"]

	for busqueda in busquedas:
		next_url = f"https://www.guiacores.com.ar/index.php?r=search%2Findex&b={busqueda}&R=&L=&Twa=1&NTw=1"
		r = requests.get(next_url)
		html = r.content
		sup = BeautifulSoup(html)
		div_listing = sup.find_all('div', {"class" : "datos"})
		count= 0
		for div in div_listing:
			nombre_comercio = div.find("span", {"class": "nombre-comercio"}).text
			whatsapp_comercio = div.find("a", {"class": "search-result-link"}).text
			count += 1
			print(count, nombre_comercio, whatsapp_comercio)
			import time


		return div_listing


def guia():
	driver = webdriver.Chrome('C:\\Users\\pc\\Desktop\\chromedriver.exe')
	# busquedas = ["PETRO", "INMO", "ABOGA", "FERRETERIA", "DISTRIBU", "SERVICIO", "MAQUIN", "PROFES"]
	busquedas = ["S.R.L.", "S.A."]
	for busqueda in busquedas:
		next_url = f"https://www.guiacores.com.ar/index.php?r=search%2Findex&b={busqueda}&R=&L=&Twa=1&NTw=1"
		driver.get(next_url)
		time.sleep(5) # Let the user actually see something!
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)
		while True:
			try:
				load_button = driver.find_element_by_xpath('//*[@id="ver-mas"]')
				load_button.click()
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(5)
			except:
				break
		html = driver.page_source        
		sup = BeautifulSoup(html)
		div_listing = sup.find_all('div', {"class" : "datos"})
		count = 0
		for div in div_listing:
			nombre_comercio = div.find("span", {"class": "nombre-comercio"}).text
			whatsapp_comercio = div.find("a", {"class": "search-result-link"}).text
			obj, created = Lead.objects.update_or_create(
				name=nombre_comercio,
				phone=whatsapp_comercio,
				phone_type="WHATSAPP",
				city="NEUQUEN",
				state="NQ",
				country="ARGENTINA")    
			count += 1
			if created:
				print("object created", count, nombre_comercio, whatsapp_comercio, "NEUQUEN")
			else:
				print("object updated", count, nombre_comercio, whatsapp_comercio, "NEUQUEN")
#END GUIA CORES



   
if __name__ == '__main__':
	print("200", Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status="200").count())
	print("200 SSL ISSUE" , Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status="200NOSSL").count())
	print("400", Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status__startswith="4").count())
	print("500", Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status__startswith="5").count())
	print("BLOCKED", Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status__startswith="BLOCKED").count())
	print("DOWN", Lead.objects.filter(country="CANADA").filter(website_type="REGULAR").filter(website_status__startswith="DOWNSSL").count())
	website_info()
