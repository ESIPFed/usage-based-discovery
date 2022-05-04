![Usage-Based Data Discovery Web App](https://github.com/ESIPFed/ubd-tool-remotedb/blob/main/static/ubd-app.png?raw=true)


## Local Development

- Install (and use) **python3.8** if not already available on your machine. We recommend using a tool like **pyenv**.
- Clone this repo and navigate to the root directory.
- `$ python3.8 -m venv ./venv`
- `$ source venv/bin/activate`
- `$ pip3 install -r requirements-dev.txt`
- `$ make app` and navigate to localhost:5000

Test via `$ make test`.

## Security

Install git-secrets on your machine to prevent yourself from accidentally committing sensitive info (like access keys, secrets) to your GitHub repo:

https://github.com/awslabs/git-secrets

Use Python Safety (https://github.com/pyupio/safety) to check your installed dependencies for known security vulnerabilities:

`$ safety check -r requirements.txt`

Use Python Bandit (https://github.com/PyCQA/bandit) to find common security issues in your Python code:

`$ bandit -r ~/your_repos/project`

**Snyk** is used as a blocking step to check dependencies for vulnerabilities when deploying to any environment.

## Contributing

Any questions or suggestions for improvement?
- Create an issue, and use the templates for feature request or bug reports for improvements
- Questions - email vincent.inverso@nasa.gov 

If looking to contribute, please look at [CONTRIBUTING.md](CONTRIBUTING.md).

