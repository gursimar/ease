from create import create
from grade import grade
import sys
import pickle
import numpy as np
import csv
import pandas as pd
from sklearn.cross_validation import train_test_split

# change the prompt according to essay data set
prompt = "In general, people are living longer now. Discuss the causes of this phenomenon. Use specific reasons and details to develop your essay.";
#data_filename = sys.argv[1] # numpy array with first column being the essays and second their scores
#result_filename = sys.argv[2] # csv file containing the result from grading
data_filename = 'suheb_ds.csv' # numpy array with first column being the essays and second their scores
result_filename = 'result.csv' # csv file containing the result from grading

#USAGE: python create_model.py <data_inputfile> <trainset_outputfile> <testset_outputfile> <model_outputfile>

if __name__ == "__main__":
	# get traning data and split in train test sets
	#with open(data_filename, "r") as data_file:
		#print data_file
		#exit()
		#data = pickle.load(data_file)
	data = pd.read_csv(data_filename, )
	#print data
	print "Data size " + str(len(data))
	train, test = train_test_split(data, train_size = 0.7, test_size = 0.3)
	print "Train set size " + str(len(train)), "Test set " + str(len(test))

	# dump the train test sets
	with open("train.p", "w") as trainset_file:
		pickle.dump(train, trainset_file)
	with open("test.p", "w") as testset_file:
		pickle.dump(test, testset_file)

	# train ml model
	tr = np.array(train)
	texts = tr[:, 0]
	scores = map(int, tr[:, 1])
	# train ml model
	model = create(texts, scores, prompt, True)

	# dump the model
	with open("model.p", "w") as model_file:
		pickle.dump(model, model_file)

	# create grader data
	grader_data = {'model': model['classifier'], 'extractor': model['feature_ext'], 'prompt': prompt, 'algorithm': model['algorithm']}
	results = []
	# grade each item in test set using model created above
	for index, row in test.iterrows():
		result = grade(grader_data, row['essay'])
		result['essayText'] = row['essay']
		result['myscore'] = row['score']
		#result['etsScore'] = item[2]
		#result['amcatId'] = item[3]
		results.append(result)
		#print result
	
	# write result to csv file
	with open(result_filename, 'w') as result_file:
	    fieldnames = results[0].keys()
	    fieldnames.append('correct')
	    print fieldnames
	    writer = csv.DictWriter(result_file, fieldnames=fieldnames)
	    writer.writeheader()
	    writer.writerows(results)

