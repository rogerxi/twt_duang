import sqlite3 as lite
from gexf import Gexf

## connect database
directory = '...'
db_path = directory + 'duang.db'
con = lite.connect(db_path)


gexf = Gexf("Duang", "A GEXF file about Tweets")
graph = gexf.addGraph(type="directed", mode="dynamic", label="Tweets Graph")#, timeformat="dateTime")

## read database
with con:
	curs = con.cursor()
	## read table nodes
	curs.execute('SELECT n.user_id, n.user_label, n.created_at FROM nodes AS n INNER JOIN links as l ON l.source = n.user_id OR l.target = n.user_id')
	nodes = curs.fetchall()
	nodes = set(nodes)
	## read table links
	curs.execute('SELECT * FROM links')
	links = curs.fetchall()
	## create gexf
	if (nodes is not None):
		## write nodes into one file of gexf format
		for node in nodes:
			graph.addNode(id=str(node[0].encode('utf-8')), label=str(node[1].encode('utf-8')), start=str(node[2]))
	if (links is not None):
		## write links into the file
		for link in links:
			graph.addEdge(id=str(link[0]), source = str(link[1].encode('utf-8')), target = str(link[2].encode('utf-8')), start=str(link[3]))
	## write the graph to file
	output_file = open(directory + "graph.gexf", "w")
	gexf.write(output_file)
	output_file.close()