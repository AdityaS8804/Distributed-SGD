# Distributed Stochastic Gradient Descent

### Steps to run this:  

- cd to the current directory
- have `docker` and `docker-compose` installed
```bash
docker build -t hogwild-sgd:latest .
```
```bash
docker-compose up --scale worker=4
```
- Ctrl+C will stop the nodes
