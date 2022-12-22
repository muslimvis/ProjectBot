# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import re
import telebot
import config
import dbworker



opts = webdriver.ChromeOptions()
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')

bot = telebot.TeleBot(config.token)
driver = webdriver.Chrome(options=opts)
driver.maximize_window()

def enter_car(my_car):
    search_field = driver.find_element('xpath',
        '//*[@id="app"]/div/div/header/div[1]/div/div[3]/div/label')
    search_field.click()

    search_field.send_keys(my_car)
    sleep(1.5)
    search_field.send_keys(Keys.RETURN)


def get_model_list():
    sleep(1.5)
    page_text = driver.page_source.encode('utf-8')
    bs_text = BeautifulSoup(page_text, 'html.parser')
    x = bs_text.find_all('a', {'class': 'Link ListingPopularMMM__itemName'})
    if len(x) == 11 or len(x) == 7:
        try:

            model = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[4]/div/div[4]/span')))

            model.click()

            page_text = driver.page_source.encode('utf-8')
            bs_text = BeautifulSoup(page_text, 'html.parser')

            x = bs_text.find_all('a', {'class': 'Link ListingPopularMMM__itemName'})

            available_models = [i.text.strip() for i in x]
        except:
            available_models = [i.text.strip() for i in x]
    else:
        available_models = [i.text.strip() for i in x]

    return available_models


def get_generation_dict_list():
    generation_field = driver.find_element('xpath',
        '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div/div[3]/div[1]/button/span/span')

    generation_field.click()
    sleep(1.5)

    page_text = driver.page_source.encode('utf-8')
    bs_text = BeautifulSoup(page_text, 'html.parser')
    years = [i.text.strip() for i in bs_text.find_all('div', {'class': 'PopupGenerationItem__years'})]
    names = [i.text.strip() for i in bs_text.find_all('div', {'class': 'PopupGenerationItem__name'})]
    generation_zip = zip(years, names)
    generation_list = list((i[0] + ' ' + i[1]) for i in generation_zip)
    return generation_list


def enter_year(year):
    pattern = re.compile(r'^\d{4}$')
    pattern_range = re.compile(r'^\d{4}-\d{4}$')

    if pattern.match(year) and '1870' <= year <= '2023':
        url = driver.current_url[:-13] + year + '-year/' + driver.current_url[-13:]
    elif pattern_range.match(year) and ('1870' <= year[:4] <= '2023') and ('1870' <= year[5:] <= '2023') and (
            year[:4] < year[5:]):
        url = driver.current_url + '?year_from=' + year[:4] + '&year_to=' + year[5:]
    else:
        raise

    return url


def get_average_price(url):
    driver.get(url)
    page_text = driver.page_source.encode('utf-8')
    bs_text = BeautifulSoup(page_text, 'html.parser')

    find_pages = bs_text.find_all('a', {'class': 'Button Button_color_whiteHoverBlue Button_size_s \
Button_type_link Button_width_default ListingPagination__page'})

    find_prices = bs_text.find_all('div', {'class': 'ListingItemPrice__content'})

    price_list = [''.join(i.text.strip()[:-2].split('\xa0')) for i in find_prices]

    if len(find_pages) != 0:
        next_page = driver.find_element('xpath','/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[7]/div/div/a[2]/span/span')

        for i in range(int(find_pages[-1].text.strip()) - 1):
            next_page.click()
            sleep(2)

            page_text = driver.page_source.encode('utf-8')
            bs_text = BeautifulSoup(page_text, 'html.parser')

            find_prices = bs_text.find_all('div', {'class': 'ListingItemPrice__content'})
            price_list += [''.join(i.text.strip()[:-2].split('\xa0')) for i in find_prices]


            if i != range(int(find_pages[-1].text.strip()) - 1)[-1]:
                sleep(1.5)


    price_list_int = [int(i) for i in price_list]
    average_price = sum(price_list_int) / len(price_list_int)

    return average_price, len(price_list_int)


