#!/usr/bin/python

import string
import math
import js2py
import urllib2
import ujson as json

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

#our weighting function
def weighting(rating,deviation,cutoff):
	if deviation > 100 and cutoff > 1500:
		return 0.0
	return (math.erf(float(rating-cutoff)/float(deviation)/math.sqrt(2.0))+1.0)/2.0
	#return victoryChance(rating,deviation,cutoff,0.0)
	#this is for logistic weighting
	#s=math.sqrt(3.0)*float(deviation)/math.pi
	#return (math.tanh(float(rating-cutoff)/s/2.0)+1.0)/2.0
	#this is for extreme value weighting
	#b=math.sqrt(6.0)*float(deviation)/math.pi
	#return 1.0-math.exp(-math.exp(-float(cutoff-rating)/b))

#if (r2,d2)=(1500,350) this becomes the GXE formula
def victoryChance(r1,d1,r2,d2):
	C=3.0*pow(math.log(10.0),2.0)/pow(400.0*math.pi,2)
	return 1.0 / (1.0 + pow(10.0,(r2-r1)/400.0/math.sqrt(1.0+C*(pow(d1,2.0)+pow(d2,2.0))))) 

def readTable(filename):
	file = open(filename)
	table=file.readlines()
	file.close()

	usage = {}

	nBattles = int(table[0][16:])

	for i in range(5,len(table)):
		line = table[i].split('|')
		if len(line)<3:
			break
		name = line[2][1:]

		while name[len(name)-1] == ' ': 
			#remove extraneous spaces
			name = name[0:len(name)-1]

		pct = line[3][1:line[3].index('%')]
	
		usage[name]=float(pct)/100.0

	return usage,nBattles



def getFormats():
	js=urllib2.urlopen("https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/config/formats.js").read()
	print 'Updating tiers'
	return json.loads(js2py.eval_js('exports={},'+js+'JSON.stringify(exports.Formats)'))

def getBattleFormatsData():
	js=urllib2.urlopen("https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/formats-data.js").read()
	print 'Updating tiers'
	return json.loads(js2py.eval_js('exports={},'+js+'JSON.stringify(exports.BattleFormatsData)'))

