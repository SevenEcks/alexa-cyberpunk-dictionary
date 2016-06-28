## Installation and Configuration Instructions
Alexa Cyberpunk Dictionary Application written in Python using AWS Lambda

Step 1: Create a new Lambda using the color-skills python blueprint
Step 2: Use all the defaults
Step 3: Enter 'process_request' as the function name
Step 4: Enter a description like 'Cyberpunk Lambda Function for Amazon Alexa'
Step 5: Choose the 'lambda_basic_execution' role
Step 6: We are not resource heavy, make sure you use the minimum ram to keep costs low
Step 7: Our code should execute fast, thus our timeout should be a max of 3 seconds (or less)
Step 8: We shouldn't need a VPC for this
Step 9: Finish creating the function
Step 10: Zip the files in the base directory and upload them to the lambda
Step 11: In the configuration secdtion of your lambda function, change the handler to main.process_request (filename + function name)
Step 12: Open Developer Portal (https://developer.amazon.com/edw/home.html)
Step 13: Add a new Skill
Step 14: Add Intent from intent directory
Step 15: Add utterances from utterance directory
Step 16: Set ARN for the Lambda (find in the Lambda console in top left)
## Other Information
### Tests
A directory full of tests has been provided.  This allows you to test your skills intents from the Lambda Test console.  This is done by copying the test for the intent you are working with into the test console for your lambda function.

Writing tests may seem like a hassle at first but it is actually a very important part of development and will come in very handy when you 
want to do testing of your application.  As such, you should write a test for every new intent you create.
