#!/usr/bin/env python


#
# Import all necessary libraries
#

import argparse
from lcrequest import LCRequest
from operator import itemgetter


#
# Define some global constants
#

VERSION= '1.2.2'
MINIMUM_INVESTMENT_AMOUNT= 25
MINIMUM_EMPLOYMENT_MONTHS= 12
MINIMUM_DELINQUENCY_MONTHS= 12
MINIMUM_RECORD_MONTHS= 36
MINIMUM_DEROGATORY_MONTHS= 36
MAXIMUM_DTI= 40
MAXIMUM_UTILIZATION= 75
GRADES= map(chr, range(ord('A'), ord('G')+1))
PORTFOLIO_DESCRIPTION= 'Automatically created'

KEY_CASH= 'cash'
KEY_INVESTED_LOANS= 'investedLoans'
KEY_SHOPPING_LIST= 'shoppingList'


# Lending Club API data structure keys
KEY_AVAILABLE_CASH= 'availableCash'
KEY_ACCOUNT_TOTAL= 'accountTotal'
KEY_LOANS= 'loans'
KEY_NOTES= 'myNotes'
KEY_GRADE= 'grade'
KEY_RATE= 'intRate'
KEY_PRINCIPAL= 'principalPending'
KEY_ID= 'id'
KEY_PURPOSE= 'purpose'
KEY_EMPLOYMENT= 'empLength'
KEY_DTI= 'dti'
KEY_DTI_JOINT= 'dtiJoint'
KEY_CREDIT_UTILIZATION= 'bcUtil'
KEY_COLLECTIONS= 'collections12MthsExMed'
KEY_SINCE_LAST_DELINQUENCY= 'mthsSinceLastDelinq'
KEY_SINCE_LAST_RECORD= 'mthsSinceLastRecord'
KEY_SINCE_LAST_DEROGATORY= 'mthsSinceLastMajorDerog'
KEY_TAX_LIEN= 'taxLiens'
KEY_HOME= 'homeOwnership'
KEY_LOAN_AMOUNT= 'loanAmount'
KEY_FUNDED_AMOUNT= 'fundedAmount'

KEY_PORTFOLIO_ID= 'portfolioId'
KEY_PORTFOLIO_NAME= 'portfolioName'
KEY_PORTFOLIO_DESCRIPTION= 'portfolioDescription'
KEY_PORTFOLIOS= 'myPortfolios'

KEY_AID= 'aid'
KEY_LOAN_ID= 'loanId'
KEY_REQUESTED_AMOUNT= 'requestedAmount'
KEY_INVESTED_AMOUNT= 'investedAmount'
KEY_ORDER_ID= 'orderInstructId'
KEY_CONFIRMATIONS= 'orderConfirmations'
KEY_EXECUTIONS_STATUS= 'executionStatus'

ACCEPTABLE_HOME= ['RENT', 'OWN', 'MORTGAGE']
ACCEPTABLE_PURPOSES= ['debt_consolidation', 'home_improvement', 'small_business', 'house', 'car', 'major_purchase', 'credit_card']


#
# Define our functions
#