aliases={
	'NidoranF': ['Nidoran-F'],
	'NidoranM': ['Nidoran-M'],
	'Wormadam-Sandy': ['Wormadam-S', 'Wormadamsandy'],
	'Wormadam-Trash': ['Wormadam-G', 'Wormadamtrash'],
	'Giratina-Origin': ['Giratina-O'],
	'Unown': ['Unown-B','Unown-C','Unown-D','Unown-E','Unown-F','Unown-G','Unown-H','Unown-I','Unown-J','Unown-K','Unown-L','Unown-M','Unown-N','Unown-O','Unown-P','Unown-Q','Unown-R','Unown-S','Unown-T','Unown-U','Unown-V','Unown-W','Unown-X','Unown-Y','Unown-Z','Unown-!','Unown-?'],
	'Burmy': ['Burmy-G','Burmy-S', 'Burmy-Sandy', 'Burmysandy', 'Burmy-Trash', 'Burmytrash'],
	'Castform': ['Castform-Snowy','Castform-Rainy','Castform-Sunny'],
	'Cherrim': ['Cherrim-Sunshine'],
	'Shellos': ['Shellos-East','Shelloseast'],
	'Gastrodon': ['Gastrodon-East','Gastrodoneast'],
	'Deerling': ['Deerling-Summer','Deerling-Autumn','Deerling-Winter','Deerlingsummer', 'Deerlingautumn', 'Deerlingwinter'],
	'Sawsbuck': ['Sawsbuck-Summer','Sawsbuck-Autumn','Sawsbuck-Winter','Sawsbucksummer', 'Sawsbuckautumn', 'Sawsbuckwinter'],
	'Tornadus-Therian': ['Tornadus-T'],
	'Thundurus-Therian': ['Thundurus-T'],
	'Landorus-Therian': ['Landorus-T'],
	'Keldeo': ['Keldeo-R','Keldeo-Resolution','Keldeo-Resolute','Keldeoresolute'],
	'Meloetta': ['Meloetta-S','Meloetta-Pirouette','Meloettapirouette'],
	'Genesect': ['Genesect-Douse','Genesect-Burn','Genesect-Shock','Genesect-Chill','Genesect-D','Genesect-S','Genesect-B','Genesect-C','Genesectdouse','Genesectburn','Genesectshock','Genesectchill'],
	'Darmanitan': ['Darmanitan-D','Darmanitan-Zen','Darmanitanzen'],
	'Basculin': ['Basculin-Blue-Striped','Basculin-A','Basculinbluestriped'],
	'Kyurem-Black': ['Kyurem-B'],
	'Kyurem-White': ['Kyurem-W'],
	'Pichu': ['Pichu-Spiky-eared','Spiky Pichu','Pichuspikyeared','Spikypichu'],
	'Rotom-Heat': ['Rotom-H','Rotom- H','Rotom-h'],
	'Rotom-Wash': ['Rotom-W','Rotom -W','Rotom-w'],
	'Rotom-Frost': ['Rotom-F','Rotom -F', 'Rotom-f'],
	'Rotom-Fan': ['Rotom-S','Rotom -S', 'Rotom-s'],
	'Rotom-Mow': ['Rotom-C','Rotom -C',' Rotom-c'],
	'Deoxys-Defense': ['Deoxys-D'],
	'Deoxys-Attack': ['Deoxys-A'],
	'Deoxys-Speed': ['Deoxys-S'],
	'Shaymin-Sky': ['Shaymin-S'],
	'Ho-Oh': ['Ho-oh'],
	'Virizion': ['Birijion'],
	'Terrakion': ['Terakion'],
	'Acceldor': ['Agirudaa'],
	'Landorus': ['Randorosu'],
	'Volcarona': ['Urugamosu'],
	'Whimsicott': ['Erufuun'],
	'Excadrill': ['Doryuuzu'],
	'Jellicent': ['Burungeru'],
	'Ferrothorn': ['Nattorei', 'Ferry'],
	'Chandelure': ['Shadera'],
	'Conkeldurr': ['Roobushin'],
	'Haxorus': ['Ononokusu'],
	'Hydreigon': ['Sazandora'],
	'Cinccino': ['Chirachiino'],
	'Kyurem': ['Kyuremu'],
	'Sperperior': ['Jarooda'],
	'Zoroark': ['Zoroaaku'],
	'Mandibuzz': ['Barujiina'],
	'Reuniclus': ['Rankurusu','Rank'],
	'Thundurus': ['Borutorosu'],
	'Mime Jr.': ['Mime Jr'],
	'Dragonite': ['Dnite'],
	'Forretress': ['Forry'],
	'Lucario': ['Luke'],
	'Porygon2': ['P2','Pory2'],
	'Porygon-Z': ['Pz','Poryz','PorygonZ'],
	'Tyranitar': ['Ttar'],
	'Pumkaboo': ['Pumpkaboo-Average','Pumpkabooaverage'],
	'Gourgeist': ['Gourgeist-Average','Gourgeistaverage'],
	'Aegislash': ['Aegislash-Blade','Aegislashblade'],
	'Floette-Eternal' : ['Floetteeternalflower','Floetteeternal'],
	'Pikachu' : ['Pikachu-Cosplay','Pikachu-Belle','Pikachu-Rock-Star','Pikachu-Pop-Star','Pikachu-PhD','Pikachu-Libre'],
	'Meowstic' : ['Meowstic-F','Meowstic-M','Meowsticf','Meowsticm'],
	'Bisharp' : ['Bsharp'],
	'Missingno' : ['Missingno.'],
	'Vivillon' : ["Vivillon-Archipelago", "Vivillon-Continental", "Vivillon-Elegant", "Vivillon-Garden", "Vivillon-Highplains", "Vivillon-Icysnow", "Vivillon-Jungle", "Vivillon-Marine", "Vivillon-Modern", "Vivillon-Monsoon", "Vivillon-Ocean", "Vivillon-Polar", "Vivillon-River", "Vivillon-Sandstorm", "Vivillon-Savanna", "Vivillon-Sun", "Vivillon-Tundra", "Vivillon-Fancy", "Vivillon-Pokeball", "Vivillonarchipelago", "Vivilloncontinental", "Vivillonelegant", "Vivillongarden", "Vivillonhighplains", "Vivillonicysnow", "Vivillonjungle", "Vivillonmarine", "Vivillonmodern", "Vivillonmonsoon", "Vivillonocean", "Vivillonpolar", "Vivillonriver", "Vivillonsandstorm", "Vivillonsavanna", "Vivillonsun", "Vivillontundra", "Vivillonfancy", "Vivillonpokeball"],
	'Flabebe' : ["Flabebeblue", "Flabebeorange", "Flabebewhite", "Flabebeyellow", "Flabebe-Blue", "Flabebe-Orange", "Flabebe-White", "Flabebe-Yellow", u'Flabe\u0301be\u0301'],
	'Floette' : ["Floetteblue", "Floetteorange", "Floettewhite", "Floetteyellow", "Floette-Blue", "Floette-Orange", "Floette-White", "Floette-Yellow"],
	'Florges' : ["Florgesblue", "Florgesorange", "Florgeswhite", "Florgesyellow", "Florges-Blue", "Florges-Orange", "Florges-White", "Florges-Yellow"],
	'Ditto': ['Dtto'],
	'Magearna': ['Magearnaoriginal', 'Magearna-Original'],
	'Minior': ['Minior{}'.format(color) for color in ('orange', 'yellow', 'green', 'blue', 'indigo', 'violet')] + ['Minior-{}'.format(color) for color in ('Orange', 'Yellow', 'Green', 'Blue', 'Indigo', 'Violet')],
	'Greninja-Ash': ['Ashgreninja', 'Ash-Greninja'],
	'Zygarde-10%': ['Zydog', 'Zygardedog', 'Zygarde-Dog'],
	'Zygarde': ['Zygarde-50%', 'Zygarde50'],
	'Zygarde-Complete': ['Zyc', 'Zygarde-100%', 'Zygarde100', 'Zygarde-C', 'Zygarde-Full', 'Zygod', 'Perfect-Zygarde'],
	'Oricorio': ['Oricorio-Baile', 'Oricoriobaile'],
	'Oricorio-Sensu': ['Oricorio-S'],
	'Lycanroc': ['Lycanroc-Midday', 'Lycanrocmidday', 'Lycanroc-Day', 'Lycanrocday'],
	'Lycanroc-Midnight': ['Lycanroc-Night', 'Lycanrocnight'],
	'Furfrou': ['Furfrou{}'.format(trim) for trim in ("dandy", "debutante", "diamond", "heart", "kabuki", "lareine", "matron", "pharaoh", "star")] + ['Furfrou-{}'.format(trim.title()) for trim in ("dandy", "debutante", "diamond", "heart", "kabuki", "lareine", "matron", "pharaoh", "star")]
}

