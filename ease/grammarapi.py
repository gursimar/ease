import pandas as pd
import requests, json

def textGearGramamr(essayText):
    essayText.replace(' ', '+')
    payload = {'text':essayText, 'key':'DEMO_KEY'}
    r = requests.post("https://api.textgears.com/check.php", data=payload)
    return r


if __name__ == "__main__":
    #data_filename = 'suheb_ds.csv'  # numpy array with first column being the essays and second their scores
    data_filename = 'essays_ps.csv'  # numpy array with first column being the essays and second their scores
    data = pd.read_csv(data_filename)
    scores = []
    for index, essay in data.iterrows():
        essayText = essay['essay']
        try:
            r = textGearGramamr(essayText)
            r = json.loads(r.text)
            errors = r['errors']
            score = r['score']
            print score
            scores.append(score)
        except:
            scores.append(-1)
            print '-1'
    scores = pd.DataFrame(scores,columns=['GraScore'])
    data.append(scores)
    pass
