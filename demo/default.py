import logging.config
import pworm
# import pworm.server 

logging.config.fileConfig('logger.conf')
pworm.lookup('./demo/routes')

pworm.server.resourcePath = "./demo/routes"
pworm.test()
# pworm.run()