# bb8

## Install

```
pip install bb8 --upgrade
```

## Usage

Create file `bb8.yml` in your project folder

Sample `bb8.yml`:

```yaml
up:
  # Start environment
  - docker-compose up
  # Start React Hot Reload
  - npm start
  # Start API server
  - sleep 3 && ./server.sh
  # Run monitor files
  - bb8 mon
mon:
  # Generate model when schema.yml changed
  - paths:
      - data/postgresql/schema.yml
    cmds:
      # Generate model
      - export PYTHONPATH=`pwd` && ./worker/bin/python coffee_server/generator/model.py
      - export PYTHONPATH=`pwd` && ./worker/bin/python coffee_server/generator/react.py
      - export PYTHONPATH=`pwd` && ./worker/bin/python coffee_server/generator/sql.py
  # Generate sample data when sample.yml changed
  - paths:
      - data/postgresql/sample.yml
    cmds:
      - export PYTHONPATH=`pwd` && ./worker/bin/python coffee_server/generator/sample.py
```

Run

```
bb8 up
```
