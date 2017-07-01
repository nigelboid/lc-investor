#!/usr/bin/env python


#
# Import all necessary libraries
#

import argparse
from lcrequest import LCRequest


#
# Define some global constants
#

VERSION= '0.1.0'
GRADES= map(chr, range(ord('A'), ord('G')+1))

# Lending Club API data structure keys
KEY_COUNT= 'count'
KEY_TOTAL= 'total'

KEY_NOTES= 'myNotes'
KEY_GRADE= 'grade'

KEY_ACCOUNT_CASH= 'availableCash'
KEY_ACCOUNT_TOTAL= 'accountTotal'
KEY_IN_FUNDING= 'infundingBalance'
KEY_PRINCIPAL_RECEIVED= 'receivedPrincipal'
KEY_PRINCIPAL_OUTSTANDING= 'outstandingPrincipal'
KEY_INTEREST_RECEIVED= 'receivedInterest'
KEY_FEES_RECEIVED= 'receivedLateFees'
KEY_NOTES_COUNT= 'totalNotes'

KEY_NOTE_AMOUNT= 'noteAmount'
KEY_NOTE_PAYMENTS= 'paymentsReceived'
KEY_NOTE_PRINCIPAL_RETURNED= 'principalReceived'
KEY_NOTE_INTEREST_PAID= 'interestReceived'
KEY_NOTE_DATE= 'orderDate'
KEY_NOTE_STATUS= 'loanStatus'



#
# Define our functions
#

# Collect all expected and detected arguments from the command line
#
def GetArguments():
  argumentParser= argparse.ArgumentParser()

  argumentParser.add_argument('-t', '--token', '--authorization-token', nargs=1, dest='token', required=True, action='store', help='Lending Club individual API authorization token')
  argumentParser.add_argument('-i', '--id', '--investor-id', nargs=1, dest='id', required=True, action='store', help='Lending Club individual account number')

  argumentParser.add_argument('-d', '--debug', dest='debug', required=False, action='store_true', default=False, help='Turn on verbose diagnostics')

  argumentParser.add_argument('-v', '--version', action='version', version='%(prog)s '+VERSION)

  return argumentParser.parse_args()


# Validate and normalize some of the obtained arguments and pass the rest along
#
def NormalizeArguments(options):
  # convert lists of single strings into strings
  options.id= str(options.id.pop())
  options.token= str(options.token.pop())

  return options


# Grab and report current account summary
#
def GetSummary(options, request):
  # check our account
  summary= request.get_account_summary()

  print
  print 'Summary'
  print '---------------------------------'
  print '{:>18}: ${:12,.2f}'.format('Account total', summary[KEY_ACCOUNT_TOTAL])
  print '{:>18}: ${:12,.2f}'.format('Cash balance', summary[KEY_ACCOUNT_CASH])
  print '{:>18}: ${:12,.2f}'.format('Committed cash', summary[KEY_IN_FUNDING])
  print '{:>18}: ${:12,.2f}'.format('Current principal', summary[KEY_PRINCIPAL_OUTSTANDING])
  print '{:>18}: ${:12,.2f}'.format('Capital returned', summary[KEY_PRINCIPAL_RECEIVED])
  print '{:>18}: ${:12,.2f}'.format('Interest received', summary[KEY_INTEREST_RECEIVED])
  print '{:>18}: ${:12,.2f}'.format('Fees received', summary[KEY_FEES_RECEIVED])
  print
  print '{:>18}: {:13,}'.format('Notes owned', summary[KEY_NOTES_COUNT])

  return summary


