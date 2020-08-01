# Usage-Based Discovery Prototype - A simple web application
 

General instructions for set up:


Need a Neo4j database running:

1. If using Docker:

`$ docker run -d -e NEO4J_AUTH=neo4j/ubdprototype -p 7687:7687 -p 7474:7474 --name neo4j --rm neo4j`

(To stop Neo4j, `docker stop neo4j`. The docker container will be automatically removed.)

2. Using Neo4J Desktop

- Install Neo4j Desktop application at https://neo4j.com/download/

- Start up Neo4j Desktop, click 'New' to create a new project, and then 'Add Database'

- Select "Set up a local database" and enter a name for your database

- Set password as 'ubdprototype'

- Start the database

- Clone this repository. cd into the project directory. 

3. Install the required python packages

`$ pip install -r requirements.txt`

4. Run the application

`$ python app.py`

5. Browse to http://localhost:5000


Any questions or suggestions for improvement?
- Questions - email maggieqzhu@yahoo.com 
- Suggestions - submit a pull request




Ways to contribute to this project: 
- Redesign this application to be compatible with a remote Neo4j database (with pass
- Automate the relationship foraging process (will likely involve web scraping and/or ML)



