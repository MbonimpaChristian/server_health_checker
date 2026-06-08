# Server Health Checker

Server Health Checker is a Python script that checks whether a list of servers or service endpoints are up, responding correctly, and performing within an acceptable response time.

## Project Description

The script sends HTTP GET requests to configured service endpoints and checks:

- HTTP status code
- Response time in milliseconds
- JSON body validation
- Slow responses
- Failed services
- Retry attempts
- Optional email alerts

## Features Implemented

- Load servers from `config.json`
- Load servers from `SERVERS` environment variable
- Send HTTP GET requests to service endpoints
- Measure response time in milliseconds
- Mark services as `OK`, `DOWN`, `TIMEOUT`, or `ERROR`
- Validate JSON body for `"status": "ok"`
- Detect slow services over 500ms
- Print clean result lines per service
- Save failed services and print them at the end
- Flexible config loading: environment variable first, then config file
- Organized code into reusable functions
- Run checks in parallel using `ThreadPoolExecutor`
- Retry failed requests before marking them as failed
- Send optional email alerts for failed services

## Project Structure

```text
server-health-checker/
│
├── server_health_checker.py
├── config.json
├── README.md
└── .gitignore
```

## Requirements

Install the required package:

```bash
python -m pip install requests
```

## Configuration Option 1: config.json

Create a `config.json` file:

```json
{
  "servers": [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/json"
  ]
}
```

## Configuration Option 2: Environment Variable

You can also load servers from an environment variable:

```bash
export SERVERS="https://httpbin.org/status/200,https://httpbin.org/status/500"
```

The script checks the environment variable first. If it is not set, it falls back to `config.json`.

To remove the environment variable:

```bash
unset SERVERS
```

## How to Run

```bash
python server_health_checker.py
```

## Example Output

```text
Loaded 4 servers

https://httpbin.org/status/200    — OK (200) — 320ms
https://httpbin.org/json          — OK (200) — 350ms
https://httpbin.org/status/500    — DOWN (500) — 290ms after 3 attempts
https://httpbin.org/delay/2       — OK (200) — 2100ms [slow]

Failed services: https://httpbin.org/status/500
Email alert skipped: email configuration is missing
```

## Email Alert Configuration

Email alerts are optional. The script only sends alerts if these environment variables are configured:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export ALERT_EMAIL_FROM="your_email@gmail.com"
export ALERT_EMAIL_TO="receiver_email@gmail.com"
export ALERT_EMAIL_PASSWORD="your_gmail_app_password"
```

Then run:

```bash
python server_health_checker.py
```

To remove email configuration:

```bash
unset SMTP_SERVER
unset SMTP_PORT
unset ALERT_EMAIL_FROM
unset ALERT_EMAIL_TO
unset ALERT_EMAIL_PASSWORD
```

## Manual Testing Checklist

- [x] Load servers from `config.json`
- [x] Load servers from `SERVERS` environment variable
- [x] Send request to one server
- [x] Return URL and status code
- [x] Measure response time in milliseconds
- [x] Mark `200–299` as `OK`
- [x] Mark `400+` as `DOWN`
- [x] Handle timeout/request errors
- [x] Validate JSON response body
- [x] Detect slow service over 500ms
- [x] Print clean result per service
- [x] Save and print failed services
- [x] Organize code into functions
- [x] Run checks in parallel
- [x] Retry failed requests
- [x] Skip email alert when email config is missing
- [x] Send email alert when email config is provided

## Commands Tested

```bash
python server_health_checker.py
```

```bash
export SERVERS="https://httpbin.org/status/200,https://httpbin.org/status/500"
python server_health_checker.py
unset SERVERS
```

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export ALERT_EMAIL_FROM="your_email@gmail.com"
export ALERT_EMAIL_TO="receiver_email@gmail.com"
export ALERT_EMAIL_PASSWORD="your_gmail_app_password"
python server_health_checker.py
```

## Main Functions

```text
load_servers()
check_server(url)
check_all_servers(servers)
format_result(result)
send_email_alert(failed_services)
```

## Peer Review Request

Please review:

- Code structure
- Error handling
- Retry logic
- Parallel execution
- Config loading
- Email alert implementation
- Output formatting