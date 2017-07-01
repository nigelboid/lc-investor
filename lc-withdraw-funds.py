#!/usr/bin/env python


#
# Import all necessary libraries
#

import argparse
from LendingClubAPI import LCRequest
from operator import itemgetter


#
# Define some global constants
#

VERSION= '0.0.1'
MINIMUM_WITHDRAWAL_AMOUNT= 100
MAXIMUM_WITHDRAWAL_AMOUNT= 1000

# Lending Club API data structure keys
KEY_AVAILABLE_CASH= 'availableCash'
KEY_AMOUNT= 'amount'
KEY_TRANSFER_DATE= 'estimatedFundsTransferDate'


#
# Define our functions
#

# Collect all expected and detected arguments from the command line
#
def GetArguments():
  argumentParser= argparse.ArgumentParser()

  argumentParser.add_argument('-t', '--token', '--authorization-token', nargs=1, dest='token', required=True, action='store', help='Lending Club individual API authorization token')
  argumentParser.add_argument('-i', '--id', '--investor-id', nargs=1, dest='id', required=True, action='store', help='Lending Club individual account number')

  argumentParser.add_argument('--minimum-amount', nargs=1, dest='min', type=int, required=False, action='store', default=[MINIMUM_WITHDRAWAL_AMOUNT], help='Smallest amount to withdraw')
  argumentParser.add_argument('--maximum-amount', nargs=1, dest='max', type=int, required=False, action='store', default=[MAXIMUM_WITHDRAWAL_AMOUNT], help='Largest amount to withdraw')



  argumentParser.add_argument('-n', '--simulation', dest='simulation', required=False, action='store_true', default=False, help='Take no action -- only report decisions')
  argumentParser.add_argument('-q', '--quiet', dest='quiet', required=False, action='store_true', default=False, help='Suppress non-critical messages')
  argumentParser.add_argument('-d', '--debug', dest='debug', required=False, action='store_true', default=False, help='Turn on verbose diagnostics')

  argumentParser.add_argument('-v', '--version', action='version', version='%(prog)s '+VERSION)

  return argumentParser.parse_args()


# Validate and normalize some of the obtained arguments and pass the rest along
#
def NormalizeArguments(options):
  if options.debug and options.quiet:
    # cannot have it both ways -- debug trumps quiet
    options.quiet= False

  # convert lists of single values into integer values
  options.min= int(options.min.pop())
  options.max= int(options.max.pop())

  # convert lists of single strings into strings
  options.id= str(options.id.pop())
  options.token= str(options.token.pop())

  return options


# Assess current account state and submit a withdrawal request if there is enough cash
#
def Withdraw(options, request):
  response= {}

  # check our account
  summary= request.get_account_summary()
  cash= summary[KEY_AVAILABLE_CASH]

  if cash >= options.min:
    # we seem to have enough to withdraw
    # (or just go through the motions for the sake of debugging)

    if not options.quiet:
      print
      print '      Cash balance: ${:12,.2f}'.format(cash)

    if cash <= options.max:
      amount= cash
    else:
      amount= options.max

    if not options.quiet:
      print ' Withdrawal amount: ${:12,.2f}'.format(amount)

    response= request.submit_withdrawal(amount)

    if not options.quiet:
      print
      if len(response) > 0:
        print 'Request to withdraw ${:6,.2f} set for {}'.format(response[KEY_AMOUNT], response[KEY_TRANSFER_DATE])
      else:
        print '\tno request submitted'

  else:
    # we don't have enough cash to proceed
    if options.debug:
      print '\nNot enough cash to proceed (${:,.2f} available)'.format(cash)

  return cash


# Should there be an 's' at the end?
#
def PluralS(number):
  if int(number) == 1:
    return ''
  else:
    return 's'


# Main entry point
#
def main():
  try:
    # instantiate our Lending Club API and initialize from command line arguments
    options= NormalizeArguments(GetArguments())
    request= LCRequest(options)

    # figure out what we have
    cash= Withdraw(options, request)

  except Exception as error:
    print type(error)
    print error.args[0]
    for counter in xrange(1, len(error.args)):
      print '\t' + str(error.args[counter])

  else:
    if options.debug:
      print
      print 'All done!'


#
# Execute if we were run as a program
#

if __name__ == '__main__':
  main()
