import time
import selenium
import config as cfg
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import logging
logging.basicConfig(filename='debug.log')

#main function for main prompt
def main():
    print("Welcome to the POS helper!")
    print("1. Store Product Activation")
    print("2. Store Product Deactivation")
    print("3. Activate PAX")
    print("----------------------------------")
    choice = input("Selection: ")

    if choice == '1':
        print("Product Activation:")
        ActivateCode()
    if choice == '2':
        print("Product Deactivation:")
        DeactivateCode()
    if choice == '3':
        print("Activate PAX:")
        PAXActivation()

#Login function - Loads POS page for login and uses Username and Password Variables as set for login - returns driver made
def login():
    #using set driver path, create web driver
    driver = webdriver.Chrome(cfg.mysql['driverPath'])

    #first load POS login page
    driver.get(cfg.mysql['posLoginPage']);

    #send username to username field
    driver.find_element_by_name('userId').send_keys(cfg.mysql['user'])

    #send password to password field and hit enter
    driver.find_element_by_name('password').send_keys(cfg.mysql['password'] + Keys.ENTER)

    return driver

#helper function for activate product
def NoProductFound(driver, companySel, productCode, storeNum):

    #Navigate to search company product page
    driver.get(cfg.mysql['companyProductPage'])

    #Sets the company on the company product screen
    driver.find_element_by_name('compResourceId').send_keys(companySel)

    #product field on company product page
    productField = driver.find_element_by_name('productCode')
    productField.clear()
    productField.send_keys(productCode)

    #click search button
    driver.find_element_by_name('method.searchCompanyProducts').click()

    #find results
    results = driver.find_elements_by_class_name("result-row")

    #if there are any results
    if len(results) != 0:
        resultRow = results[0].find_elements_by_tag_name('td')
        #check to see if set to active
        if resultRow[5].text == "Yes":
            companyActive = True
        else:
            companyActive = False
    #if no results
    else:
        companyActive = False

    #if companyActive flag is off, the product is not active at the company and therefore can not be activated
    if companyActive == False:
        print('Product not active at company!')
        return

    #navigate to search product page
    driver.get(cfg.mysql['storeProductPage'])

    #make tempstore variable, for editing
    tempStore = storeNum

    while len(tempStore) > 0:

        #set company on store product page
        driver.find_element_by_name('compResourceId').send_keys(companySel)

        #set store number
        store = driver.find_element_by_name('storeNum')
        store.clear()
        store.send_keys(tempStore)

        #set product number, and search
        product = driver.find_element_by_name('productCode')
        product.clear()
        product.send_keys(productCode)
        product.send_keys(Keys.ENTER)

        #See if product exist at this store
        try:
            driver.find_element_by_name('productList[0].selected')
            active = True;
        except NoSuchElementException:
            print("Product Not found at " + tempStore)
            active = False

        #if not found and the tempStore is not 1 character, subtract 1 char from the end of the tempstore variable to search next for
        if active == False & len(tempStore) != 1:
            tempStore = tempStore[:-1]
            continue

        #if not found and tempstore is 1 char, then the product is not active at any store of the company
        elif active == False & len(tempStore) == 1:
            print("Product not found at any store")
            break

        #else it was found start Add like code
        else:
            print("Product found at "+ tempStore + " trying add like")

            #get results, and click the add like link
            results = driver.find_elements_by_class_name('result-row')
            innerResults = results[0].find_elements_by_tag_name('td')
            innerResults[8].find_element_by_tag_name('a').click()

            #set store that the product is being added to
            driver.find_element_by_name('storeResourceId').send_keys(storeNum)

            #click go
            driver.find_element_by_name('method.getUniqueVendorsForStore').click()

            #Clears not used fields that may throw error
            driver.find_element_by_name("minStockLimit").clear()
            driver.find_element_by_name("minPrice").clear()

            #Adds Like product to the store
            driver.find_element_by_name('method.saveStoreProduct').click()

            print("Successfully added product to store " + storeNum + " Using add like from store " + tempStore)
            break

