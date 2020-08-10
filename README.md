# Usage-Based Discovery Prototype - A simple web application

To see the deployed application, click <a href="https://9dolot495j.execute-api.us-east-1.amazonaws.com/dev">here</a>.


General instructions for set up:

To access the database with the correct credentials contact me at maggieqzhu@yahoo.com. Once you obtain the username and password from me, execute the following commands (replacing 'username' and 'password' with the correct values):

`$ export NEO4J_USERNAME=username`<br />
`$ export NEO4J_PASSWORD=password`<br /><br />

Next up:

- Clone this repository. `$ cd` into the project directory. 
- Create a Python virtual environment with the command `$ virtualenv name-of-env`. 
For simplicity, name it 'venv'. 

- Start up the virtual environment using the following command `$ source venv/bin/activate`.
- Install the required python packages

`$ pip install -r requirements.txt`

- Run the application

`$ python app.py`

- Browse to http://localhost:5000

<br /><br />
Any questions or suggestions for improvement?
- Questions - email maggieqzhu@yahoo.com 
- Suggestions - submit a pull request

<br /><br />
Ways to contribute to this project:
- Automate the relationship foraging process (will likely involve web scraping and/or ML). A link for input/ideas: https://docs.google.com/document/d/1T0aPKu0mlW1syUEsAEXI3g3aTg-7m7XO7jTnnnoKLWI/edit?usp=sharing