# Collect all expected and detected arguments from the command line
#
def GetArguments():
  argumentParser= argparse.ArgumentParser()

  argumentParser.add_argument('-t', '--token', '--authorization-token', nargs=1, dest='token', required=True, action='store', help='Lending Club individual API authorization token')
  argumentParser.add_argument('-i', '--id', '--investor-id', nargs=1, dest='id', required=True, action='store', help='Lending Club individual account number')
  argumentParser.add_argument('-p', '--portfolio', nargs=1, dest='portfolio', required=False, action='store', help='Lending Club destination portfolio for bought notes')

  argumentParser.add_argument('-g', '--grade', nargs=2, metavar=('GRADE', 'PERCENT'), dest='grades', required=False, action='append', help='Specify percent allocation for a major note grade')
  argumentParser.add_argument('--minimum-amount-per-note', nargs=1, dest='min', type=int, required=False, action='store', default=[MINIMUM_INVESTMENT_AMOUNT], help='Smallest amount to invest per note')
  argumentParser.add_argument('--maximum-amount-per-note', nargs=1, dest='max', type=int, required=False, action='store', default=[MINIMUM_INVESTMENT_AMOUNT], help='Largest amount to invest per note')
  argumentParser.add_argument('--employment-months', nargs=1, dest='minEmploymentMonths', type=int, required=False, action='store', default=[MINIMUM_EMPLOYMENT_MONTHS], help='Minimum acceptable current employment length (in whole months)')
  argumentParser.add_argument('--dti', nargs=1, dest='maxDTI', type=int, required=False, action='store', default=[MAXIMUM_DTI], help='Maximum acceptable debt-to-income ratio')
  argumentParser.add_argument('--utilization', nargs=1, dest='maxUtilization', type=int, required=False, action='store', default=[MAXIMUM_UTILIZATION], help='Maximum acceptable credit utilization')
  argumentParser.add_argument('--delinquency-months', nargs=1, dest='minDelinquencyMonths', type=int, required=False, action='store', default=[MINIMUM_DELINQUENCY_MONTHS], help='Minimum acceptable time since last delinquency (in whole months)')
  argumentParser.add_argument('--record-months', nargs=1, dest='minRecordMonths', type=int, required=False, action='store', default=[MINIMUM_RECORD_MONTHS], help='Minimum acceptable time since last public record (in whole months)')
  argumentParser.add_argument('--derogatory-months', nargs=1, dest='minDerogatoryMonths', type=int, required=False, action='store', default=[MINIMUM_DEROGATORY_MONTHS], help='Minimum acceptable time since last major derogatory (in whole months)')

  argumentParser.add_argument('--chase-yield', dest='chaseYield', required=False, action='store_true', default=False, help='Prefer higher yielding notes within a grade')
  argumentParser.add_argument('--eat-cash', dest='eatCash', required=False, action='store_true', default=False, help='Aggressively attempt to overbuy to use up any and all cash')

  argumentParser.add_argument('-n', '--simulation', dest='simulation', required=False, action='store_true', default=False, help='Take no action -- only report decisions')
  argumentParser.add_argument('-q', '--quiet', dest='quiet', required=False, action='store_true', default=False, help='Suppress non-critical messages')
  argumentParser.add_argument('-d', '--debug', dest='debug', required=False, action='store_true', default=False, help='Turn on verbose diagnostics')

  argumentParser.add_argument('-v', '--version', action='version', version='%(prog)s '+VERSION)

  return argumentParser.parse_args()


# Validate and normalize some of the obtained arguments and pass the rest along
#
def NormalizeArguments(options):
  allocations= {}
  allocated= 0

  if options.debug and options.quiet:
    # cannot have it both ways -- debug trumps quiet
    options.quiet= False

  # convert lists of single values into integer values
  options.min= int(options.min.pop())
  options.max= int(options.max.pop())
  options.minEmploymentMonths= int(options.minEmploymentMonths.pop())
  options.maxDTI= int(options.maxDTI.pop())
  options.maxUtilization= int(options.maxUtilization.pop())
  options.minDelinquencyMonths= int(options.minDelinquencyMonths.pop())
  options.minDerogatoryMonths= int(options.minDerogatoryMonths.pop())
  options.minRecordMonths= int(options.minRecordMonths.pop())

  # convert lists of single strings into strings
  options.id= str(options.id.pop())
  options.token= str(options.token.pop())
  if options.portfolio <> None:
    options.portfolio= str(options.portfolio.pop())

  for grade in GRADES:
    # initialize our aggregator array
    allocations[grade]= 0

  if options.grades <> None:
    for specification in options.grades:
      # figure out our target allocations by note grade
      grade= specification[0][0].upper()
      if grade in GRADES:
        if specification[1].isdigit():
          allocations[grade]+= float(specification[1]) / 100
          allocated+= int(specification[1])
        elif options.debug:
          print('\n*** Ignoring percent specification <{}> for grade {} as it is not an integer value\n'.format(specification[1], grade))
      elif options.debug:
        print('\n*** Ignoring grade specification "{}" as it is not an expected major grade label [A-G]\n'.format(specification[0]))

  if allocated > 100:
    # over-allocated!
    if options.debug:
      raise Exception("Specified allocations exceed 100% ({:.0f}% allocated)!".format(allocated), allocations)
    else:
      raise Exception("Specified allocations exceed 100%!")

  options.allocations= allocations
  return options


