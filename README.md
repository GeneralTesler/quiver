# Quiver - Hunter.io Faceprinter

Searches [Hunter.io](https://hunter.io/) for emails from a supplied domain. You can provide either an API key or a file containing a list of keys. If a list is supplied, the script will exhaust each key in order. Additionally, you can set the free tier flag to prevent the script from running if the target organization requires more queries than the free tier allows.

*Note: this is still a somewhat beta release and requires some additional testing*

## Install

```
pip install -r requirements
```

## Usage

```
usage: quiver.py [-h] -t TARGET [-a APIKEY] [-l APILIST] -o OUTPUTFILE [-f]
                 [-p]

optional arguments:
  -h, --help     show this help message and exit
  -t TARGET      target domain
  -a APIKEY      Hunter.io API key
  -l APILIST     file of API keys
  -o OUTPUTFILE  Output file location
  -f, --free     Enable free tier limit restrictions
  -p, --print    print a text table of the results

```

**Example**

Search for example.com emails using a list of keys and print the table of emails to the terminal

```
python quiver.py -t example.com -l keys.txt -o output.txt -p

 /\___/\  
|       | Quiver
 \     /  
  |___|   @2xxeformyshirt
 

[+] Hunting for users associated with example.com
[+] Results written to output.txt

[+] Printing results:
First Name    Last Name    Email                            
Joe           Shmoe        joe.shmoe@example.com
<...>

[+] Retrieving new staminas:
Key                                        Stamina
abcdefghijklmnopqrstuvwxyz                 100 
<...>
```

## Changelog

8/14/2018 - Initial release

## To-dos

- Better error handling
