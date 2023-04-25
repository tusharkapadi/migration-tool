# migration-tool

Migration Tool

This migration tool allows to export and import different Sysdig resource. Current version supports only Dashboard export & import but will have more resources added in the future.

This tool is written in Python3.

### Pre-Req

1. Make sure python3 with required libraries is installed.
2. Get Sysdig Monitor API Token (Look at next slide on how to get Sysdig Monitor API Token)

### Setup Env variables

The script requires to have 2 env variables.

| Env Var Name  | Description                | Sample Values | Note |
| ------------- | -------------------------- | --------------- | ---- |
| SYSDIG_ENDPOINT_URL | End point url for Sysdig backend  | West - <https://us2.app.sysdig.com>, East - <https://secure.sysdig.com> | Do not include trailing "/"
| SYSDIG_API_TOKEN | API Token to access Sysdig resource | look at pre-req | |

Set above 2 environment variables before testing out the script

### How to get Sysdig Monitor API Token

1. Login to your Sysdig UI
2. Click on your Initial Icon at the bottom left
3. Go to Settings
4. Go to User Profile
5. Copy Sysdig Monitor API Token

### Invoke the script

```
python3 sysdig_migrate.py <operation> <resource> <options>
```

| Option | Description | Required/Optional | Possible Value(s) |
| ------ | ----------------- | ----------- | ----------------- |
| \<operation> | Operation you want Sysdig migration tool to perform | required | export or import |
| \<resource> | Resource you want Sysdig migration tool to export or import | required | dashboard |
| \<options> | Options required to support different operation and/or resource | required | see tables below |

### Export Dashboard Options

```
python3 sysdig_migrate.py export dashboard <options>
```

| Option | Description | Required/Optional | Possible Value(s) | Default Value |
| ------ | ----------------- | ----------- | ----------------- | ------------- |
| --all | exports all dashbaords for given token has access to | optional |  -all | |
| --ids | exports dashbaords for given ids. It is a comma separated list | optional | --ids="1234,2323,4332" | |
| --names | exports dashboards for given names. It is a comman separated list | optional | --names="SQL Troubleshooting,Workload CPUs"  | |
| --output_folder | exports all dashbaords in specified folder. This can be relative or absolute path. Make sure to have trailing '/' in the end. | optional | --output_folder="./json/" or --output_folder="/home/dashboards/" | --output_folder="./json/" |

### Import Dashboard Options

```
python3 sysdig_migrate.py import dashboard <options>
```

| Option | Description | Required/Optional | Possible Value(s) | Default Value |
| ------ | ----------------- | ----------- | ----------------- | ------------- |
| --input_folder | reads all json files from this folder to import into Sysdig. This can be relative or absolute path. Make sure to have trailing '/' in the end. | required | --input_folder="./json/" or --input_folder="/home/dashboards/" |  |
| --plan | prints plan (like Terraform plan) to show you how many dashboards will be created vs updated. User needs to enter 'yes' to continue import process | optional |  | --plan |
| --yes | can be used with --plan to explicitly apply 'yes'. User will not be asked to confirm the plan. | optional | --yes | |

### Common Options

| Option | Description | Required/Optional | Possible Value(s) | Default Value |
| ------ | ----------------- | ----------- | ----------------- | ------------- |
| --log_level | sets the log level for the execution. It is case insensitive | optional | debug, info, error, critical <br> --log_level=debug | --log_level=info |
| --log_folder | creates logs in this folder | optional | any relative or absolute path | --log_folder="./logs/" |

### Export Examples

#### Export all dashboards to <curr dir>/json folder

```
python3 export dashboard --all
```

#### Export all dashboards to /home/dashboards folder

```
python3 export dashboard --all --output_folder="/home/dashboards/"
```

#### Export dashboards based on dashboard ids 3423, 4322, 4343 and 3211 and export them to <curr dir>/json folder

```
python3 export dashboard --ids="3423,4322,4343,3211"
```

#### Export dashboards based on dashboard names 'SQL Troubleshooting' and 'Workload CPUs' export them to /home/dashboards folder

```
python3 export dashboard --names="SQL Troubleshooting,Workload CPUs" --output_folder="/home/dashboards/"
```

### import Examples

#### Import all the dashbaords from <curr dir>/json folders without seeing or approving any plans

```
python3 import dashboard --input_folder="./json/"
```

#### Import all the dashboards from /home/dashboards folder after seeing and approving the plan

```
python3 import dashboard --input_folder="/home/dashboards/" --plan
```

#### Import all the dashboards from /home/dashboards folder with plan info printed but without user needs to manually approve it

```
python3 import dashboard --input_folder="/home/dashboards/" --plan --yes
```

### Common Examples

#### Set the log level to debug

```
python3 import dashboard --input_folder="/home/dashboards/" --plan --log_level=debug
```

#### Set the log folder to /home/dashboards/logs

```
python3 export dashboard --output_folder="/home/dashboards/" --log_folder="/home/dashboards/logs/"
```

### Docker

There is an experimental docker image that can be built and used to run the migration tool.  The docker image is built using the Dockerfile in the root of this repository.  The docker image is built using the following command:

```
docker build -t sysdig-dashboard-migration:latest .
```

The docker image can be run using the following command to export dashboards:

```
docker run --rm \
  -e SYSDIG_ENDPOINT_URL=<https://app.sysdigcloud.com> \
  -e SYSDIG_API_TOKEN=xxxxxxxxxxxxx \
  -v "$(pwd)/json:/app/json" \
  sysdig-dashboard-migration:latest export dashboards --all
```

The docker image can be run using the following command to import dashboards:

```
docker run --rm \
  -e SYSDIG_ENDPOINT_URL=<https://app.sysdigcloud.com> \
  -e SYSDIG_API_TOKEN=xxxxxxxxxxxxx \
  -v "$(pwd)/json:/app/json" \
  sysdig-dashboard-migration:latest import dashboards --input_folder="./json/"
```

### License Note

Notwithstanding anything that may be contained to the contrary in your agreement(s) with Sysdig, Sysdig provides no support, no updates, and no warranty or guarantee of any kind with respect to these script(s), including as to their functionality or their ability to work in your environment(s).  Sysdig disclaims all liability and responsibility with respect to any use of these scripts
