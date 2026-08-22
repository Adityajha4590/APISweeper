from abc import ABC, abstractmethod

class BaseScanner(ABC):
    """
    ======================================================================
    APISweeper Core Module Blueprint (The 'Contract')
    ======================================================================
    
    ATTENTION TEAM:
    Every single scanning module you write (Passive, Active, or Logic)
    MUST inherit from this `BaseScanner` class. 
    
    Why?
    By inheriting from this class, we guarantee that all our modules 
    have the exact same structure. This allows the CLI (`scanner.py`) 
    and the Web UI (`ui.py`) to run all of your checks dynamically 
    without needing to know how each specific check works internally.
    """
    
    def __init__(self, target_url: str, token: str = None):
        """
        Initialize the scanner with the target API details.
        
        Args:
            target_url (str): The base URL to scan (e.g., "http://localhost:5000/api/v1").
            token (str, optional): A JWT or Bearer token for authenticated scans.
        """
        self.target_url = target_url
        self.token = token
        
        # This list will store all vulnerabilities found by your specific module.
        # DO NOT modify this list directly! Use `self.add_finding()` instead.
        self.results = []

    @abstractmethod
    def scan(self) -> None:
        """
        ==================================================================
        MANDATORY METHOD TO IMPLEMENT
        ==================================================================
        Every module you create MUST have a `scan()` method. 
        This is where you write your actual attacking/scanning logic using 
        the `requests` library.
        
        If you find a vulnerability during your logic here, you must report 
        it by calling `self.add_finding(...)`.
        """
        pass

    def add_finding(self, severity: str, endpoint: str, description: str) -> None:
        """
        Standardized way to report a vulnerability finding.
        
        Args:
            severity (str): Must be exactly one of: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'.
            endpoint (str): The specific path affected (e.g., '/api/v1/users/2').
            description (str): A detailed explanation of what you found and why it's bad.
        """
        # We enforce uppercase severity so our reports always look clean and consistent.
        valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        severity_upper = severity.upper()
        
        if severity_upper not in valid_severities:
            raise ValueError(f"Invalid severity '{severity}'. Must be one of {valid_severities}.")
            
        self.results.append({
            "severity": severity_upper,
            "endpoint": endpoint,
            "description": description
        })
        
    def get_results(self) -> list:
        """
        Returns the list of findings. 
        The CLI and UI use this to grab your results after calling `.scan()`.
        """
        return self.results
