# What is this
This is the code that is running on SWARFARM that imports and exports data from user profiles, located at [http://swarfarm.com/data/](http://swarfarm.com/data/)

# Why is this
There are understandable security concerns uploading your network capture files to a website, so I wanted to publish the code so someone can ease their worries about what I do with it. I am also open to pull requests with new export formats. 

# Explaining the code
This code is not exactly something you can download and run right now. I'll evolve it over time to be a properly packaged app that can run by itself. Right now I just wanted to get it up on Github when releasing the import pcap ability.

The data models are from another Django app that contains the bulk of the SWARFARM website, which is not yet open source. I've copied them into swarfarm_models.py. Anywhere you see 'from herders.models import <models>' they can be referenced in swarfarm_models.py