@bot.message_handler(commands=['info'])
def cmd_info(message):
    bot.send_message(message.chat.id, 'Some reading as promised! \n'
                                      'I can tell ya the average price of\n'
                                      'a car among ads listed on auto.ru\n'
                                      'based on 3 parameters.')
    bot.send_message(message.chat.id, 'First you choose a car itself.\n'
                                      'Then pick model and generation.\n'
                                      'Finally enter requested parameters:\n'
                                      'Production year, power and mileage in km.')
    bot.send_message(message.chat.id, 'Enter year in format YYYY for\n'
                                      'a specific year or\n'
                                      'YYYY-YYYY for range of years.\n'
                                      '\n'
                                      'Enter power in format \n'
                                      'POWER FROM-POWER TO\n'
                                      'POWER FROM must be > 0\n'
                                      'but can be equal to POWER TO\n'
                                      '\n'
                                      'Enter mileage in km. in format\n'
                                      'MILEAGE FROM-MILEAGE TO\n'
                                      'Enough reading i  guess :)')


@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id,
                     "/reset - to discard previous selections and start all over.\n"
                     "/start - to start a new dialogue from the very beginning.\n"
                     "/info - to do some reading.\n"
                     "/commands - you know what it is used for.\n")



@bot.message_handler(commands=['reset'])
def cmd_reset(message):
    dbworker.set_state_j(message.chat.id, config.States.S_START.value)
    markup = telebot.types.ReplyKeyboardMarkup(True, True)
    markup.keyboard = [['/enter_car', '/info']]
    bot.send_message(message.chat.id, 'Ah shit, here we go again.\n'
                                      'Use /enter_car to choose a car. \n'
                                      'Use /info to do some reading.', reply_markup=markup)


@bot.message_handler(commands=['start'])
def cmd_start(message):
    dbworker.set_state_j(message.chat.id, config.States.S_START.value)
    markup = telebot.types.ReplyKeyboardMarkup(True, True)
    markup.keyboard = [['/enter_car', '/info']]
    bot.send_message(message.chat.id, 'Wazzup, my freind! I\'m Autobot.\n'
                                      'I can find an average price of a car\n'
                                      'among listed ads on auto.ru based\n'
                                      'on three parameters!\n'
                                      '/info to do some reading.\n'
                                      '/reset to start all over.\n'
                                      '/commands to see commands.\n'
                                      '/enter_car to start a search.', reply_markup=markup)





@bot.message_handler(func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_START.value)
                     and message.text.strip().lower() != '/enter_car')
def answers(message):
    bot.send_message(message.chat.id, 'I\'m quite stupid, so please\n'
                                      'either click/type /enter_car\n'
                                      'or don\'t make me feel dumb\n'
                                      'Thank you, mate!')



@bot.message_handler(func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_START.value)
                                           and message.text.strip().lower() == '/enter_car')
def after_start(message):
    bot.send_message(message.chat.id, 'Wait a sec...')

    driver.get('https://auto.ru')

    fld = driver.find_element('xpath',
        '/html/body/div[2]/div/div/div[3]/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/div/div[6]/div')

    fld.click()
    page_text = driver.page_source.encode('utf-8')
    bs_text = BeautifulSoup(page_text, 'html.parser')

    x = bs_text.find_all('div', {'class': 'IndexMarks__marks-with-counts'})[0].find_all(
        'div', {'class': 'IndexMarks__item-name'})

    list_of_available_cars = [i.text.strip() for i in x]
    dbworker.set_json_data('list_of_cars', list_of_available_cars)

    markup = telebot.types.ReplyKeyboardMarkup(True, True)
    markup.keyboard = [list_of_available_cars[i:i + 3] for i in range(0, len(list_of_available_cars), 3)]
    bot.send_message(message.chat.id, 'Here is the list of available cars. \n'
                                      'Go ahead and choose one.', reply_markup=markup)
    dbworker.set_state_j(message.chat.id, config.States.S_ENTER_CAR.value)


@bot.message_handler(
    func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_CAR.value))
