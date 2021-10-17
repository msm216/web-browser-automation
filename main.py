#!/usr/bin/python
#############################################################################################
# 1. Einloggen im Webshop
# 2. Navigieren zum Produkt HP Z3200 WIRELESS MOUSE
# 3. Legen Sie 1 Maus der Farbe Weiß und 2 der Farbe Rot in den Warenkorb.
# 4. Führen Sie den Bezahlprozess bis zum Ende durch.
# 5. Der richtige Preis der beiden roten Mäuse und der Gesamtpreis sollen verifiziert werden.
#############################################################################################

# import os
# import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException


infos = {
    'url': 'http://www.advantageonlineshopping.com/',
    'username': 'someone',
    'lastname': 'last',
    'email': 'somemail@google.com',
    'password': 'Password0',
    'phone_number': '123456789',
    'country': 'China',
    'city': 'somecity',
    'address': 'somewhere',
    'postal_code': '200199',
    'province': 'somestate',
    'safepay_username': '12345678910',
    'safepay_password': 'Password123',
    'shopping_list': {
        'HP Z3200 Wireless Mouse': {
                'red': {'amount': 2, 'price': 29.99, },
                'white': {'amount': 1, 'price': 29.99, },
        },
        'HP Z4000 Wireless Mouse': {
                'blue': {'amount': 1, 'price': 9.99, },
        },
    },
    # 'total_budget': '$89.97',
    # 'red_budget': '$59.98',
}


# set up the right amount
def set_amount(n: int) -> None:
    # reset amount when needed
    while True:
        # check if rest still needed
        try:
            #################################################################################
            # When the amount is 1, the button '-' is un-clickable, in another word:
            # Element div[class='minus disableBtn'] is locatable, which means, no rest needed
            # --> break the loop!
            #################################################################################
            driver.find_element_by_css_selector("div[class='minus disableBtn']")
            break
        except NoSuchElementException:
            print("Amount not minimal.")
            # click on '-'
            minus = driver.find_element_by_xpath(
                "//div[@class='e-sec-plus-minus']/div[1]"
            )
            driver.execute_script('arguments[0].click()', minus)
            print("Amount --")
            time.sleep(1)
    # set up new amount
    if n > 1:
        for i in range(n - 1):
            # click on '+'
            plus = driver.find_element_by_xpath(
                "//div[@class='e-sec-plus-minus']/div[3]"
            )
            driver.execute_script('arguments[0].click()', plus)
            print("Amount ++")
            time.sleep(1)


# get what is required
def get_goods(shopping_list: dict) -> None:
    ############################################################################################
    # The shopping list suppose to be a dictionary of product names and dictionaries of colours.
    # Each colour contains amount and planed budget for single price. It looks like this:
    # 'shopping_list': {
    #     'HP Z3200 Wireless Mouse': {
    #         'red': {'amount': 2, 'price': 29.99, },
    #         'white': {'amount': 1, 'price': 29.99, },
    #     },
    # },
    ############################################################################################
    # for required product(s)...
    for product, content in shopping_list.items():
        # pick {product}
        print("Picking {0}...".format(product))
        target = driver.find_element_by_xpath(
            "//div[@class='cell categoryRight']/ul[1]/li/p[1]/a[text()='{0}']".format(product)    # original name
        )
        driver.execute_script('arguments[0].click()', target)
        time.sleep(3)
        # for required colour(s)...
        for colour, amount_price in content.items():
            # pick {amount} {colour}
            print("Picking {1} {0}...".format(colour, amount_price['amount']))
            clr = driver.find_element_by_xpath(
                "//div[@class='colors ng-scope']/div[2]/span[@title='{0}']".format(colour.upper())
            )
            driver.execute_script('arguments[0].click()', clr)
            time.sleep(1)
            # set the required amount
            set_amount(int(amount_price['amount']))
            # save to cart
            driver.find_element_by_name('save_to_cart').click()
            print("Added to cart.")
            time.sleep(1)
        driver.back()
        time.sleep(3)


# verify the shopping cart
def verify_cart(shopping_list: dict, **kwargs) -> bool:
    ##########################################################################################
    # To **kwargs should be given a dictionary of product and colour, that need to be verified
    # For example: {'HP Z3200 Wireless Mouse': 'red', 'HP Z4000 Wireless Mouse': 'blue'}
    ##########################################################################################
    check_list = []
    # calculate total budget
    total_budget = 0
    for product in shopping_list.keys():
        for content in shopping_list[product].values():
            total_budget += int(content['amount']) * float(content['price'])
    # verify the total sum ($89.97 for HP Z3200 Wireless Mouse)
    total_sum = driver.find_element_by_xpath(
        "//div[@id='shoppingCart']/table[1]/tfoot[1]/tr[1]/td[2]/span[2]"
    ).text    # string
    c = "OK" if (total_sum == '$'+str(total_budget)) is True else "Not OK"
    check_list.append(c)
    print("Sum of total: {0}, {1}".format(total_sum, c))

    # calculate budget of certain product type
    if len(kwargs) != 0:
        for product, colour in kwargs.items():
            product_budget = 0
            content = shopping_list[product][colour.lower()]
            product_budget += int(content['amount']) * float(content['price'])
            # verify product sum ($59.98 for 2 reds)
            product_sum = driver.find_element_by_xpath(
                """//div[@id='shoppingCart']/table[1]/tbody[1]/
                tr[td[4]/span[1]/@title='{1}' and td[2]/label[1][contains(text(),'{0}')]]/
                td[6]/p[1]""".format(product.upper(), colour.upper())    # name in capital
            ).text    # string
            c = "OK" if (product_sum == '$'+str(product_budget)) is True else "Not OK"
            check_list.append(c)
            print("Sum of {1} {0}: {2}, {3}".format(product, colour, product_sum, c))
    else:
        pass
    # witch purchase
    if all(check_list) is True:
        print("Prices verified.")
        p = True
    else:
        print("Prices are NOT correct.")
        p = False

    return p


