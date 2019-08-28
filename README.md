# SpidAR

This is a web crawler which will start digging the web gathering web pages.

# How to use

`import spidar`

`crawler = Spidar('https://wikipedia.org')`

`res = crawler.crawl()`

The response will be  a list of object, each one representing a different web page formatted in the following way:

```json
{
  "content": "string", // visible text of the page
  "language": "string", // language extract from the response header
  "url": "string", //url of the page
  "html": "string" // html raw of the response of the page
}
```

## Options

You can set several options for the crawler in the initializer:

| Key   | Default value | Description
|---    |---    |---
|`limit_pages_counter`    |1  |Set the maximum amount of pages to crawl. If this value is less than 1 it will never stop, use it very carefully!!
|`allow_external_link_crawling` | False | Specify if the crawler should crawls also web pages of different domain names from the starting url
|`user_agent`   | Spidar/<version>  | User agent to use in the web requests
|`storage`  | False | Persist the crawling data on files under the directory *data*, see next section for more info
|`debug`    | False | Print information for debug
|`meta` | {}    | Object which will be persisted along the crawled page, only if `storage` is True
|`selenium_chrome_driver`|None  | path to the chromedrivre for selenium, if specified the page will be crawled with selenium

### Storage

This will generate 2 directory Under the folder *data*: *sources* and *infos*. Each one of the two directory will have a folder for each *domain name* crawled.
Inside the *domain name* folder you will find one file for each web page crawled.

For **sources** directory the final page will be an html file.

For **infos** directory the final file will be a json with the following structure:

```json
{
  "content": "string", // visible text of the page
  "language": "string", // language extract from the response header
  "url": "string", //url of the page
  "html": "string", // html raw of the response of the page
  "domain_name": "string", // domain name parsed
  "meta": "object" // object set in the initializer 
}
``` 

# Why

SpidAR is a mix of names, it is not a typo! This is a spider (crawler) and I'm Antonio Romano, mixed up will be SpidAR!! =D