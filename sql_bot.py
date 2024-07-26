from runpy import run_path
from sqlalchemy import create_engine
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import logging
from langchain.prompts import load_prompt
from pathlib import Path
import yaml

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")



genai.configure(api_key=api_key)

llm = ChatGoogleGenerativeAI(model="gemini-pro")



#response = llm.invoke("Sing a ballad of LangChain.")
##  logging.debug(f"Response: {response}")
   # print(response.content) 




from langchain_community.utilities import SQLDatabase

cs="mysql+mysqlconnector://root:12345678@localhost/classicmodels"
db_engine=create_engine(cs)
db=SQLDatabase(db_engine)

#database_uri = 'sqlite:///STUDENT.db'

#db = SQLDatabase.from_uri(database_uri)


#print(db.dialect)
print(db.get_usable_table_names())
#a=db.run("SELECT * FROM STUDENT_INFO LIMIT 10;")

#for row in a:
   # print(row,end="")
from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.prompts.prompt import PromptTemplate

#examples=[Show data of the employee names Loui
#{question:}

#]


#THIS TEMPLATED IF U WANT TO PASS THE SCHEMA OF THE TABLE

#template = '''
'''CREATE TABLE productlines (
  productLine varchar(50),
  textDescription varchar(4000) DEFAULT NULL,
  htmlDescription mediumtext,
  image mediumblob,
  PRIMARY KEY (productLine)
);

CREATE TABLE products (
  productCode varchar(15),
  productName varchar(70) NOT NULL,
  productLine varchar(50) NOT NULL,
  productScale varchar(10) NOT NULL,
  productVendor varchar(50) NOT NULL,
  productDescription text NOT NULL,
  quantityInStock smallint(6) NOT NULL,
  buyPrice decimal(10,2) NOT NULL,
  MSRP decimal(10,2) NOT NULL,
  PRIMARY KEY (productCode),
  FOREIGN KEY (productLine) REFERENCES productlines (productLine)
);

CREATE TABLE offices (
  officeCode varchar(10),
  city varchar(50) NOT NULL,
  phone varchar(50) NOT NULL,
  addressLine1 varchar(50) NOT NULL,
  addressLine2 varchar(50) DEFAULT NULL,
  state varchar(50) DEFAULT NULL,
  country varchar(50) NOT NULL,
  postalCode varchar(15) NOT NULL,
  territory varchar(10) NOT NULL,
  PRIMARY KEY (officeCode)
);

CREATE TABLE employees (
  employeeNumber int,
  lastName varchar(50) NOT NULL,
  firstName varchar(50) NOT NULL,
  extension varchar(10) NOT NULL,
  email varchar(100) NOT NULL,
  officeCode varchar(10) NOT NULL,
  reportsTo int DEFAULT NULL,
  jobTitle varchar(50) NOT NULL,
  PRIMARY KEY (employeeNumber),
  FOREIGN KEY (reportsTo) REFERENCES employees (employeeNumber),
  FOREIGN KEY (officeCode) REFERENCES offices (officeCode)
);

CREATE TABLE customers (
  customerNumber int,
  customerName varchar(50) NOT NULL,
  contactLastName varchar(50) NOT NULL,
  contactFirstName varchar(50) NOT NULL,
  phone varchar(50) NOT NULL,
  addressLine1 varchar(50) NOT NULL,
  addressLine2 varchar(50) DEFAULT NULL,
  city varchar(50) NOT NULL,
  state varchar(50) DEFAULT NULL,
  postalCode varchar(15) DEFAULT NULL,
  country varchar(50) NOT NULL,
  salesRepEmployeeNumber int DEFAULT NULL,
  creditLimit decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (customerNumber),
  FOREIGN KEY (salesRepEmployeeNumber) REFERENCES employees (employeeNumber)
);

CREATE TABLE payments (
  customerNumber int,
  checkNumber varchar(50) NOT NULL,
  paymentDate date NOT NULL,
  amount decimal(10,2) NOT NULL,
  PRIMARY KEY (customerNumber,checkNumber),
  FOREIGN KEY (customerNumber) REFERENCES customers (customerNumber)
);

CREATE TABLE orders (
  orderNumber int,
  orderDate date NOT NULL,
  requiredDate date NOT NULL,
  shippedDate date DEFAULT NULL,
  status varchar(15) NOT NULL,
  comments text,
  customerNumber int NOT NULL,
  PRIMARY KEY (orderNumber),
  FOREIGN KEY (customerNumber) REFERENCES customers (customerNumber)
);

CREATE TABLE orderdetails (
  orderNumber int,
  productCode varchar(15) NOT NULL,
  quantityOrdered int NOT NULL,
  priceEach decimal(10,2) NOT NULL,
  orderLineNumber smallint(6) NOT NULL,
  PRIMARY KEY (orderNumber,productCode),
  FOREIGN KEY (orderNumber) REFERENCES orders (orderNumber),
  FOREIGN KEY (productCode) REFERENCES products (productCode)
);'''


# THIS TEMPLATED IF U WANT THE BOT TO LEARN THE SCHEMA OF THE TABLE ON ITS OWN

template ='''
You are a MySQL expert. Your task is to describe a table in a MySQL database to learn its schema for a better understanding of the table structure.

Follow these steps:

1. Open your MySQL client (such as MySQL Workbench, the MySQL command line, or another SQL client).

2. Select the database that contains the table you want to describe. Use the `USE` statement to select the database:
   ```sql
   USE {database_name} and learn about the database and its table
3.then  apply the desc on all the tables in the database to get the schema of the table then learn the schema of all the tables.
The desc funtion is used to give schema of the table.
After leanring the schemas of the table show me all the schemas of all the tables
     
take a user question and respond back with a SQL query.
example:
user question: show data for the employee named Loui
your generated sql query: SELECT * FROM employees WHERE firstname= "Loui";

example: show me the customer name, order date, shipping dates, status of customer id 141
your generated answer: 
SELECT 
    customers.customerName,
    orders.orderDate,
    orders.shippedDate,
    orders.status
FROM 
    customers
INNER JOIN 
    orders 
ON 
    customers.customerNumber = orders.customerNumber
WHERE orders.customerNumber=141;

example: give me the name of the customers who have canceled their orders
your generated answer: 
SELECT 
    customers.customerName,
    orders.orderNumber,
    orders.shippedDate,
    orders.status
FROM 
    customers
INNER JOIN 
    orders 
ON 
    customers.customerNumber = orders.customerNumber
WHERE orders.status="cancelled";
do not include the word sql and show me the output without "" and ()

user question: {input}

---



'''

prompt = PromptTemplate(
    input_variables=["database_name,input"],
    template=template
   
)
 


















from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent

'''toolkit = SQLDatabaseToolkit(db=db,llm=ChatGoogleGenerativeAI(model="gemini-pro"))
context = toolkit.get_context()
tools = toolkit.get_tools()
db=db
agent=create_sql_agent(llm,  prompt=prompt,toolkit=toolkit,verbose=True)
agent.run(" give me the name of the customers who have canceled their orders")'''

prompt = PromptTemplate(
    input_variables=["input"],
    template=template
)


llm = ChatGoogleGenerativeAI(model="gemini-pro")



db_toolkit = SQLDatabaseToolkit(db=db,llm=llm)


sql_agent = create_sql_agent(llm=llm,toolkit=db_toolkit,verbose=True)


user_question = "show me the volvo customer details"
database='classicmodels'
formatted_prompt = template.format(input=user_question,database_name=database)

response = sql_agent.run(formatted_prompt)

print(response)



