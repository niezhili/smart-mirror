'use strict';
/* global Log, Module, JSON */

/* Magic Mirror
 * Module: Compliments
 *
 * By Michael Teeuw http://michaelteeuw.nl
 * MIT Licensed.
 */

Module.register('MMM-quotes',{

	// Module config defaults.
	defaults: {
		quotes: [
			{
				quote: 'If you can dream it, you can do it.',
      	author: 'Walt Disney'
			},
			{
				quote: 'No matter how slow you go, you are still lapping everybody on the couch.',
				author: 'Unknown'
			},
			{
				quote: 'Don\'t cry because it\'s over. Smile because it happened.',
				author: 'Dr. Seuss'
			},
			{
				quote: 'It\'s kind of fun to do the impossible.',
				author: 'Walt Disney'
			},
			{
				quote: 'A person\'s a person, no matter how small.',
				author: 'Dr. Seuss'
			},
			{
				quote: 'The way to get started is to quit talking and begin doing.',
				author: 'Walt Disney'
			},
			{
				quote: 'I like nonsense; it wakes up the brain cells.',
				author: 'Dr. Seuss'
			},
			{
				quote: 'Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment.',
				author: 'Budha'
			},
			{
				quote: 'What we think, we become.',
				author: 'Budha'
			},
			{
				quote: 'It does not matter how slowly you go as long as you do not stop.',
				author: 'Confucius'
			},
			{
				quote: 'You can not open a book without learning something.',
				author: 'Confucius'
			},
			{
				quote: 'Attitude is a little thing that makes a big difference.',
				author: 'Winston Churchill'
			}
		],
		updateInterval: 30000,
		fadeSpeed: 4000
	},

	// Define required scripts.
	getStyles: function() {
		return ['MMM-quotes.css'];
	},

	// Define start sequence.
	start: function() {
		Log.info('[QUOTES] Starting module: ' + this.name);

		this.lastQuoteIndex = -1;

		// Schedule update timer.
		var self = this;
		setInterval(function() {
			self.updateDom(self.config.fadeSpeed);
		}, this.config.updateInterval);
	},

	/* randomIndex(quotes)
	 * Generate a random index for a list of quotes.
	 *
	 * argument quotes Array<Object> - Array with quotes.
	 *
	 * return Number - Random index.
	 */
	randomIndex: function(quotes) {
		if (quotes.length === 1) {
			return 0;
		}

		var generate = function() {
			return Math.floor(Math.random() * quotes.length);
		};

		var quoteIndex = generate();

		while (quoteIndex === this.lastQuoteIndex) {
			quoteIndex = generate();
		}

		this.lastQuoteIndex = quoteIndex;

		return quoteIndex;
	},

	/* randomQuote()
	 * Retrieve a random quote.
	 *
	 * return quote object - A quote with attribution.
	 */
	randomQuote: function() {
    Log.info('[QUOTES] Entering randomQuote()');
		var index = this.randomIndex(this.config.quotes);
    Log.info('[QUOTES] random index: ' + index.toString());

		return this.config.quotes[index];
	},

	// Override dom generator.
	getDom: function() {
    Log.info('[QUOTES] Entering getDom()');
		var quoteObj = this.randomQuote();

		Log.info('[QUOTES] quoteObj: ' + quoteObj.quote.toString());

		var wrapper = document.createElement('div');
    var quoteWrapper = document.createElement('div');
    var authorWrapper = document.createElement('div');
		quoteWrapper.className = 'quotes medium bright light';
    authorWrapper.className = 'quotes quotes-author thin small bright';

    quoteWrapper.innerHTML = quoteObj.quote;
    authorWrapper.innerHTML = '—' + quoteObj.author;
		wrapper.appendChild(quoteWrapper);
    wrapper.appendChild(authorWrapper);


		return wrapper;
	}

});
