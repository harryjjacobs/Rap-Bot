#write a rap song with tweets yo
#runs once

import tweepy
from random import randint
import time
import csv
import json
import urllib2
import re

MAXLINELENGTH = 30 #chars

lastWordOfPreviousLine = ""
skipB = False

def tweet_me(tweetId):
    try:
        api.retweet(tweetId)
        print("tweeted!")
        skipB = False #succeeded so find a line to rhyme with it
    except: #happens if we've already RTed this tweet
        skipB = True #the a tweet failed so don't find anything to rhyme with it
        return "failed"
    
def remove_weird_chars(text): #returns only ascii chars in string
    return ''.join([i if ord(i) < 128 else '' for i in text])

def grab_a_word(): #returns a random word that occurs in well known rap songs
    wordsList = []
    with open('commonwords.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            wordsList.append(row[0]);
        return wordsList[randint(0, len(wordsList) -1)]

def get_rhyming_words(word):
    result = urllib2.urlopen("http://rhymebrain.com/talk?function=getRhymes&word=" + word).read()
    j = json.loads(result)
    return j
    
def line_a():
    global lastWordOfPreviousLine
    word = grab_a_word()
    results = api.search(q=word, count=100, lang='en')
    for result in results:
        text = remove_weird_chars(result.text)
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text) #check if it contains a url
        ats = re.findall('@.+', text) #check if it contains an @...
        hashtags = re.findall('#.+', text) #check if it contains an @...
        if urls == [] and ats == [] and hashtags == [] and len(result.text) < MAXLINELENGTH:
            split = text.split( )
            length = len(split)
            if split[length-1].isalpha(): #make sure the last word is actually a word of some kind...
                lastWordOfPreviousLine = split[length-1]
                print text
                if tweet_me(result.id) != "failed":
                    return
            
def line_b(): #follow up line that rhymes with line_a
    global lastWordOfPreviousLine
    if lastWordOfPreviousLine != "":
        rhymes = get_rhyming_words(lastWordOfPreviousLine) #get last word of sentence and find rhyme
        for word in rhymes:
            results = api.search(q=word["word"], count=100, lang='en')
            for result in results:
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', result.text)
                ats = re.findall('@.+', result.text)
                lastWord = result.text.split( )[len(result.text.split( )) - 1].lower()
                if urls == [] and ats == [] and lastWord == word["word"].lower() and len(result.text) < MAXLINELENGTH: #check to see if last word is the one that we've found in the tweet
                    print(result.text)
                    if tweet_me(result.id) != "failed":
                        return

#set up
auth = tweepy.OAuthHandler('', '')
auth.set_access_token('', '')

api = tweepy.API(auth)

print("starting...")
time.sleep(1)

line_a()
if skipB == False:
    line_b()
    
print("done...")
time.sleep(180) #every 3 minutes
