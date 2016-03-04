Twitter API/Gephi


1) DEVELOPMENT ENVIRONMENT

Python 2.7.10


2) IMPLEMENTATION

Our goal of the task is to analyze Twitter tweets about the recent tragedy Paris attacks, and build a network between the source user who posts tweets and the target user who receives them by using Gephi.

The tweets are sourced through Twitter API. First of all, we need to create an application which is named after “Tweet_Duang” in https://apps.twitter.com/, and generate API keys and Access tokens, which we will use in Python to crawl tweets by, specifically, the API “GET search/tweets” that returns a collection of relevant tweets matching a specified query. And the tweets can be searched based on some parameters: the query fields, geocode (latitude, longitude and radius), until (the expiration date when tweets created before), result type (mixed, recent, popular), and the number of counts. Refer to more information in Twitter API (https://dev.twitter.com/rest/reference/get/search/tweets). Here we focus on Paris (48.8567° N, 2.3508° E) where the event happened, and set the radius 200 miles.

Given one query parameter, e.g., “attack”, the API would feed back the tweets of text containing the parameter. Since we aim to build a network between Twitter users, only the tweets that are posted as reply messages are considered. For each replying tweet, we set the author as the source user, and the users who receive it as the target users, whose screen names are in the format “@xxxx” in the message. And GEXF file accepts only unicode or ACSII. Therefore, extract the target users by matching the regular expression “@\w+” while some results are not exactly the user names, such as “@Paris”. So we need to verify if it is a valid user name in another method “GET users/search”. Then collect all the valid users’ IDs and insert them into a sqlite database, where two tables are created: nodes for users information (user ID, user label and created date / time), and links for users’ connection by tweets (source user ID, target user ID, created date / time). The created date / time is formatted of XSD date time type “YYYY-MM-DDThh:mm:ss” for building a network in Gephi. The query is predefined in some terms such as “terror”, “bataclan”, “shoot”, etc. which are likely related to the event Paris attacks. And also we can vary the radius of the location where the tweets are posted and the number of counts to be searched. Run the program and we obtain nodes and links.

Well, after the database is prepared, we can retrieve the nodes and links to output into a GEXF file. It is implemented in a Python program. Import the package pygexf to create a file and add one graph, and add each node and link into the graph. Map (user ID, user screen name, created date / time) to node (id, label, start), and (tweet ID, source user ID, target user ID, created date / time) to link (id, source, target, start) in gexf format. And then output the graph to the file.


3) TROUBLESHOOTING

In MAC OS X, if there are some issues about packages such as lxml and gexf, try the possible solutions:

•	Run xcode-select --install

•	Open XCode and accept the Terms & Conditions

•	Run sudo pip install lxml


4) REFERENCE

https://github.com/dudaspm/DataAnalytics/blob/master/Week8/getTweets.py
https://github.com/paulgirard/pygexf
