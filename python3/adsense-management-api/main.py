#!/usr/bin/python

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient import discovery
from datetime import datetime , timedelta
import json
import os
import sys

def out_json(output, sys_number=1):
	print(json.dumps(output, indent=4))
	sys.exit(sys_number)

CLIENT_SECRETS_FILE = 'client_secrets.json'
CREDENTIALS_FILE = 'adsense.dat'
ALWAYS_REQUIRE_AUTHENTICATION = False
SCOPES = ['https://www.googleapis.com/auth/adsense.readonly']

# https://github.com/googleads/googleads-adsense-examples/tree/master/v2/python

credentials = None
if os.path.isfile(CREDENTIALS_FILE):
	credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE)
else:
	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
	credentials = flow.run_console()
	with open(CREDENTIALS_FILE, 'w') as credentials_file:
		credentials_json = credentials.to_json()
		if isinstance(credentials_json, str):
			credentials_json = json.loads(credentials_json)
		json.dump(credentials_json, credentials_file)

days_diff = 3
startDate = { 
	'year': datetime.strftime(datetime.now()-timedelta(days=days_diff), '%Y'),
	'month': datetime.strftime(datetime.now()-timedelta(days=days_diff), '%m'),
	'day': datetime.strftime(datetime.now()-timedelta(days=days_diff), '%d'),
}

endDate = {
	'year': datetime.strftime(datetime.now(), '%Y'),
	'month': datetime.strftime(datetime.now(), '%m'),
	'day': datetime.strftime(datetime.now(), '%d'),
}

output = {
	'status': False,
	'error': None,
	'data': None,
}

if credentials is None:
	output['error'] = 'credentials is empty';
	out_json(output)

with discovery.build('adsense', 'v2', credentials = credentials) as service:
	account_id = None

	response = service.accounts().list().execute()
	if len(response['accounts']) == 1:
		account_id = response['accounts'][0]['name']
	else:
		output['error'] = 'mutiple accounts';
		out_json(output)

	if account_id is None:
		output['error'] = 'no account_id';
		out_json(output)

	output['data'] = {
		'account_id' : account_id, 'startDate': startDate, 'endDate': endDate, 
		'metrics' : [ 
			'PAGE_VIEWS', 
			'AD_REQUESTS', 
			'AD_REQUESTS_COVERAGE',
			'CLICKS', 
			'COST_PER_CLICK',
			'AD_REQUESTS_CTR', 
			'AD_REQUESTS_RPM',
			'ESTIMATED_EARNINGS',
		],
		'dimensions': [
			'DATE',
		],
		'result': [], 
	}

	# https://developers.google.com/adsense/management/reference/rest/v2/accounts.reports/generate
	result = service.accounts().reports().generate(
		account=account_id,
		dateRange='CUSTOM',
		startDate_year=startDate['year'],
		startDate_month=startDate['month'],
		startDate_day=startDate['day'],
		endDate_year=endDate['year'],
		endDate_month=endDate['month'],
		endDate_day=endDate['day'],
		metrics=output['data']['metrics'],
		dimensions=output['data']['dimensions'],
		currencyCode="USD",
		reportingTimeZone="ACCOUNT_TIME_ZONE",
	).execute()

	if 'rows' in result:
		for row in result['rows']:
			item = {}
			dimensions_number = len(output['data']['dimensions'])
			metrics_number = len(output['data']['metrics'])
			for i in range(dimensions_number):
				item[output['data']['dimensions'][i]] = row['cells'][i]['value']	

			for i in range(metrics_number):
				item[output['data']['metrics'][i]] = row['cells'][i+dimensions_number]['value']	

			output['data']['result'].append(item)

	output['status'] = len(output['data']['result']) > 0

	out_json(output, sys_number=0)
