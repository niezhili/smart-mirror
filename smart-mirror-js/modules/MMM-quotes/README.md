# MMM-quotes

This is an extension for the [MagicMirror²](https://github.com/MichMich/MagicMirror).  It provides the ability to display inspirational quotes, along with author attribution.

## Installation
1. Navigate into your MagicMirror's `modules` folder and execute `git clone https://github.com/javiergayala/MMM-quotes.git`. A new folder will appear, likely called `MMM-quotes`.  
2. Add the module to the config file.  

## Using the module

To use this module, add it to the modules array in the `config/config.js` file:
````javascript
modules: [
	{
		module: 'MMM-quotes',
		position: 'top_right',	// This can be any of the regions. Best results in left or right regions.
		header: 'Inspirational', // This is optional
		config: {
			// See 'Configuration options' for more information.
			// quotes: [{
			// 	quote: 'To be, or not to be. That is the question',
			// 	author: 'William Shakespeare'
			// }]
		}
	}
]
````

## Configuration options

The following options can be configured:

| Option  | Description  |
|---|---|
| `quotes`  | An array containing Objects for each quote that you want to use.  The Objects are comprised of `quote` and `author` keys.  Populate this in the config file to override the stock quotes.  |


## Contributing Guidelines

Contributions of all kinds are welcome, not only in the form of code but also with regards bug reports and documentation.

Please keep the following in mind:

- **Bug Reports**:  Make sure you're running the latest version. If the issue(s) still persist: please open a clearly documented issue with a clear title.
- **Minor Bug Fixes**: Please send a pull request with a clear explanation of the issue or a link to the issue it solves.
- **Major Bug Fixes**: please discuss your approach in an GitHub issue before you start to alter a big part of the code.
- **New Features**: please please discuss in a GitHub issue before you start to alter a big part of the code. Without discussion upfront, the pull request will not be accepted / merged.

The MIT License (MIT)
=====================

Copyright © 2016 Javier G. Ayala

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the “Software”), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

**The software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.**
