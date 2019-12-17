categories = {
    "Politik": {"https://www.faz.net/aktuell/politik"},
    "Wirtschaft": {"https://www.faz.net/aktuell/wirtschaft/"},
    "Finanzen": {"https://www.faz.net/aktuell/finanzen/"},
    "Sport": {"https://www.faz.net/aktuell/sport/"},
    "Kultur": {"https://www.faz.net/aktuell/feuilleton/", "https://www.faz.net/aktuell/stil/"},
    "Gesellschaft": {"https://www.faz.net/aktuell/gesellschaft/"},
    "Reisen": {"https://www.faz.net/aktuell/reise/"},
    "Technik": {"https://www.faz.net/aktuell/technik-motor/"},
    "Meinung": {"https://www.faz.net/aktuell/feuilleton/brief-aus-istanbul/",
                "https://www.faz.net/aktuell/rhein-main/buergergespraech/",
                "https://www.faz.net/aktuell/wirtschaft/hanks-welt/"},
    "Digital": {"https://www.faz.net/aktuell/technik-motor/digital/", "https://www.faz.net/aktuell/wirtschaft/digitec/",
                "https://www.faz.net/aktuell/finanzen/digital-bezahlen/"},
    "Wissen": {"https://www.faz.net/aktuell/wissen/", "https://www.faz.net/aktuell/wirtschaft/schneller-schlau/"},
    "Regional": {"https://www.faz.net/aktuell/rhein-main/"},
    "Karriere": {"https://www.faz.net/aktuell/karriere-hochschule/"}
}

to_selected_cat = ["Wirtschaft", "Finanzen", "Regional", "Digital"]

selected_categories = []

for x,y in categories.items():
    for i in to_selected_cat:
        if i == x:
            for a in y:
                selected_categories.append(a)

print(selected_categories)