def get_car(message):
    if message.text.lower().strip() in [i.lower().strip() for i in dbworker.get_json_data('list_of_cars')]:

        bot.send_message(message.chat.id, 'I\'m doing my best...')
        enter_car(message.text.lower().strip())

        available_models = get_model_list()    # получил список моделей

        dbworker.set_json_data('list_of_available_models', available_models)

        markup = telebot.types.ReplyKeyboardMarkup(True, True)
        markup.keyboard = [available_models[i:i + 4] for i in range(0, len(available_models), 4)]
        bot.send_message(message.chat.id, 'Now its time to choose model. \n'
                                          'Feel free to pick one.', reply_markup=markup)
        dbworker.set_state_j(message.chat.id, config.States.S_ENTER_MODEL.value)

    else:
        bot.send_message(message.chat.id, 'Dude, just choose from the list.')



@bot.message_handler(
    func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_MODEL.value))
def get_model(message):
    if message.text.lower().strip() in [i.lower().strip() for i in dbworker.get_json_data('list_of_available_models')]:
        bot.send_message(message.chat.id, 'I\'m doing my best...')

        page_text = driver.page_source.encode('utf-8')
        bs_text = BeautifulSoup(page_text, 'html.parser')

        x = bs_text.find_all('a', {'class': 'Link ListingPopularMMM__itemName'})
        model_link = [i.get('href') for i in x if i.text.strip().lower() == message.text.lower().strip()]
        driver.get(model_link[0])

        available_generations_list = get_generation_dict_list()

        dbworker.set_json_data('list_of_generations', available_generations_list)


        markup = telebot.types.ReplyKeyboardMarkup(True, True)
        markup.keyboard = [available_generations_list[i:i + 2] for i in range(0, len(available_generations_list), 2)]
        bot.send_message(message.chat.id, 'Time to choose generation. \n', reply_markup=markup)
        dbworker.set_state_j(message.chat.id, config.States.S_ENTER_GENERATION.value)
    else:
        bot.send_message(message.chat.id, 'Dude, just choose one from the list.')


@bot.message_handler(
    func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_GENERATION.value))
def get_generation(message):
    if message.text.strip() in [i.strip() for i in dbworker.get_json_data('list_of_generations')]:
        lst = [i.strip() for i in dbworker.get_json_data('list_of_generations')]

        if len(lst) > 1:
            try:
                choose_generation = driver.find_element('xpath',"/html/body/div[3]/div/div/div[2]/div[2]/div[{}]/label/span[1]/input".format(lst.index(message.text.strip()) + 1))

                choose_generation.click()
                sleep(1.5)
                all_parameters = driver.find_element('xpath',
                    '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/span')
                all_parameters.click()
            except:
                choose_generation = driver.find_element('xpath',"/html/body/div[4]/div/div/div[2]/div[2]/div[{}]/label/span[1]/input".format(lst.index(message.text.strip()) + 1))

                choose_generation.click()
                sleep(1.5)
                all_parameters = driver.find_element('xpath',
                    '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/span')
                all_parameters.click()


        else:

            try:
                choose_generation = driver.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/label/span[1]/input')
                choose_generation.click()
                sleep(1.5)
                all_parameters = driver.find_element('xpath',
                    '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/span')
                all_parameters.click()
            except:
                choose_generation = driver.find_element('xpath','/html/body/div[3]/div/div/div[2]/div[2]/div/label/span[1]/input')
                choose_generation.click()
                sleep(1.5)
                all_parameters = driver.find_element('xpath',
                    '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/span')
                all_parameters.click()

        bot.send_message(message.chat.id, 'Enter year\n'
                                          'in format YYYY for a specific year\n'
                                          'or YYYY-YYYY for range of years.')

        dbworker.set_state_j(message.chat.id, config.States.S_ENTER_YEAR.value)
    else:
        bot.send_message(message.chat.id, 'Dude, just choose one from the list.')


@bot.message_handler(
    func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_YEAR.value))
