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
        "account_id": "accounts/pub-###########",
        "startDate": {
            "year": "2021",
            "month": "10",
            "day": "23"
        },
        "endDate": {
            "year": "2021",
            "month": "10",
            "day": "26"
        },
        "metrics": [
            "ESTIMATED_EARNINGS"
        ],
        "dimensions": [
            "DATE"
        ],
        "result": [
            {
                "DATE": "20211023",
                "ESTIMATED_EARNINGS": ##.##
            },
            {
                "DATE": "20211024",
                "ESTIMATED_EARNINGS": ##.##
            },
            {
                "DATE": "20211025",
                "ESTIMATED_EARNINGS": ##.##
            },
            {
                "DATE": "20211026",
                "ESTIMATED_EARNINGS": ##.##
            }
        ]
    }
}
```
