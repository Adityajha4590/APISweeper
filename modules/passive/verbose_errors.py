#import necessary libraries

import requests
import re
from core.base import BaseScanner


"""
    ======================================================================
    APISweeper Passive Verbose Errors Scanner Module
    ======================================================================
"""


#class to scan for verbose error information in HTTP 500 responses
class VerboseErrorsScanner(BaseScanner):

    #define common verbose error patterns and their severity levels
    ERROR_PATTERNS = {

        "Python Stack Trace": {
            "patterns": [
                r"Traceback \(most recent call last\)",
                r'File ".*", line \d+',
                r"AttributeError",
                r"KeyError",
                r"TypeError",
                r"ValueError"
            ],
            "severity": "HIGH",
            "description": "HTTP 500 response exposes Python traceback or exception details."
        },

        "Java Stack Trace": {
            "patterns": [
                r"java\.lang\.",
                r"java\.util\.",
                r"java\.sql\.SQLException",
                r"Exception in thread",
                r"NullPointerException",
                r"IllegalArgumentException"
            ],
            "severity": "HIGH",
            "description": "HTTP 500 response exposes Java exception or stack trace details."
        },

        "SQL Error": {
            "patterns": [
                r"SQL syntax",
                r"You have an error in your SQL syntax",
                r"MySQL",
                r"PostgreSQL",
                r"sqlite3\.OperationalError",
                r"ORA-\d+",
                r"SQLException"
            ],
            "severity": "HIGH",
            "description": "HTTP 500 response exposes SQL or database error details."
        }
    }


    #defining scan function to check for verbose errors
    def scan(self) -> None:
        try:

            #make a GET request to the target URL
            response = requests.get(
                self.target_url,
                timeout=10
            )

            #only check HTTP 500 responses
            if response.status_code == 500:

                #get the response body as text
                response_text = response.text

                #check each error type
                for error_type, details in self.ERROR_PATTERNS.items():

                    #check each pattern associated with the error type
                    for pattern in details["patterns"]:

                        #search for the pattern in the response body
                        if re.search(
                            pattern,
                            response_text,
                            re.IGNORECASE
                        ):

                            #add finding when a verbose error is detected
                            self.add_finding(
                                severity=details["severity"],
                                endpoint=self.target_url,
                                description=details["description"]
                            )

                            #avoid duplicate findings for the same error type
                            break

        #handle any request exceptions
        except requests.RequestException as error:
            print(f"Error scanning {self.target_url}: {error}")