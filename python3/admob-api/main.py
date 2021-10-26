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
CREDENTIALS_FILE = 'admob.dat'
ALWAYS_REQUIRE_AUTHENTICATION = False
SCOPES = ['https://www.googleapis.com/auth/admob.readonly']

# https://github.com/googleads/googleads-admob-api-samples/blob/master/python/v1/

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

with discovery.build('admob', 'v1', credentials = credentials) as service:
	account_id = None

	response = service.accounts().list().execute()
	if len(response['account']) == 1:
		account_id = response['account'][0]['name']
	else:
		output['error'] = 'mutiple accounts';
		out_json(output)

	if account_id is None:
		output['error'] = 'no account_id';
		out_json(output)

	output['data'] = {
		'account_id' : account_id, 'startDate': startDate, 'endDate': endDate, 
		'metrics' : [ 
			'ESTIMATED_EARNINGS',
		],
		'dimensions': [
			'DATE',
		],
		'result': [], 
	}

	# https://developers.google.com/adsense/management/reference/rest/v2/accounts.reports/generate
	result = service.accounts().networkReport().generate(
		parent=account_id,
		body= {
			'reportSpec': {
				'dateRange' : {
					'startDate': output['data']['startDate'],
					'endDate': output['data']['endDate'],
				},
				'dimensions': output['data']['dimensions'],
				'metrics': output['data']['metrics'],
				'localizationSettings': {
					'currencyCode': 'USD',
					'languageCode': 'en-US',
				},
			},
		},
	).execute()

	for row in result:
		if 'row' in row:
			item = {}
			if 'dimensionValues' in row['row']:
				for k in row['row']['dimensionValues']:
					item[k] = row['row']['dimensionValues'][k]['value']
			if 'metricValues' in row['row']:
				for k in row['row']['metricValues']:
					if 'value' in row['row']['metricValues'][k]:
						item[k] = row['row']['metricValues'][k]['value']
					elif 'microsValue' in row['row']['metricValues'][k]:
						item[k] = float(row['row']['metricValues'][k]['microsValue'])/1000000

			output['data']['result'].append(item)

	output['status'] = len(output['data']['result']) > 0

	out_json(output, sys_number=0)
