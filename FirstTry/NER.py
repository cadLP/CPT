from __future__ import print_function, unicode_literals
import spacy
import de_core_news_sm

nlp = de_core_news_sm.load()
doc = nlp(u'Ich bin ein Berliner.')
doc2 = nlp(u'Das menschliche Gehirn kennt wissenschaftlichen Erkenntnissen zufolge drei Arten von Belohnung: die materielle, die soziale und die intrinsische. „Der Vorteil der materiellen Belohnung ist, dass sie sehr schnell wirkt“, sagt der Bremer Biologe Gerhard Roth, einer der renommiertesten Hirnforscher hierzulande. Der Nachteil: Die Wirkung lasse auch schnell wieder nach. Mit jeder Wiederholung der selben Belohnung halbiere sich deren Wirkung. Um diese Diskontierung zu verhindern, müsse man die Belohnung erhöhen. Dadurch trete zwar abermals eine positive Wirkung ein, der Abschwung trete jetzt jedoch noch schneller ein. Damit zeige jede Erhöhung weniger Wirkung, sagt Roth und spricht von einer „Bonus-Falle“. Der Grund für diesen Effekt sei in unseren Gehirnen verankert, erklärt Roth. Eine eigentlich einmalig angelegte Belohnung werde von den Menschen sofort eingepreist und daraus ein Anspruch für die Zukunft abgeleitet. Zu beobachten ist das in der Bankenbranche, in der Bonus-Zahlungen nicht mehr als Ausweis für besondere wirtschaftliche Erfolge betrachtet werden, sondern in gewissen Positionen und Funktionen als Selbstverständlichkeit betrachtet werden. Eine Nicht-Zahlung würden die Betroffenen als Entzug empfinden, erläutert Roth. „Damit wird die Botschaft gesendet: Ich bin denen nichts mehr Wert.“ Der Schmerz sei doppelt so groß wie der Zugewinn, sagt Roth, diese Erkenntnis über die Wirkung materieller Belohnung gehe auf den Nobelpreisgewinner Daniel Kahneman zurück. Langfristig hilft nur Spaß an der Arbeit Die soziale Belohnung obliege den selben Gesetzen. Auch wiederholtes Lob verliere irgendwann seine Wirkung – es sei denn, es bleibt aus. Nur für die intrinsische Belohnung in Form von Spaß und Zufriedenheit mit der eigenen Arbeit gelte dies nicht. Das Problem ist nur, das man diese von außen nicht direkt beeinflussen kann. „Sie können nur einen optimalen Rahmen schaffen, damit ihre Mitarbeiter zufrieden sind“, sagt Roth. Die Menschen besitzen laut Roth zudem ein gutes Gespür dafür, ob eine Belohnung gerecht sei oder nicht. Seine Warnung diesbezüglich ist eindeutig: „Nichts verdirbt die Sitten so sehr wie eine ungerechte Belohnung.“')

print(' '.join('{word}/{tag}'.format(word=t.orth_, tag=t.tag_) for t in doc))

#print(' '.join('{word}/{tag}').format(word=ent.text, tag=ent.label_) for ent in doc2.ents)

ner_tags = ""

for ent in doc2.ents:
    ner_tags.append(ent.text + '/' + ent.label_)
    print(ent.text, ent.label_)
    print(ner_tags)