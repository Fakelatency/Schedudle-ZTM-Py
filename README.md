ZTM WARSZAWA SCHEDULE - Program created for showing ZTM schedule for specified stop and line. 

Usage in secondary branch: Pick line -> Pick direction -> Show stops -> Pick stop -> Show timetable for that stop

In order to start: 
1. Create an account here and get your API KEY: https://api.um.warszawa.pl
2. Create .env in your root dir and paste this line with proper key:  "API_KEY=enter_key_here"
3. Run script.py ( It will download a database of tram/bus/metro stops in the capital city of Poland )
4. Run indexLines.py ( It will make an indexed file and create routes for the program so it won't bomb the api with many many calls, process will take ~ 1 hour )
5. Run main.py and follow the instructions in the console.

Project is using "https://github.com/radekwielonski/warsaw-data-api" data wrapper for simplicity. 





