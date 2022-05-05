![Usage-Based Data Discovery Web App](https://github.com/ESIPFed/ubd-tool-remotedb/blob/main/static/ubd-app.png?raw=true)


## Development

The following instructions have only been tested on macOS. However the app can be run entirely in Docker (see [Makefile](Makefile) for relevant Docker commands).

- Install (and use) **python3.8**. We recommend using a tool like **pyenv**.
- Install Docker Desktop
- Clone this repo and navigate to the root directory.
- Create .env.development in the root directory and set ORCID to a value in [orcid.json](./orcid.json) to simulate role=supervisor (or blank for role=general) when logged in
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