# Compile detailed performance statistics per grade and report them
#
def GetPerformanceDetails(options, request):
  # check our notes
  notes= request.get_owned_notes()

  # compile performance summaries
  performance= {}
  statusCodes= {}
  for note in notes:
    # get details from each owned note
    if note[KEY_GRADE] in performance.keys():
      performance[note[KEY_GRADE]][KEY_COUNT]+= 1
      performance[note[KEY_GRADE]][KEY_NOTE_AMOUNT]+= note[KEY_NOTE_AMOUNT]
      performance[note[KEY_GRADE]][KEY_NOTE_PRINCIPAL_RETURNED]+= note[KEY_NOTE_PRINCIPAL_RETURNED]
      performance[note[KEY_GRADE]][KEY_NOTE_INTEREST_PAID]+= note[KEY_NOTE_INTEREST_PAID]
      performance[note[KEY_GRADE]][KEY_NOTE_PAYMENTS]+= note[KEY_NOTE_PAYMENTS]
    else:
      performance[note[KEY_GRADE]]= {KEY_COUNT: 1, KEY_NOTE_AMOUNT: note[KEY_NOTE_AMOUNT], KEY_NOTE_PRINCIPAL_RETURNED: note[KEY_NOTE_PRINCIPAL_RETURNED], KEY_NOTE_INTEREST_PAID: note[KEY_NOTE_INTEREST_PAID], KEY_NOTE_PAYMENTS: note[KEY_NOTE_PAYMENTS]}

    if note[KEY_NOTE_STATUS] in statusCodes.keys():
      statusCodes[note[KEY_NOTE_STATUS]]+= 1
    else:
      statusCodes[note[KEY_NOTE_STATUS]]= 1


  # set up accumulators
  count= {}
  invested= {}
  returned= {}
  interest= {}
  payments= {}
  count[KEY_TOTAL]= invested[KEY_TOTAL]= returned[KEY_TOTAL]= interest[KEY_TOTAL]= payments[KEY_TOTAL]= 0
  for grade in GRADES:
    count[grade]= invested[grade]= returned[grade]= interest[grade]= payments[grade]= 0

  # details header
  separator= '{:->81}'.format('')
  header= separator + '\n' + '{:>6} {:>6} {:>16} {:>16} {:>16} {:>16}'.format('grade', 'count', 'invested', 'returned', 'interest', 'payments') + '\n' + separator
  print
  print
  print 'Details'
  print header

  # details by minor grade
  for grade in sorted(performance):
    count[grade[0]]+= performance[grade][KEY_COUNT]
    invested[grade[0]]+= performance[grade][KEY_NOTE_AMOUNT]
    returned[grade[0]]+= performance[grade][KEY_NOTE_PRINCIPAL_RETURNED]
    interest[grade[0]]+= performance[grade][KEY_NOTE_INTEREST_PAID]
    payments[grade[0]]+= performance[grade][KEY_NOTE_PAYMENTS]

    print '{:>6} {:6d}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}'.format(grade, performance[grade][KEY_COUNT], performance[grade][KEY_NOTE_AMOUNT], performance[grade][KEY_NOTE_PRINCIPAL_RETURNED], performance[grade][KEY_NOTE_INTEREST_PAID], performance[grade][KEY_NOTE_PAYMENTS])


  # details by major grade
  print header
  for grade in GRADES:
    count[KEY_TOTAL]+= count[grade]
    invested[KEY_TOTAL]+= invested[grade]
    returned[KEY_TOTAL]+= returned[grade]
    interest[KEY_TOTAL]+= interest[grade]
    payments[KEY_TOTAL]+= payments[grade]
    print '{:>5}  {:6d}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}'.format(grade, count[grade], invested[grade], returned[grade], interest[grade], payments[grade])

  # details footer
  print separator
  print 'Totals:{:6d}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}     ${:11,.2f}'.format(count[KEY_TOTAL], invested[KEY_TOTAL], returned[KEY_TOTAL], interest[KEY_TOTAL], payments[KEY_TOTAL])
  print separator

  print
  print
  for status in statusCodes:
    print '{:6d} {}'.format(statusCodes[status], status)



  return performance


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

    # grab and report current account summary
    summary= GetSummary(options, request)

    # compile detailed performance statistics per grade and report them
    performance= GetPerformanceDetails(options, request)

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
