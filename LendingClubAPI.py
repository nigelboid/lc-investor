#
# Import all necessary libraries
#

import requests


#
# Define some global constants
#

# API request building blocks
API_VERSION= 'v1'
REQUEST_ROOT= 'https://api.lendingclub.com/api/investor/{}/'.format(API_VERSION)
REQUEST_LOANS= 'loans/listing?showAll=true'
REQUEST_ACCOUNTS= 'accounts/{}/'
REQUEST_SUMMARY= 'summary'
REQUEST_NOTES= 'detailednotes'
REQUEST_PORTFOLIOS= 'portfolios'
REQUEST_HEADER= 'Authorization'
REQUEST_ORDERS= 'orders'

KEY_AID= 'aid'
KEY_LOAN_ID= 'loanId'
KEY_REQUESTED_AMOUNT= 'requestedAmount'
KEY_ORDERS= 'orders'
KEY_PORTFOLIO_NAME= 'portfolioName'
KEY_PORTFOLIO_DESCRIPTION= 'portfolioDescription'
KEY_PORTFOLIO_ID= 'portfolioId'
KEY_ERRORS= 'errors'
KEY_LOANS= 'loans'
KEY_NOTES= 'myNotes'
KEY_PORTFOLIOS= 'myPortfolios'


# API request result codes
STATUS_CODE_OK= 200


#
# Define our Lending Club API class
#
class LCRequest:

  # Constructor
  def __init__(self, arguments):
    self.token= arguments.token
    self.id= arguments.id
    self.debug= arguments.debug

    self.requestHeader= {REQUEST_HEADER: self.token}
    self.requestLoans= REQUEST_ROOT + REQUEST_LOANS
    self.requestAccounts= REQUEST_ROOT + REQUEST_ACCOUNTS.format(self.id)


  # Obtain available cash amount
  def get_account_summary(self):
    request= self.requestAccounts + REQUEST_SUMMARY
    result= requests.get(request, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      return result.json()
    else:
      if self.debug:
        raise Exception('Could not obtain account summary (status code {})'.format(result.status_code), self, request, self.requestHeader)
      else:
        raise Exception('Could not obtain account summary (status code {})'.format(result.status_code))


  # Obtain all available notes ("In Funding")
  def get_available_notes(self):
    request= self.requestLoans
    result= requests.get(request, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      if KEY_LOANS in result.json():
        return result.json()[KEY_LOANS]
      else:
        if self.debug:
          raise Exception('Received an empty response for available loans (result object {})'.format(result.json()), self, request, self.requestHeader)
        else:
          raise Exception('Received an empty response for available loans')
    else:
      if self.debug:
        raise Exception('Could not obtain a list of available loans (status code {})'.format(result.status_code), self, request, self.requestHeader)
      else:
        raise Exception('Could not obtain a list of available loans (status code {})'.format(result.status_code))


  # Obtain a list of all notes owned
  def get_owned_notes(self):
    request= self.requestAccounts + REQUEST_NOTES
    result= requests.get(request, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      return result.json()[KEY_NOTES]
    else:
      if self.debug:
        raise Exception('Could not obtain a list of owned notes (status code {})'.format(result.status_code), self, request, self.requestHeader)
      else:
        raise Exception('Could not obtain a list of owned notes (status code {})'.format(result.status_code))


  # Obtain a list of all portfolios owned
  def get_owned_portfolios(self):
    request= self.requestAccounts + REQUEST_PORTFOLIOS
    result= requests.get(request, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      return result.json()[KEY_PORTFOLIOS]
    else:
      if self.debug:
        raise Exception('Could not obtain a list of owned portfolios (status code {})'.format(result.status_code), self, request, self.requestHeader)
      else:
        raise Exception('Could not obtain a list of owned portfolios (status code {})'.format(result.status_code))


  # Create named portfolio
  def create_portfolio(self, name, description):
    request= self.requestAccounts + REQUEST_PORTFOLIOS
    payload= {KEY_AID:self.id, KEY_PORTFOLIO_NAME:name, KEY_PORTFOLIO_DESCRIPTION:description}
    result= requests.post(request, json=payload, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      return result.json()
    else:
      if self.debug:
        raise Exception('Could not create the portfolio named "{}" with description "{}" (status code {})'.format(name, description, result.status_code), self, request, self.requestHeader, result.json()[KEY_ERRORS])
      else:
        raise Exception('Could not create the portfolio named "{}" with description "{}" (status code {})'.format(name, description, result.status_code)[KEY_ERRORS])


  # Submit buy order
  def submit_order(self, notes):
    request= self.requestAccounts + REQUEST_ORDERS
    payload= {KEY_AID:self.id, KEY_ORDERS:notes}
    result= requests.post(request, json=payload, headers=self.requestHeader)

    if result.status_code == STATUS_CODE_OK:
      return result.json()
    else:
      if self.debug:
        raise Exception('Order failed (status code {})'.format(result.status_code), self, request, self.requestHeader, result.json())
      else:
        raise Exception('Order failed (status code {})'.format(result.status_code))