# Assess current account state and identify what to buy
#
def AssessAccount(options, request):

  # check our account
  summary= request.get_account_summary()
  cash= summary[KEY_AVAILABLE_CASH]
  total= summary[KEY_ACCOUNT_TOTAL]
  investedLoans= []
  shoppingList= {}

  if cash >= options.min:
    # we seem to have enough for at least one note
    # let's figure out allocations
    ownedNotes= request.get_owned_notes()
    principal= {}
    count= {}

    if not options.quiet:
      print()
      print(' Cash balance: ${:12,.2f}'.format(cash))
      print('Account total: ${:12,.2f}\n'.format(total))
      print('My notes: {:,}'.format(len(ownedNotes)))

    for grade in GRADES:
      # initialize our aggregator arrays
      principal[grade]= 0
      count[grade]= 0
      shoppingList[grade]= 0

    for note in ownedNotes:
      # calculate principal and count of notes for each major grade
      grade= note[KEY_GRADE][0]
      investedLoans.append(note[KEY_LOAN_ID])
      count[grade]+= 1
      principal[grade]+= note[KEY_PRINCIPAL]

    for grade in GRADES:
      # figure out which grades remain below target allocation and allocate buys
      invested= principal[grade]/total
      if invested < options.allocations[grade]:
        shoppingList[grade]= int((total * (options.allocations[grade] - invested)) / options.min)
        if options.eatCash:
          # aggressively attempt to overbuy to use up any and all cash
          shoppingList[grade]+= 1
        countLabel= str(shoppingList[grade])

      if shoppingList[grade] == 0:
        # prune this shopping list entry since we won't be buying notes of this grade
        del shoppingList[grade]

      if not options.quiet:
        if grade not in shoppingList:
          countLabel= 'no'
          plurality= 's'
        elif shoppingList[grade] == 1:
          countLabel= str(shoppingList[grade])
          plurality= ' '
        else:
          countLabel= str(shoppingList[grade])
          plurality= 's'

        print('\t{:5d} grade {} notes with principal value ${:12,.2f} ({:6,.2%} / {:4,.0%}) [{:>4} unit{} to buy]'.format(count[grade], grade, principal[grade], invested, options.allocations[grade], countLabel, plurality))

    if options.portfolio <> None:
      # check if our target portfolio exists and create it if not
      # lastly, replace the portfolio name with its ID, for future reference
      portfolios= request.get_owned_portfolios()
      matchedPortfolio= [portfolio[KEY_PORTFOLIO_ID] for portfolio in portfolios if
      (
        portfolio[KEY_PORTFOLIO_NAME] == options.portfolio
      )
      ]
      if len(matchedPortfolio) > 0:
        if options.debug:
          print('\nFound existing target portfolio "{}" with ID "{}"'.format(options.portfolio, matchedPortfolio[0]))
        options.portfolio= matchedPortfolio[0]
      else:
        if options.simulation:
          print('\nSpecified target portfolio "{}" does not exist:'.format(options.portfolio))
          print('\twould have tried to create a portfolio named "{}"\n\tand description "{}"\n\tif this was not a simulated run'.format(options.portfolio, PORTFOLIO_DESCRIPTION))
          options.portfolio= '123456'
        else:
          response= request.create_portfolio(options.portfolio, PORTFOLIO_DESCRIPTION)
          if not options.quiet:
            print('\nSpecified target portfolio "{}" does not exist:'.format(options.portfolio))
            print('\tcreated target portfolio named "{}"\n\twith ID "{}"\n\tand description "{}"'.format(response[KEY_PORTFOLIO_NAME], response[KEY_PORTFOLIO_ID], response[KEY_PORTFOLIO_DESCRIPTION]))
            options.portfolio= response[KEY_PORTFOLIO_ID]

  else:
    # we don't have enough cash to proceed
    if options.debug:
      print('\nNot enough cash to proceed (${:,.2f} available)'.format(cash))

  return {KEY_CASH: cash, KEY_INVESTED_LOANS: investedLoans, KEY_SHOPPING_LIST: shoppingList}



