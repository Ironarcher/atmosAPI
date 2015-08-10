import atmoslog1_1
import random

logger = atmoslog1_1.Logger("Nz9yp8Q7gnRNaTpZZHuD")
for i in range(500):
	logger.log("log2", round(random.random()*10, 1))

print('finishedadding')

logger.commitLogsIntoDB()
print("done")