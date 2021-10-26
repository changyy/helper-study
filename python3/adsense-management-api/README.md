# Env

```
$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 18.04.6 LTS
Release:        18.04
Codename:       bionic

$ python3 -V
Python 3.6.9

$ virtualenv -p /usr/bin/python3 venv
$ source venv/bin/activate

$ pip3 install google-api-python-client
$ pip3 install google-auth-oauthlib
```

# Usage

```
$ python3 main.py
{
    "status": true,
    "error": null,
    "data": {
        "account_id": "accounts/pub-XXXXXXXX",
        "startDate": {
            "year": "2021",
            "month": "10",
            "day": "25"
        },
        "endDate": {
            "year": "2021",
            "month": "10",
            "day": "26"
        },
        "metrics": [
            "PAGE_VIEWS",
            "AD_REQUESTS",
            "AD_REQUESTS_COVERAGE",
            "CLICKS",
            "COST_PER_CLICK",
            "AD_REQUESTS_CTR",
            "AD_REQUESTS_RPM",
            "ESTIMATED_EARNINGS"
        ],
        "dimensions": [
            "DATE"
        ],
        "result": [
            {
                "DATE": "2021-10-25",
                "PAGE_VIEWS": "####",
                "AD_REQUESTS": "####",
                "AD_REQUESTS_COVERAGE": "0.99",
                "CLICKS": "##",
                "COST_PER_CLICK": "0.##",
                "AD_REQUESTS_CTR": "0.####",
                "AD_REQUESTS_RPM": "##.##",
                "ESTIMATED_EARNINGS": "##.##"
            },
            {
                "DATE": "2021-10-26",
                "PAGE_VIEWS": "####",
                "AD_REQUESTS": "####",
                "AD_REQUESTS_COVERAGE": "0.99",
                "CLICKS": "##",
                "COST_PER_CLICK": "0.##",
                "AD_REQUESTS_CTR": "0.####",
                "AD_REQUESTS_RPM": "##.##",
                "ESTIMATED_EARNINGS": "##.##"
            }
        ]
    }
}
```
