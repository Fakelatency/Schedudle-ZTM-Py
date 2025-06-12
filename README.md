ZTM WARSZAWA SCHEDULE - Program created for showing ZTM schedule for specified stop and line. 

Usage in main branch: Pick stop -> Pick line -> Show timetable for the line

IN ORDER TO PICK THE TRAM/BUS LINE FIRST CHANGE THE BRANCH TO SECONDARY AND FOLLOW THE README.

In order to start: 
1. Create an account here and get your API KEY: https://api.um.warszawa.pl
2. Create .env in your root dir and paste this line with proper key:  "API_KEY=enter_key_here"
3. Run script.py ( It will download a database of tram/bus/metro stops in the capital city of Poland )
4. Run main.py and follow the instructions in the console.

Project is using "https://github.com/radekwielonski/warsaw-data-api" data wrapper for simplicity. 