# Find and buy notes to meet desired allocation targets
#
def BuyNotes(options, request, account):
  # compose our order and submit it
  result= SubmitOrder(options, request, ComposeOrder(options, request, account))

  return result



# Compose a buy order for desired notes
#
def ComposeOrder(options, request, account):
  # prioritize orders by rate or by deficit (i.e., most wanted)
  notesAvailable= request.get_available_notes()
  shoppingList= account[KEY_SHOPPING_LIST]
  if options.chaseYield:
    # sort the shopping list by highest grade, in descending order
    # also, sort filtered available loans by highest rate, in descending order
    shoppingOrder= sorted(shoppingList, reverse=True)
    notesDesired= sorted(FilterNotesByPreference(options, account[KEY_INVESTED_LOANS], notesAvailable, shoppingOrder), key=itemgetter(KEY_RATE), reverse=True)
  else:
    # sort the shopping list by highest relative deficit (i.e., most notes to buy), in descending order
    # also, just filter available loans preserving their original order
    shoppingOrder= sorted(shoppingList, key=shoppingList.get, reverse=True)
    notesDesired= FilterNotesByPreference(options, account[KEY_INVESTED_LOANS], notesAvailable, shoppingOrder)

  # collect our orders
  cash= account[KEY_CASH]
  orders= {}
  for grade in shoppingOrder:
    # attempt to find and purchase notes for each grade in our shopping list
    if not options.quiet:
      print()
      print('Allocating available cash to grade {} notes:'.format(grade))

    notes= FilterNotesByGrade(notesDesired, grade)
    if not options.quiet:
      if len(notes) > 0:
        units= int(min(cash/options.min, shoppingList[grade]))
        print('\tfound {:,} suitable grade {} note{} out of {:,} unfunded notes currently available'.format(len(notes), grade, PluralS(len(notes)), len(notesAvailable)))
        if cash < options.min:
          print('\tbut cash available (${:,.2f}) remains below the cost of a single note'.format(cash))
        else:
          print('\twill attempt to purchase up to {:,} unit{} with ${:,.2f} cash available'.format(units, PluralS(units), cash))
      else:
        print('\tfound no suitable grade {} notes out of {:,} unfunded notes currently available'.format(grade, len(notesAvailable)))

    # collect candidate notes and desired amounts
    count= 0
    spent= 0
    unfunded= {}

    for note in notes:
      # first pass allocation
      if (note[KEY_LOAN_AMOUNT] - note[KEY_FUNDED_AMOUNT]) >= options.min and (spent + options.min) <= cash:
        orders[note[KEY_ID]]= options.min
        unfunded[note[KEY_ID]]= note[KEY_LOAN_AMOUNT] - note[KEY_FUNDED_AMOUNT] - options.min
        count+= 1
        spent+= options.min
        if not options.quiet:
          print('\tallocated ${:3.2f} to note {} (${:,.2f} remaining)'.format(options.min, note[KEY_ID], cash-spent))
        if (spent + options.min) > cash or count == shoppingList[grade]:
          # ran out of money!
          break

    while (spent + options.min) <= cash and count < shoppingList[grade] and len(unfunded) > 0:
      # raise allocations for currently funded notes
      unfundedIDs= unfunded.keys()
      for id in unfundedIDs:
        if unfunded[id] >= options.min and (orders[id] + options.min) <= options.max:
          orders[id]+= options.min
          unfunded[id]-= options.min
          count+= 1
          spent+= options.min
          if not options.quiet:
            print('\tallocated ${:.2f} more to note {} (${:,.2f} remaining)'.format(options.min, id, cash-spent))
          if (spent + options.min) > cash or count == shoppingList[grade]:
            # ran out of money!
            break
        else:
          del unfunded[id]

    if options.debug:
      if count < shoppingList[grade]:
        if cash > spent and cash > options.min:
          print('\tfailed to find enough unfunded matching notes to allocate planned funds ({} note{} short)'.format(shoppingList[grade]-count, PluralS(shoppingList[grade]-count)))
        else:
          print('\tfailed to fund all desired unfunded notes due to insufficient available cash ({} note{} short)'.format(shoppingList[grade]-count, PluralS(shoppingList[grade]-count)))

    cash-= spent

  # itemize our buy order
  if options.debug:
      print()
      print('Composing order:')

  buyList= []
  if len(orders) > 0:
    for id in orders:
      if options.portfolio <> None:
        buyList.append({KEY_LOAN_ID:id, KEY_REQUESTED_AMOUNT:orders[id], KEY_PORTFOLIO_ID:options.portfolio})
      else:
        buyList.append({KEY_LOAN_ID:id, KEY_REQUESTED_AMOUNT:orders[id]})
      if options.debug:
        print('\twill attempt to order ${:,.2f} worth of note {}'.format(orders[id], id))
  else:
    if options.debug:
      print('\tnothing to order')

  return buyList


