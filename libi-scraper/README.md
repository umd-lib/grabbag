To successfully run the script, you need to go through the following steps:

### Libi-Vagrant
- Download [libi-vagrant](https://github.com/umd-lib/libi)
- Start up the vagrant under 'vm' folder: `$ vagrant up `
- Configure the permissions, go over steps listed in the ticket [LIBWEB-4065](https://issues.umd.edu/browse/LIBWEB-4065) 

### Python3 Environment
- Make sure you have **Python3** environment and **pip3**, then install the required packages

```bash
$ pip3 install -r requirements.txt
```

### Input
- Prepare the input files **'nid\_attachments'** and **'node\_urls'** into the folder **'./INPUT/'**, check the *.sample* for references, MAKE SURE THERE ARE NO NEW LINES AT THE END OF INPUT FILES!
- Reference ticket [LIBWEB-4066](https://issues.umd.edu/browse/LIBWEB-4066)

### The Scraper
- Start the script by `python3 scraper.py`
- The result will be generated in `OUTPUT/` folder
- The log file will be generated into `LOG/script.log`

Check ticket [LIBWEB-4067](https://issues.umd.edu/browse/LIBWEB-4067) for delivery destination
