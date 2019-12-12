# Health Insurance Database System

## I. Authors
Liangbin Zhu, Yujue Wang

## II. Dataset
Data Source: [The Centers for Medicare & Medicaid Services (CMS) ](https://www.cms.gov/cciio/resources/data-resources/marketplace-puf)
>[Benefits and Cost Sharing Data](https://www.cms.gov/CCIIO/Resources/Data-Resources/Downloads/BenefitsCostSharing-DataDictionary-20.pdf)\
>[Rate Data](https://www.cms.gov/CCIIO/Resources/Data-Resources/Downloads/Rate-DataDictionary-PY20.pdf)\
>[Plan Attributes Data](https://www.cms.gov/CCIIO/Resources/Data-Resources/Downloads/PlanAttributes-DataDictionary-PY20.pdf)\
>[Business Rules Data](https://www.cms.gov/CCIIO/Resources/Data-Resources/Downloads/BusinessRules-DataDictionary-PY20.pdf)

## III. Setup Guide
#### Deployment Environment
- Operating System: Linux (centos 7.7.1908)
- Platform: Microsoft Azure
- Container: Docker PostgreSQL & MongoDB
```dockerfile
$ docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
$ docker run --name some-mongo -d mongo:tag
```
#### Database
- PostgreSQL
- MongoDB

#### Database Connection Configuration
```python
$ constants.py

Const.HOST_NAME = "172.17.0.2" # Container IP address
Const.DB_NAME = "insurance" # Database Name
Const.DB_USER = "manager" # Database Role Name
Const.MONGO_HOST = "172.17.0.3" # Container IP address
Const.MONGO_PORT = "27017" # Port Number
```
#### Programming Language
- Python (3.x)

#### Package
- psycopg2
- tabulate
- csv
- pymongo
```python
pip3 install <package-name>
```

#### File Structure
1. schema.sql
2. load_data.py
3. constants.py
4. enumeration.py
5. utils.py
6. application.py
7. database.py

## IV. Data Loading
#### Working Directory
- Datasets: ./2020-dataset/*.csv
- Python Files: 
    >./constants.py\
    ./enumeration.py \
    ./load_data.py


#### Running
```postgresql
psql -U manager insurance < schema.sql
```
```python
python3 load_data.py
```
*load_data.py* supports reading the .csv files and loading into the specific 
database based on the database design of *schema.sql*.

The enumeration data type generated from the allowable values of official 
document file instructions, supported by *enumeration.py*.


## V. Run
```python
python3 application.py
```
*application.py* supports the user interface by command line and pass the parameters
to *database.py*. It provides multiple-level menu selection and dynamic 
query functions, which delivers the real-time query result as the next step
user options and enables user to add/remove query conditions arbitrarily.

*database.py* bridges the database and python execution. It generates the sql syntax 
based on the use input arguments.

### VI. Data Exploration
This database system supports multiple types and multiple levels queries at the same time. 
At the main menu list, it allows users to access 5 categories,
1. General Insurance Plan Search
2. State Average Individual Rate Search
3. Eye Plan Search
4. Plan Benefits Search
5. Tobacco User Friendly Plan Search

As for each category search results, this system provides general information of plan at first
and enables users to choose a specific plan from results and display more detailed information.

Through the query condition setup process, users can add and remove the conditions as wish and 
the total number of results at each step will be also displayed at the menu list for user reference.

## VII. Functions
- [x] SQL and NON-SQL Database
- [x] Dynamic and Real-Time Query
- [x] Automatic Data Loading and Supporting the Long-tern Reuse
- [x] Page Turning
- [x] Avoiding SQL-injection Vulnerabilities

### VIII. Acknowledgment
> Professor Samuel B. Johnson\
> Coffee :)

