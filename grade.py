#Grader called by pyxserver_wsgi.py
#Loads a grader file, which is a dict containing the prompt of the question,
#a feature extractor object, and a trained model.
#Extracts features and runs trained model on the submission to produce a final score.
#Correctness determined by ratio of score to max possible score.
#Requires aspell to be installed and added to the path.

import sys
import pickle
import os
import numpy
import logging
from statsd import statsd

base_path = os.path.dirname(__file__)
sys.path.append(base_path)

from essay_set import EssaySet
import util_functions

#Imports needed to unpickle grader data
import feature_extractor
import sklearn.ensemble

log = logging.getLogger(__name__)

TEMPORARY_WANTS_CONFIG=True

@statsd.timed('open_ended_assessment.machine_learning.grader.time')
def grade(grader_path,grader_config,submission,sandbox=None):

    results = {'errors': [],'tests': [],'score': 0, 'feedback' : "", 'success' : False}

    has_error=False

    #Try to find and load the model file

    try:
        grader_data=pickle.load(file(grader_path,"r"))
    except:
        results['errors'].append("Could not find a valid model file.")
        has_error=True
    grader_set=EssaySet(type="test")

    #Try to add essays to essay set object
    try:
        grader_set.add_essay(str(submission),0)
        grader_set.update_prompt(str(grader_data['prompt']))
    except:
        results['errors'].append("Essay could not be added to essay set:{0}".format(submission))
        has_error=True

    #Try to extract features from submission and assign score via the model
    try:
        grader_feats=grader_data['extractor'].gen_feats(grader_set)
        feedback=grader_data['extractor'].gen_feedback(grader_set,grader_feats)[0]
        results['score']=int(grader_data['model'].predict(grader_feats)[0])
    except :
        results['errors'].append("Could not extract features and score essay.")
        has_error=True

    if not has_error:

        if(len(feedback['prompt_overlap'])>4):
            results['score']=0
            results['correct']=False

        results['success']=True

        #Generate short form output--number of problem areas identified in feedback
        problem_areas=0
        for tag in feedback:
            if tag is not 'markup_text':
                problem_areas+=len(feedback[tag])>5

        #Add feedback to results
        results['feedback']={
            'topicality' : feedback['topicality'],
            'prompt-overlap' : feedback['prompt_overlap'],
            'spelling' : feedback['spelling'],
            'grammar' : feedback['grammar'],
            'markup-text' : feedback['markup_text'],
        }

    else:
        #If error, success is False.
        results['success']=False

    #Count number of successful/unsuccessful gradings
    statsd.increment("open_ended_assessment.machine_learning.grader_count",
        tags=["success:{0}".format(results['success'])])

    return results



    
