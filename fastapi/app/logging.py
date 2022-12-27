config_str = """
version: 1
formatters:
  simple:
    format: '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: DEBUG
    filters: []
    stream: ext://sys.stdout
loggers:
  uvicorn:
    error:
      propagate: true
root:
  level: DEBUG
  handlers: [console]
  propagate: no
"""

