#!/usr/bin/python

import string
import math

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
	return (math.erf(float(rating-cutoff)/float(deviation)/math.sqrt(2.0))+1.0)/2.0
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

	for i in range(5,len(table)):
		name = table[i][10:29]
	
		if (name[0] == '-'):
			break

		while name[len(name)-1] == ' ': 
			#remove extraneous spaces
			name = name[0:len(name)-1]
	
		pct = table[i][31:39]
		usage[name]=float(pct)/100.0

	return usage

def getUsage(filename,col,weight,usage):
	tempUsage = readTable(filename)

	for i in tempUsage:
		if keyify(i) not in usage:
			usage[keyify(i)]=[0,0,0,0]
		if i != 'empty':
			usage[keyify(i)][col] = usage[keyify(i)][col]+weight*6.0*tempUsage[i]/sum(tempUsage.values())/24

aliases={
	'NidoranF': ['Nidoran-F'],
	'NidoranM': ['Nidoran-M'],
	'Pichu': ['Spiky Pichu'],
	'Rotom-Mow': ['Rotom-C'],
	'Rotom-Heat': ['Rotom-H'],
	'Rotom-Frost': ['Rotom-F'],
	'Rotom-Wash': ['Rotom-W'],
	'Rotom-Fan': ['Rotom-S'],
	'Deoxys-Attack': ['Deoxys-A'],
	'Deoxys-Defense': ['Deoxys-D'],
	'Deoxys-Speed': ['Deoxys-S'],
	'Wormadam-Sandy': ['Wormadam-G'],
	'Wormadam-Trash': ['Wormadam-S'],
	'Shaymin-Sky': ['Shaymin-S'],
	'Giratina-Origin': ['Giratina-O'],
	'Unown': ['Unown-B','Unown-C','Unown-D','Unown-E','Unown-F','Unown-G','Unown-H','Unown-I','Unown-J','Unown-K','Unown-L','Unown-M','Unown-N','Unown-O','Unown-P','Unown-Q','Unown-R','Unown-S','Unown-T','Unown-U','Unown-V','Unown-W','Unown-X','Unown-Y','Unown-Z','Unown-!','Unown-?'],
	'Burmy': ['Burmy-G','Burmy-S'],
	'Castform': ['Castform-Snowy','Castform-Rainy','Castform-Sunny'],
	'Cherrim': ['Cherrim-Sunshine'],
	'Shellos': ['Shellos-East'],
	'Gastrodon': ['Gastrodon-East'],
	'Deerling': ['Deerling-Summer','Deerling-Autumn','Deerling-Winter'],
	'Sawsbuck': ['Sawsbuck-Summer','Sawsbuck-Autumn','Sawsbuck-Winter'],
	'Tornadus-Therian': ['Tornadus-T'],
	'Thundurus-Therian': ['Thundurus-T'],
	'Landorus-Therian': ['Landorus-T'],
	'Keldeo': ['Keldeo-R','Keldeo-Resolution','Keldeo-Resolute'],
	'Meloetta': ['Meloetta-S','Meloetta-Pirouette'],
	'Genesect': ['Genesect-Douse','Genesect-Burn','Genesect-Shock','Genesect-Chill','Genesect-D','Genesect-S','Genesect-B','Genesect-C'],
	'Darmanitan': ['Darmanitan-D','Darmanitan-Zen'],
	'Basculin': ['Basculin-Blue-Striped','Basculin-A'],
	'Kyurem-Black': ['Kyurem-B'],
	'Kyurem-White': ['Kyurem-W'],
	'Pichu': ['Pichu-Spiky-eared'],
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
	'Tyranitar': ['Ttar']
}
