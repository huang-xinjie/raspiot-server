import logging as log

log.basicConfig(level=log.DEBUG,
                format='%(asctime)s %(levelname)s [pid:%(process)d] [tid:%(thread)d] '
                       '[%(filename)s:%(lineno)d] %(funcName)s %(message)s')
