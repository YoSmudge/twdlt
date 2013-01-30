#TWDLT
##Keep your Twitter feed tidy

TWDLT is a simple Python script to automatically delete any tweets older than a certain date. You can set sepreate "expire" times for normal tweets and @replies. The script can be run continuously with something like Supervisord or one time with something like CRONd or Jenkins.

TWDLT uses a JSON configuration file, you need to be able to locate and provide a consumer key, consumer secret and the linked access token and access token secret from Twitter.

#Configuration format

Configuration files are simple JSON files containing the information needed to run the application. Provide the `--config` or `-c` flag to `twdlt` to specify the config file location. There are a number of different options you can provide in the config file

 * **age** - *default: 24* - tweets will be deleted after this many hours
 * **atAge** - @replies will be deleted after this many hours. If not provided `age` is used
 * **perPage** - *default: 150* - number of tweets fetched per page*
 * **maxPage** - *default: 5* - maximum number of pages to fetch*
 * **useLimit** - *default: 0.25* - maximum % of rate limit for a resource that will be used
 * **every** - *default: 60* - how often to check for tweets to delete, in minutes. Not used if running as `--cron`

You **must** also supply

 * consumerKey
 * consumerSecret
 * accessToken
 * accessSecret

containing your Twitter API credentials in order for the application to work.

\* the maximum results that can be returned from Twitter is 800. so perPage multiplied by maxPage should be <= 800

Be aware there are twitter API limits, so if you have a lot of tweets to delete it may take a while. The application will never go over it's specified `useLimit` and will wait until the rate limit resets before continuing.

#Installation

To install the software, download this repository, run `pip install -r requirements.txt` then `python setup.py install`. It's reccomended you install within a virtualenv.

#Running

To run the software execute `twdlt --config=[path to your config file]`

To run in CRON mode execute `twdlt --config=[path to your config file] --cron`

For a list of options run `twdtl --help`

#Licence

This software is licenced as GPL3. See LICENCE.txt for more information