def get_year(message):
    try:
        dbworker.set_json_data('current_url', enter_year(message.text.strip()))
        bot.send_message(message.chat.id, 'Enter power in format\n'
                                          'POWER FROM-POWER TO\n'
                                          'POWER FROM must be > 0\n'
                                          'but can be equal to POWER TO\n')
        dbworker.set_state_j(message.chat.id, config.States.S_ENTER_POWER.value)
    except:
        bot.send_message(message.chat.id, 'You got it wrong!\n'
                                          'YYYY for a specific year\n'
                                          'YYYY-YYYY for range of years.')


@bot.message_handler(func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_POWER.value))
def get_power(message):
    pattern = re.compile(r'^[1-9]\d*-[1-9]\d*$')
    if pattern.match(message.text.strip()):
        power_from = re.findall(r'\d+', message.text.strip())[0]
        power_to = re.findall(r'\d+', message.text.strip())[1]

        if int(power_from) <= int(power_to):
            url = dbworker.get_json_data('current_url')
            x = re.compile(r'\d{4}')

            if x.match(url[-4:]):
                url += ('&power_from=' + power_from + '&power_to=' + power_to)
                dbworker.set_json_data('current_url', url)
            elif url.endswith('all/'):
                url += ('?power_from=' + power_from + '&power_to=' + power_to)
                dbworker.set_json_data('current_url', url)

            bot.send_message(message.chat.id, 'Enter mileage in km. in format\n'
                                              'MILEAGE FROM-MILEAGE TO\n')
            dbworker.set_state_j(message.chat.id, config.States.S_ENTER_KM.value)
        else:
            bot.send_message(message.chat.id, 'You got it wrong! Format is\n'
                                              'POWER FROM-POWER TO\n'
                                              'POWER FROM must be > 0\n'
                                              'but can be equal to POWER TO\n')

    else:
        bot.send_message(message.chat.id, 'You got it wrong! Format is\n'
                                          'POWER FROM-POWER TO\n'
                                          'POWER FROM must be > 0\n'
                                          'but can be equal to POWER TO\n')


@bot.message_handler(func=lambda message: (dbworker.get_current_state_j(str(message.chat.id)) == config.States.S_ENTER_KM.value))
def get_km(message):
    pattern_range = re.compile(r'^\d+-[1-9]\d*$')
    url = dbworker.get_json_data('current_url')
    state = True

    if pattern_range.match(message.text.strip()) and int(re.findall(r'\d+', message.text.strip())[0]) <= int(re.findall(r'\d+', message.text.strip())[1]):
        if re.findall(r'\d', message.text.strip())[0] == 0:
            url += ('&km_age_to=' + message.text.strip())
            dbworker.set_json_data('current_url', url)
            state = False
        else:
            km_from = re.findall(r'\d+', message.text.strip())[0]
            km_to = re.findall(r'\d+', message.text.strip())[1]

            url += ('&km_age_from=' + km_from + '&km_age_to=' + km_to + '&with_discount=false')
            dbworker.set_json_data('current_url', url)
            state = False
    else:
        bot.send_message(message.chat.id, 'Something is wrong! Use format\n'
                                          'MILEAGE FROM-MILEAGE TO\n')

    if state == False:
        try:
            bot.send_message(message.chat.id, 'I\'m gathering info.\n'
                                              'It might take a while...')
            average_price, num_of_ads = get_average_price(dbworker.get_json_data('current_url'))

            bot.send_message(message.chat.id, f'I found {num_of_ads} ad(s) with such parameters\n'
                                              f'Average price is: {average_price:,.0f}')
            markup = telebot.types.ReplyKeyboardMarkup(True, True)
            markup.keyboard = [['/enter_car', '/info']]
            bot.send_message(message.chat.id, '/enter_car to start another search.', reply_markup=markup)
            dbworker.set_state_j(message.chat.id, config.States.S_START.value)

        except:
            markup = telebot.types.ReplyKeyboardMarkup(True, True)
            markup.keyboard = [['/enter_car', '/info']]
            bot.send_message(message.chat.id, 'I\'m sorry, no ads listed\n'
                                              'with such parameters.\n'
                                              'Try something else!', reply_markup=markup)
            dbworker.set_state_j(message.chat.id, config.States.S_START.value)
    else:
        pass



if __name__ == '__main__':
    bot.infinity_polling()


