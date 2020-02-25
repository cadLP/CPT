from cpt.spiders.Runner import ScrapyCrawler
from cpt.tagging import CrawlerTagging
from cpt.exporter import Export
from cpt.viewer import Viewer

spiders = []
categories = []
methods = []
allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                 "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
known_spiders = ["sueddeutsche", "faz", "wiwo", "heise", "spiegel"]
allmethods = ["treetagger_pos", "spacy_ner", "spacy_pos"]


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
            if spider.lower() not in spiders:
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
        return False
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
            if category.capitalize() not in categories:
                categories.append(category.capitalize())
    return False


def select():
    """
    This method reads first Spiders and second Categories from the console.
    :return:
    """
    print("Please enter Spiders to use with Spaces inbetween (for all, type \"all\"):")
    print("These are the spiders to choose from: " + str(known_spiders))
    spiders_read = False
    while not spiders_read:
        spiders_read = readspiders()
        if not spiders_read:
            print("Following Spiders where recognized: "+str(spiders)+"")
            print("To confirm please press Enter, to add more Spiders enter the same as before, to remove Spiders preface input with \"remove\".")

    print("Please enter Categories to use with Spaces inbetween (for all, type \"all\"):")
    print("These are the Categories to choose from: " + str(allcategories))
    categories_read = False
    while not categories_read:
        categories_read = readcategories()
        if not categories_read:
            print("Following Categories where recognized: "+str(categories)+"")
            print("To confirm please press Enter, to add more Categories enter the same as before, to remove Categories preface input with \"remove\".")

    if not (spiders and categories):
        print("Either no Spiders or no Categories selected, restarting...")
        categories.clear()
        spiders.clear()
        return False
    return True


def startScrape():
    """
    This methods starts the scraping process with selected spiders and categories.
    :return:
    """
    crawler = ScrapyCrawler(categories, spiders)
    crawler.startcrawl()
    #crawler.runcrawler()
    categories.clear()
    spiders.clear()


def readmethod():
    """
    This method reads the methods that are to be used for tagging from the console while allowing for adjustments.
    :return:
    """
    eingabe = input("")
    if eingabe == "":
        return True
    if eingabe == "reset":
        methods.clear()
        return False
    if eingabe.lower() == "all":
        for method in allmethods:
            if method not in methods:
                methods.append(method)
        return False
    methods_input = eingabe.split()
    if methods_input[0].lower() == "remove":
        for method in methods_input[1:]:
            if method.lower() in methods:
                methods.remove(method.lower())
        return False
    for method in methods_input:
        if method.lower() in allmethods:
            if method.lower() not in methods:
                methods.append(method.lower())
    return False


def startTag():
    """
    This method reads which text ist to be text and which methods is to be used from the console and starts
    the Tagging process.
    :return:
    """
    print("Please enter method(s) to be used:")
    print("These are the methods to choose from: " + str(allmethods))
    method_read = False
    while not method_read:
        method_read = readmethod()
        if not method_read:
            print("The following methods where recognized: "+str(methods))
            print("To confirm please press Enter, to add more Methods enter the same as before, to remove Methods preface input with \"remove\".")
    if not methods:
        print("No methods were selected, restarting")
        methods.clear()
        return
    print("Starting Tagging with :" + str(methods))
    CrawlerTagging(tagging_method=methods)
    methods.clear()


def view():
    """
    This method reads an sql query from the console and displays the result.
    :return:
    """
    eingabe = input("Please enter sql \"select\" query: \n")
    if eingabe == "":
        return
    if str(eingabe[0:6]).lower() != "select":
        print("Input not select statement, resetting...")
        return
    Viewer(eingabe)


def export():
    """
    This method reads a filename, a format and (in case of .json) a selection method from the console and exports the
    result from the database to a local file.
    :return:
    """
    print("Note: Only json export will allow for sql query / category / spider selection")
    eingabe = input("Please enter desired filename (Example: MyData):\n")
    if eingabe == "":
        return
    filename = eingabe
    eingabe = input("Please enter export method (json / xml):\n")
    exporter = Export()
    if eingabe.lower() == "xml":
        print("XML exporter started...")
        exporter.get_xml(filename)
        print("Export to " + filename + ".xml done.")
    elif eingabe.lower() == "json":
        eingabe = input("Please enter whether you would like to select via sql or spiders and categories (sql or Enter):\n")
        if eingabe == "sql":
            eingabe = input("Please enter sql select query:\n")
            if eingabe == "":
                return
            if str(eingabe[0:6]).lower() != "select":
                print("Input not select statement, resetting...")
                return
            try:
                print("JSON exporter started...")
                exporter.get_sql_json(eingabe, filename)
                print("Export to " + filename + ".json done.")
            except:
                print("Not a valid sql select query.")
                return
        if eingabe == "":
            selected = select()
            if selected:
                print("JSON exporter started...")
                exporter.get_json(filename=filename, source=spiders, categories=categories)
                print("Export to " + filename + ".json done.")
            spiders.clear()
            categories.clear()
    else:
        print("Format " + str(eingabe) + " not recognized, resetting...")
        return


def getTask():
    """
    This method assigns the task to be completed by the System depending on user input.
    :return:
    """
    while True:
        eingabe = input("Please choose whether you would like to \"Scrape\", \"Tag\", \"View\", \"Export\", or \"Exit\":\n").lower()
        if eingabe == "scrape":
            print("Remember, multiple different Scrapes will require a restart, due to Twisted's Reactor architecture.")
            if select():
                startScrape()
        if eingabe == "tag":
            startTag()
        if eingabe == "view":
            view()
        if eingabe == "export":
            export()
        if eingabe == "exit":
            break
print("Welcome to the CPT Crawler!")
getTask()