# clean up shopping cart
def clean_cart() -> None:
    print("Cleaning up the shopping cart...")
    m = len(driver.find_elements_by_xpath(
        "//table[@class='fixedTableEdgeCompatibility']/tbody[1]/tr"
    ))
    # print("There are {0} type(s) of product(s) in shopping cart.".format(m))
    for i in range(m):
        remove = driver.find_element_by_xpath(
            "//div[@id='shoppingCart']/table[1]/tbody[1]/tr[1]/td[6]/span[1]/a[3]"
        )
        driver.execute_script('arguments[0].click()', remove)
        print("Product removed.")
        time.sleep(1)


if __name__ == '__main__':

    # Open website
    webdriver.FirefoxOptions().add_argument('--headless')
    driver = webdriver.Firefox()
    driver.implicitly_wait(3)
    # driver.maximize_window()
    print("Opening browser...")
    driver.get(infos.get('url'))
    time.sleep(5)

    # login
    print("Signing in...")
    driver.find_element_by_id('menuUser').click()
    time.sleep(1)
    driver.find_element_by_name('username').clear()
    driver.find_element_by_name('username').send_keys(infos.get('username'))
    driver.find_element_by_name('password').clear()
    driver.find_element_by_name('password').send_keys(infos.get('password'))
    driver.find_element_by_id('sign_in_btnundefined').click()
    time.sleep(1)

    # go to mice category
    print("Looking for mice...")
    mice = driver.find_element_by_id('miceImg')
    driver.execute_script('arguments[0].click()', mice)
    time.sleep(3)

    # pick the product.
    get_goods(infos.get('shopping_list'))
    time.sleep(3)

    # go to shopping cart
    print("Verifying the prise...")
    driver.find_element_by_id('menuCart').click()
    time.sleep(1)

    # verify the prises
    d = {
        'HP Z3200 Wireless Mouse': 'red',
        'HP Z4000 Wireless Mouse': 'blue',
    }
    purchase = verify_cart(infos.get('shopping_list'), **d)
    time.sleep(1)

    # when amounts of products need to be corrected
    if purchase is not True:
        # clean up cart
        clean_cart()
        time.sleep(1)
        # back to home page
        print("Re-pick the amounts of mice...")
        driver.find_element_by_id('Layer_1').click()
        time.sleep(3)
        driver.find_element_by_id('miceImg').click()
        time.sleep(3)
        # pick the product
        get_goods(infos.get('shopping_list'))
        time.sleep(3)
    else:
        pass

    # order payment
    print("Checking order payment...")
    driver.find_element_by_id('menuCart').click()
    time.sleep(1)
    driver.find_element_by_id('checkOutButton').click()
    time.sleep(3)

    # if the page 'SHIPPING DETAILS' shows up
    try:
        # driver.find_element_by_id('next_btnundefined').click()
        # try click on 'BACK'
        driver.find_element_by_css_selector(
            "a[class='roboto-medium float-button a-link linkToPress ng-scope']"
        ).click()
        time.sleep(1)
    except NoSuchElementException:
        time.sleep(3)
        print("Page SHIPPING DETAILS' skipped")
        pass
    except ElementNotInteractableException:
        time.sleep(3)
        print("Page SHIPPING DETAILS' skipped")
        pass

    # next-button by page 'ODER PAYMENT'
    pm_next = WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.ID, 'next_btn'))
    )
    pm_next.click()
    print("Shipping details checked!")
    time.sleep(3)

    '''
    print("Editing shipping details...")
    driver.find_element_by_xpath("//div[@id='userSection']/div[1]/div[@class='blueLink']/a[1]").click()
    time.sleep(1)
    # Select(driver.find_element_by_name('countryListbox')).select_by_value("object:3728")
    Select(driver.find_element_by_name('countryListbox')).select_by_visible_text(infos.get('country'))
    # city
    input_city = driver.find_element_by_xpath(
        "//input[@name='city' and @class='ng-pristine ng-valid ng-scope ng-touched']"
    )
    input_city.clear()
    input_city.send_keys(infos.get('city')
    time.sleep(3)
    '''

    # re-enter Safepay information
    driver.find_element_by_css_selector("img[alt='Safepay']").click()
    driver.find_element_by_name('safepay_username').clear()
    driver.find_element_by_name('safepay_username').send_keys(infos.get('safepay_username'))
    driver.find_element_by_name('safepay_password').clear()
    driver.find_element_by_name('safepay_password').send_keys(infos.get('safepay_password'))
    print("Payment method checked!")
    time.sleep(3)

    # press 'PAY NOW'
    print("Paying...")
    driver.find_element_by_id('pay_now_btn_SAFEPAY').click()
    print("Thanks for your purchasing!")
    time.sleep(3)

    # back to home page
    driver.find_element_by_id('Layer_1').click()
    print('See you next time!')
    time.sleep(1)

    # close browser
    driver.quit()
