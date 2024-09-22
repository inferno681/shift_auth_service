<details><summary><h1>Local Environment Setup</h1></summary>

To make changes to the repository, you need to work within a devcontainer.

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Install [Visual Studio Code](https://code.visualstudio.com/download)
- [Set up Visual Studio Code and Docker to use Devcontainers](https://code.visualstudio.com/docs/devcontainers/containers#_getting-started)
- [Configure Git and SSH for working in Devcontainer](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- [Install the Meslo Nerd Font for CLI in the terminal](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#fonts)
- Optionally, install and configure kubectl, as the container will use the host's settings
- Clone this repository to your workstation
- Open the repository directory in Visual Studio Code
- Install the [recommended Visual Studio Code extensions](.vscode/extensions.json)
- Press `Ctrl+Shift+P` or `Cmd+Shift+P` and select `Dev Containers: Rebuild and Reopen in Container`

</details>

<details><summary><h1>Installation Guide</h1></summary>

- Clone the repository and navigate into it.
```bash
git clone git@github.com:inferno681/shift_auth_service.git
```
- Create a .env file in the root directory of the project with environment variables:
```
SECRET = (secret for token creation)
```
- To set up a virtual environment using Poetry, install it via pip:
```bash
pip install poetry
```
- To install the dependencies, run the command:

```bash
poetry install
```
- To start the API, run the command:
```bash
python src/app/main.py
```

</details>

<details><summary><h1>Linter and static type checker Execution Guide</h1></summary>

- To set up a virtual environment using Poetry, install it via pip:
```bash
pip install poetry
```
- To install the dependencies, run the command:

```bash
poetry install
```
- To run the linter, execute the command:

```bash
flake8 src/
```

- To run the static type checker, execute the command:

```bash
mypy src/
```
</details>

<details><summary><h1>Integration Tests Execution Guide</h1></summary>

- To set up a virtual environment using Poetry, install it via pip:
```bash
pip install poetry
```
- To install the dependencies, run the command:

```bash
poetry install
```

- To start the services, execute the command:

```bash
docker compose -f docker-compose-test.yaml up
```
if you use devcontainer skip next step.
- In the file src/config/config.yaml, replace the base_url values for each service with 127.0.0.1:(port from docker-compose-test.yaml)

- To run the integration tests, execute the command:

```bash
pytest src/tests/integration
```

</details>

<details><summary><h1>Manifest Application Guide</h1></summary>

- To load Kubernetes manifests for each file in the /kuber/ folder, run the following command:

```bash
kubectl apply -f ./kuber/<filename>.yaml
```
</details>

<details><summary><h1>Running the Application in Kubernetes using Helm</h1></summary>

- Run the following command:

```bash
helm install <prefix> ./api-gateway-chart
```
</details>