# Filter offered notes by grade
#
def FilterNotesByGrade(notes, grade):
  notesDesired= [note for note in notes if
  (
    note[KEY_GRADE] == grade
  )
  ]
  return notesDesired


# Filter offered notes by various preferred criteria
#
def FilterNotesByPreference(options, ownedLoans, notes, desiredGrades):
  notesDesired= [note for note in notes if
  (
    note[KEY_ID] not in ownedLoans
    and note[KEY_GRADE] in desiredGrades
    and note[KEY_PURPOSE] in ACCEPTABLE_PURPOSES
    and note[KEY_HOME] in ACCEPTABLE_HOME
    and note[KEY_EMPLOYMENT] >= options.minEmploymentMonths
    and note[KEY_DTI] <= options.maxDTI
    and note[KEY_DTI_JOINT] <= options.maxDTI
    and note[KEY_CREDIT_UTILIZATION] <= options.maxUtilization
    and note[KEY_COLLECTIONS] == 0
    and note[KEY_TAX_LIEN] == 0
    and (note[KEY_SINCE_LAST_DELINQUENCY] == None or note[KEY_SINCE_LAST_DELINQUENCY] >= options.minDelinquencyMonths)
    and (note[KEY_SINCE_LAST_RECORD] == None or note[KEY_SINCE_LAST_RECORD] >= options.minRecordMonths)
    and (note[KEY_SINCE_LAST_DEROGATORY] == None or note[KEY_SINCE_LAST_DEROGATORY] >= options.minDerogatoryMonths)
  )
  ]
  return notesDesired


# Submit our order
#
def SubmitOrder(options, request, buyList):
  response= {}

  if options.debug:
    print('\nSubmitting order:')

  if len(buyList) > 0 or options.debug:
    if options.simulation:
      print('\nSubmitting order:')
      print('\twould have tried to submit the order if this was not a simulated run')
    else:
      response= request.submit_order(buyList)
      if len(buyList) > 0:
        if options.debug:
          print('\tsubmitted order')
      else:
        print('\tsubmitted empty order')

  return response


# Compose an activity report
#
def Report(options, response):
  if not options.quiet:
    print()
    print('Order execution report:')
    if len(response) > 0:
      if response[KEY_ORDER_ID] <> None:
        print('\tOrder ID {}'.format(response[KEY_ORDER_ID]))
        for orderConfirmation in response[KEY_CONFIRMATIONS]:
          # report results of each note order
          print('\tLoan ID {} invested ${:6,.2f} of ${:6,.2f} requested (codes: {})'.format(orderConfirmation[KEY_LOAN_ID], orderConfirmation[KEY_INVESTED_AMOUNT], orderConfirmation[KEY_REQUESTED_AMOUNT], ' '.join(orderConfirmation[KEY_EXECUTIONS_STATUS])))
      else:
        print('\tnothing happened (order ID "{}")'.format(response[KEY_ORDER_ID]))
    else:
      print('\tno order submitted')

  return True


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

    # figure out what we want
    account= AssessAccount(options, request)

    if len(account[KEY_SHOPPING_LIST]) > 0 or options.debug:
      # attempt to buy notes or just go through the motions for the sake of debugging
      # deliver a report on the outcome
      Report(options, BuyNotes(options, request, account))

  except Exception as error:
    print(type(error))
    print(error.args[0])
    for counter in range(1, len(error.args)):
      print('\t' + str(error.args[counter]))

  else:
    if options.debug:
      print()
      print('All done!')


#
# Execute if we were run as a program
#

if __name__ == '__main__':
  main()