#Activates codes given at given stores
#Checks to see if product is available at store to activate
#if it isnt calls, NoProductFound to check to see if active at the company
#and then trys to add like the product from another store
def ActivateCode():

    storeNum = input("What store(s)? (Delimit using commas (,)): ")
    productCode = input("What Product(s)? (Delimit using commas (,)): ")
    companySel = input("Company?(3 char prefix): ")
    storeNumArray = storeNum.split(',')
    productCodeArray = productCode.split(',')

    #call login function
    driver = login()

    #Navigate to search store product page
    driver.get(cfg.mysql['storeProductPage'])

    for storeNum in storeNumArray:
        for productCode in productCodeArray:

            #Sets the company on the store product screen
            driver.find_element_by_name('compResourceId').send_keys(companySel)

            #sets the store number field
            store = driver.find_element_by_name('storeNum')
            store.clear()
            store.send_keys(storeNum)

            #sets the product code field and presses enter
            product = driver.find_element_by_name('productCode')
            product.clear()
            product.send_keys(productCode)
            product.send_keys(Keys.ENTER)

            #Information on product for visual purposes
            print("-------------------------")
            print("Product Code: " + productCode)
            print("Store Number: " + storeNum)
            print("Company: " + companySel)

            #Try to find a result, if there is one check it and click the activate button
            try:
                driver.find_element_by_name('productList[0].selected').click()
                driver.find_element_by_name('method.prepActivateStoreProducts').click()
                active = True;
                print("Successfully Activated")
            except NoSuchElementException:
                active = False
                print("Product Not found at store!")

            if active == False:
                #if unable to activate, call no product found function
                NoProductFound(driver, companySel, productCode, storeNum)

            time.sleep(1)
            print()
            main()

#Deactivates given code from given store(s)
def DeactivateCode():

    storeNum = input("What store(s)? (Delimit using commas (,)): ")
    productCode = input("What Product(s)? (Delimit using commas (,)): ")
    companySel = input("Company?(3 char prefix): ")
    storeNumArray = storeNum.split(',')
    productCodeArray = productCode.split(',')

    #login and store driver variable
    driver = login()

    #navigate to search store product page
    driver.get(cfg.mysql['storeProductPage'])

    for storeNum in storeNumArray:
        for productCode in productCodeArray:

            #set company in the company select box on store product page
            driver.find_element_by_name('compResourceId').send_keys(companySel)

            #set store number in the store number field
            store = driver.find_element_by_name('storeNum')
            store.clear()
            store.send_keys(storeNum)

            #set product number in product field and then search
            product = driver.find_element_by_name('productCode')
            product.clear()
            product.send_keys(productCode + Keys.ENTER)

            #Information on product for visual purposes
            print("-------------------------")
            print("Product Code: " + productCode)
            print("Store Number: " + storeNum)
            print("Company: " + companySel)

            #try finding the results
            try:
                #click check box to select product
                driver.find_element_by_name('productList[0].selected').click()

                #click deactivate button
                driver.find_element_by_name('method.prepDeactivateStoreProducts').click()
                print("Successfully Deactivated")
            except NoSuchElementException:
                print("Product Not found!")

            time.sleep(1)
            driver.quit()
            print()
            main()

#needs Work - Allocates employees
def Allocation():
    storeNum = input("Store Number: ")
    employeeId = input("Employee ID: ")
    startDate = input("Start Date: ")
    stopDate = input("Stop Date: ")

    driver = login()

    driver.get("https://pos.vioc.com/viocpos-cwa-labor/SearchUsersForAllocation.do?method=prepSearchUsersToAllocate&mlev1=labor&mlev2=employeeallocation")

    storeField = driver.find_element_by_name('storeNum')
    storeField.send_keys(storeNum)

    userField = driver.find_element_by_name('userId')
    userField.send_keys(employeeId)

    searchBox = driver.find_element_by_name('method.searchUsersToAllocate')
    searchBox.click() #needs WOrk

#function to activate Accept Debit Cards and CC_SEMI_INTEGRATED Paramaters at given stores
def PAXActivation():

    storeNum = input("Store Number(s) (delimit by comma ','): ")
    stores = storeNum.split(',')

    #login
    driver = login()

    #navigate to store system parameters page
    driver.get(cfg.mysql['storeSystemParamPage'])

    for store in stores:

        #Send store number to store field
        driver.find_element_by_name('storeResourceId').send_keys(store)

        #click search
        driver.find_element_by_name('method.searchStoreSysParam').click()

        #find the accept debit cards row
        driver.find_elements_by_class_name("result-row")[0].find_element_by_tag_name('a').click()

        #set Accept Debit cards param to Y
        param = driver.find_element_by_name('paramValue')
        param.clear()
        param.send_keys("Y" + Keys.ENTER)

        #Navigate back one page
        driver.execute_script("history.go(-1)")
        driver.back()

        #find CC_integrated row
        driver.find_elements_by_class_name("result-row")[6].find_element_by_tag_name('a').click()

        #set CC_integrated parameter to Y
        param = driver.find_element_by_name('paramValue')
        param.clear()
        param.send_keys("Y" + Keys.ENTER)

        #navigate back one page
        driver.execute_script("history.go(-1)")
        driver.back()

    print()
    main()

main()

# TODO: Add Merchant Number finder
    #Store Resource ID for franchises
    #reset employee Password
    #propatgate employee and send to store
    #Reset employee A-ID Password