nonSinglesFormats = [
	'battlespotdoubles',
	'battlespottriples',
	'gen5smogondoubles',
	'orassmogondoubles',
	'randomdoublesbattle',
	'randomtriplesbattle',
	'smogondoubles',
	'smogondoublessuspecttest',
	'smogondoublesubers',
	'smogondoublesuu',
	'smogontriples'
	'smogontriples',
	'vgc2014',
	'vgc2015',
	'vgc2016',
	'vgc2017',
	'battlespotspecial7',
	'doublesou',
	'doublesubers'
	'doublesuu',
	'gen7battlespotdoubles',
	'gen7doublesanythinggoesbeta',
	'gen7doublesanythinggoes',
	'gen7doublesou',
	'gen7doublesoubeta',
	'gen7pokebankdoublesag',
	'gen7pokebankdoublesanythinggoes',
	'gen7pokebankdoubleaanythinggoes',
	'gen7pokebankdoublesou',
	'gen7pokebankdoublesoubeta',
	'gen7randomdoublesbattle',
	'gen7vgc2017',
	'gen7vgc2017beta',
	'gen5doublesou',
]

non6v6Formats = [
	'1v1',
	'battlespotdoubles',
	'battlespotsingles',
	'challengecup1v1',
	'gen5gbusingles',
	'vgc2014',
	'vgc2015',
	'vgc2016',
	'vgc2017',
	'battlespotspecial7',
	'pgllittlecup',
	'gen7battlespotsingles',
	'gen7battlespotdoubles',
	'gen7vgc2017',
	'gen7vgc2017beta',
	'gen7challengecup1v1',
	'gen71v1',
	'gen7alolafriendly',
]
