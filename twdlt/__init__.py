"""
    TWDLT
    Copyright (C) 2013 Sam Rudge

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from config import Config, ConfigException
from optparse import OptionParser
import logging
import sys
from time import sleep, time
import twitter
import pprint
import re

class dltr(object):
    """
    Delete all the tweets in an account sent before a specified date
    
    @cvar   config:     Application configuration
    @cvar   toDelete:   List of tweet IDs to delete
    @cvar   perPage:    Number of results to return perk page of GetUserTimeline
    @cvar   maxPage:    Maximum number of pages for GetUserTimeline
    @cvar   useLimit:   Amount of total hourly API hits twdlt can use (as a %)
    @cvar   callsMade:  Number of calls to rateWait
    @cvar   rateLimit:  Store rate limit information
    """
    
    config = {}
    toDelete = []
    callsMade = 0
    rateLimit = None
    
    def __init__(self,configFile=None):
        """
        Load the config and prepare everything
        
        @arg    configFile:     Path to config file
        @type   configFile:     str
        """
        
        self.config = Config(configFile)
    
    def api(self):
        """
        Connect to Twitter API
        """
        
        if not hasattr(self, 't'):
            logging.debug("Creating twitter.Api instance")
            
            self.t = twitter.Api(
                consumer_key=self.config['consumerKey'],
                consumer_secret=self.config['consumerSecret'],
                access_token_key=self.config['accessToken'],
                access_token_secret=self.config['accessSecret'],
                base_url='https://api.twitter.com/1.1',
                cache=None
            )
            
            logging.debug("Testing credentials against Twitter")
            try:
                self.t.VerifyCredentials()
            except twitter.TwitterError:
                raise ConfigException("Could not verify credentials, check your API keys are correct")
            
            logging.debug("OK")
    
    def rateWait(self, ty):
        """
        Check the rate limit status, if there are not enough requests left to make this call within the bounds of `self.useLimit`
        """
        
        if self.callsMade%20 or not self.rateLimit:
            logging.debug("Getting rate limit from Twitter")
            url  = '%s/application/rate_limit_status.json' % self.t.base_url
            json = self.t._FetchUrl(url, no_cache=True)
            data = self.t._ParseAndCheckTwitter(json)
            
            self.rateLimit = data['resources']
        
        if ty == 'find':
            remaining = self.rateLimit['statuses']['/statuses/user_timeline']['remaining']
            limit = self.rateLimit['statuses']['/statuses/user_timeline']['limit']
            reset = self.rateLimit['statuses']['/statuses/user_timeline']['reset']
            self.rateLimit['statuses']['/statuses/user_timeline']['remaining'] -= 1
            
            logging.debug("Rate limit {0} for find".format(remaining))
        elif ty == 'delete':
            remaining = self.rateLimit['statuses']['/statuses/show/:id']['remaining']
            limit = self.rateLimit['statuses']['/statuses/show/:id']['limit']
            reset = self.rateLimit['statuses']['/statuses/show/:id']['reset']
            self.rateLimit['statuses']['/statuses/show/:id']['remaining'] -= 1
            
            logging.debug("Rate limit {0} for delete".format(remaining))
            
        if remaining <= limit-(limit*self.config['useLimit']):
            wait = int(reset-time())+5
            logging.warning("Waiting for {0} seconds until rate limit is back above threshold".format(wait))
            sleep(wait)
            self.rateLimit = None
        
    def run(self):
        """
        Run subfunctions to process tweets
        """
        
        self.toDelete = []
        self.callsMade = 0
        self.rateLimit = None
        
        self.api()
        self.findTweets()
        
        if not self.opts.dry:
            self.deleteTweets()
    
    def findTweets(self):
        """
        Find tweets older than the specified age and add them to the list
        """
        
        logging.debug("Finding old tweets")
        
        if self.config['perPage']*self.config['maxPage'] > 800:
            raise ConfigException("perPage*maxPage is greater than 800, which is greater than the limit of the Twitter status feed")
        
        page = 1
        results = True
        now = time()
        ageSeconds = self.config['age']*60*60
        
        if self.config['atAge']:
            atAgeSeconds = self.config['atAge']*60*60
        else:
            atAgeSeconds = ageSeconds
        
        logging.debug("Deleting tweets older than {0} seconds".format(ageSeconds))
        
        while results:
            logging.debug("Getting page {0} of tweets".format(page))
            
            self.rateWait('find')
            
            tweets = self.t.GetUserTimeline(count=self.config['perPage'],page=page)
            
            if len(tweets) == 0:
                results = False
            
            for tweet in tweets:
                keepExtended = False
                
                tweetText = tweet.text
                
                for url in tweet.urls:
                    tweetText = tweetText.replace(url.url,url.expanded_url)
                
                if tweetText[0] == "@":
                    keepExtended = True
                
                for pattern in self.config['exclude']:
                    if re.search(pattern,tweetText):
                        keepExtended = True
                
                if keepExtended:
                    dlAfter = atAgeSeconds
                else:
                    dlAfter = ageSeconds
                
                logging.debug(tweetText)
                
                if now-tweet.GetCreatedAtInSeconds() > dlAfter:
                    logging.debug("Status {0} is older than {1}, will be deleted".format(tweet.id,ageSeconds))
                    self.toDelete.append(tweet.id)
                else:
                    logging.debug("Status {0} is not older than {1}".format(tweet.id, dlAfter))
            
            page += 1
            
            if page > self.config['maxPage']:
                results = False
    
    def deleteTweets(self):
        """
        Delete the tweets
        """
        
        logging.debug("Deleting {0} tweets".format(len(self.toDelete)))
        
        for tweet in self.toDelete:
            logging.debug("Deleting tweet {0}".format(tweet))
            
            self.rateWait('delete')
            self.t.DestroyStatus(tweet)
        
        logging.debug("All tweets deleted!")

def cli():
    """
    Parse command line options
    """
    
    p = OptionParser(usage="%prog --config /path/to/config.json [options]")
    p.add_option("-c", "--config", dest="configLocation", help="Path to config JSON file", metavar="FILE")
    p.add_option("--cron", dest="cronMode", help="Use CRON mode (run once then exit 0)", action="store_true")
    p.add_option("-v", "--verbose", dest="verbose", help="Verbose/debug output", action="store_true")
    p.add_option("-d", "--dry", dest="dry", help="Dry run (don't delete tweets)", action="store_true")
    
    (opts,args) = p.parse_args()
    
    if opts.verbose or opts.dry:
        logging.basicConfig(
            level=logging.DEBUG
        )
    
    logging.debug("Debug Mode On!")
    
    if opts.dry:
        logging.debug("Dry Mode On!")
    
    if not opts.configLocation:
        p.error("You must specify a valid config file")
        sys.exit(1)
    
    try:
        d = dltr(opts.configLocation)
        d.opts = opts
    
        if opts.cronMode:
            d.run()
            logging.debug("CRON mode so will now exit")
            sys.exit(0)
        else:
            every = int(d.config['every'])*60
            while True:
                start = time()
                
                d.run()
                
                sleepTime = int(every-(time()-start))
                
                if sleepTime > 0:
                    logging.debug("Sleeping for {0} seconds".format(sleepTime))
                    sleep(sleepTime)
                    
    except (IOError, ConfigException) as e:
        p.error(e)
        sys.exit(1)

if __name__ == '__main__':
    cli()