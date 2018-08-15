# commute-times
Simple python script to log time in traffic for your commute in Google sheets. Requires access to Google Cloud `Directions API`, `Google Sheets API`, and `Google Drive API`.

## How it works
The script first queries the Google directions API for the time in traffic between your `home` and `work` addresses via POST request. The script then opens the Google spreadsheet which houses your commute time logs, finds the appropriate week and logs the time in the correct cell based on launch time. The script is designed to be launched by a cronjob, grabbing the current time at the beginning of the script and using it to log duration in the appropriate time cell.

## Running the script
### Ensure there is a config.json file in root directory
This json file provides the config & credentials to run the commute-times script. Google Drive API access credential and Google Maps API are required in order for the script to function.

- drive_api_creds: name of google drive api credential json file (also in root directory)
- maps_api_key: google maps API key
- home: your home address
- work: your work address

```
# sample config.json file
{
  "drive_api_creds": "MyGoogleCloudProject-8gs0ff8f73ca.json",
  "maps_api_key" : "FhaAWLwdAjjfwl-ChdwdAdhslfCkl",
  "home" : "123 Fake St, Springfield, MO 65619",
  "work" :  "1 Hacker Way, Menlo Park, CA 94025"
}
```

### Google Sheet setup
The script currently relies on a google spreadsheet that already exists in your Google Drive. The Google spreadsheet for tracking commute times contains a TEMPLATE sheet that is duplicated at the beginning of every week and labeled with the appropriate week number. Gspread does not have a native duplication method, so gspreadHelper copies the template sheet without formatting. An example spreadsheet can be found [here](https://docs.google.com/spreadsheets/d/1MyhkXr0rVp1Qruqd1HE54minmD_oF1dZXLs9XBvYrpA/edit?usp=sharing).

### Setup script automation
To track traffic times at regular intervals I setup a cronjob on a local Linux machine to run during commute hours. I used a network connected Beaglebone to perform this task, but any network connected Linux device with python could perform this job. The crontab entries I use are below:
```
[Cronjob to be added]
```

## Google Cloud API Quotas & Rate Limiting
The script's current design utilizes around 6 Directions API requests per hour. The Google Sheets API hit rate is higher due to underlying Gspread code, but no quota for Sheets API helps with this.

Overall rate limiting is provided by tenacity in the GspreadHelper class.
The retry method used by the GspreadHelper class is a simple evenly spaced
time retry in case any of the errors encountered when reading or writing the Google
Sheet.

## Future Additions
- Better logging
- Unit tests, code cov, CI/CD
- Utilize Google Directions python lib
- Automatically create cronjob entries based on template setup
- Automatically copy sheet formatting and graphs from template
