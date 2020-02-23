from cpt.spiders.SuedRunner import ScrapyCrawler
from cpt.spiders.ScrapyProcess import ScrapyProcess
known_spiders = ["sueddeutsche", "faz", "wiwo", "spiegel", "heise"]
spiders = []
categories = []
allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                 "Wissen", "Digital", "Karriere", "Reisen", "Technik"]


def readspiders():
    """
    This method reads the spiders that are to be used from the console while allowing for adjustments.
    """
    eingabe = input()
    if eingabe == "":
        return True
    if eingabe == "reset":
        categories.clear()
        spiders.clear()
    if eingabe.lower() == "all":
        for spider in known_spiders:
            if spider not in spiders:
                spiders.append(spider.lower())
        return False
    spiders_input = eingabe.split()
    if spiders_input[0].lower() == "remove":
        for spider in spiders_input[1:]:
            if spider.lower() in spiders:
                spiders.remove(spider.lower())
        return False
    for spider in spiders_input:
        if spider.lower() in known_spiders:
            spiders.append(spider.lower())
    return False


def readcategories():
    """
    This method reads the categories that are to be scraped from the console while allowing for adjustments.
    :return:
    """
    eingabe = input()
    if eingabe == "":
        return True
    if eingabe == "reset":
        categories.clear()
        spiders.clear()
    if eingabe.lower() == "all":
        for category in allcategories:
            if category not in categories:
                categories.append(category.capitalize())
        return False
    categories_input = eingabe.split()
    if categories_input[0].lower() == "remove":
        for category in categories_input[1:]:
            if category.capitalize() in categories:
                categories.remove(category.capitalize())
        return False
    for category in categories_input:
        if category.capitalize() in allcategories:
            categories.append(category.capitalize())
    return False


def startScrape():
    """
    This method reads first Spiders and second Categories from the console and starts the spiders.
    :return:
    """
    print("Please enter Spiders to use with Spaces inbetween (for all, type \"all\"):\n")
    spiders_read = False
    while not spiders_read:
        spiders_read = readspiders()
        if not spiders_read:
            print("Following Spiders where recognized: "+str(spiders)+"")
            print("To confirm please press Enter, to add more Spiders enter the same as before, to remove Spiders preface input with \"remove\".\n")

    print("Please enter Categories to use with Spaces inbetween (for all, type \"all\"):\n")
    categories_read = False
    while not categories_read:
        categories_read = readcategories()
        if not categories_read:
            print("Following Categories where recognized: "+str(categories)+"")
            print("To confirm please press Enter, to add more Categories enter the same as before, to remove Categories preface input with \"remove\".\n")

    while not (spiders and categories):
        print("Either Spiders or Categories empty, restarting...\n")
        startScrape()

    crawler = ScrapyCrawler(categories, spiders)
    #crawlertwo = ScrapyProcess(categories, spiders)
    crawler.runcrawler()
    categories.clear()
    spiders.clear()

def startTag():
    """
    This method reads which text ist to be text and which methods is to be used from the console.
    :return:
    """
    pass


def getTask():
    """
    This method assigns the task to be completed by the System depending on user input.
    :return:
    """

    eingabe = input("Please choose whether you would like to \"Scrape\", \"Tag\", \"View\", \"Export\", or \"Exit\":\n").lower()
    if eingabe == "scrape":
        print("Remember, multiple Scrapes different will require a restart, due to Twisted's Reactor.\n\n")
        startScrape()
    if eingabe == "tag":
        # Todo
        startTag()
        getTask()
    if eingabe == "view":
        # Todo?
        getTask()
    if eingabe == "export":
        # Todo
        getTask()
    if eingabe == "exit":
        exit(0)


while True:
    getTask()
