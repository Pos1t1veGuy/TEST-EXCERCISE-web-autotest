from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.remote.webelement import WebElement

import string
import random as r
import requests
import pytest
from typing import *


@pytest.fixture(scope="module")
def driver():
	options = Options()
	#options.add_argument("--headless")
	driver = webdriver.Firefox(options=options)
	yield driver
	#driver.quit()

def get_ddgo_results(driver: webdriver.Firefox, question: str, data_layout: str = 'organic') -> List[WebElement]:
	# data_laoyout=organic - это обычные результаты, может быть еще data_laoyout=videos
	url = 'https://duckduckgo.com/'
	driver.get(url)

	'''
	<input aria-autocomplete="both" aria-controls="listbox--11" aria-expanded="true"
	aria-haspopup="listbox" aria-label="Search with DuckDuckGo" role="combobox"
	class="searchbox_input__bEGm3" type="text" name="q" autocomplete="off" id="searchbox_input"
	autocapitalize="none" autocorrect="off" placeholder="Поиск без отслеживания" required=""
	minlength="1" data-reach-combobox-input="" data-state="suggesting" value="">
	'''
	inp = driver.find_element(By.ID, "searchbox_input")
	'''
	<button aria-label="Search" class="iconButton_button__6x_9C searchbox_searchButton__F5Bwq" type="submit"></button>
	'''
	search_button = driver.find_element(By.XPATH, '//button[@aria-label="Search"]')

	inp.send_keys(question)
	search_button.click() # Ввод запроса и поиск ответов

	# Ждем подгрузки результатов <ol class="react-results--main"></ol>
	results = WebDriverWait(driver, 15).until(
		EC.presence_of_element_located((By.CLASS_NAME, "react-results--main"))
	)

	# <li data-layout="organic" class="wLL07_0Xnd1QZpzpfR4W"></li>: data-layout может быть либо videos, либо organic.
	return results.find_elements(By.XPATH, f'//li[@data-layout="{data_layout}"]')


# pytest test_ddgo.py автоматически обнаружит все "test_" функции, сценарии тестирования. Иначе pytest -v text_ddgo.py::test_ddgo_...

def test_ddgo_titles(driver):
	question = r.choices(string.digits, k=r.randint(3, 5))
	results = get_ddgo_results(driver, question)
	
	slice_in = 3 # "Проверим" первые 3 результата в результате гуглежа
	for result in results[:slice_in]:
		# Проверка заголовка
		title = result.find_element(By.XPATH, '//h2/a/span')
		assert len(title.text) > 3, f'Почему тут тайтл такой короткий "{title.text}"? Меня это смущает'

def test_ddgo_images(driver):
	question = r.choices(string.digits, k=r.randint(3, 5)) # Иногда попадаются пустые иконки и ругаться начинает на них, и правильно делает
	results = get_ddgo_results(driver, question)
	
	slice_in = 3 # "Проверим" первые 3 результата в результате гуглежа
	for result in results[:slice_in]:
		# Проверка иконки
		img = result.find_element(By.XPATH, '//span/a/div/img')
		img_url = img.get_attribute('src')
		response = requests.get(img_url)
		assert response.status_code == 200, f"Иконка {img_url} не загрузилась корректно =("